from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
import httpx
import traceback
from contextlib import asynccontextmanager
# Import A2A client components and strands
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import MessageSendParams, SendStreamingMessageRequest
from strands import Agent, tool
from strands.agent.conversation_manager import SlidingWindowConversationManager
import nest_asyncio
import logging
import os
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
)

logger = logging.getLogger(__name__)


from dotenv import load_dotenv
load_dotenv()
from strands.models.openai import OpenAIModel

# MODEL = OpenAIModel(
#     client_args={
#         "api_key": os.environ.get("API_KEY"),
#         "base_url": "https://api.siliconflow.cn/v1",
#     },
#     model_id="Pro/deepseek-ai/DeepSeek-R1",
#     params={
#         "max_tokens": 28000,
#         "temperature": 0.7,
#     }
# )

# MODEL = "us.amazon.nova-pro-v1:0"
MODEL = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"



# Langfuse configuration
import base64
import os
public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
# Set up endpoint
otel_endpoint = str(os.environ.get("LANGFUSE_HOST")) + "/api/public/otel/v1/traces"
auth_token = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = otel_endpoint
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {auth_token}"

# Global variables
agent_registry: Dict[str, Dict[str, Any]] = {}
lead_agent_instance = None

# Pydantic models
class AgentInfo(BaseModel):
    id: str
    name: str
    description: str
    url: str
    skill_name: str
    skill_description: str
    skills: Optional[List[Dict[str, str]]] = None
    status: str
    enabled: bool

class AddAgentRequest(BaseModel):
    url: str

class DeleteAgentRequest(BaseModel):
    agent_id: str

class InvokeStreamRequest(BaseModel):
    query: str

class PreviewAgentRequest(BaseModel):
    url: str

class UpdateAgentEnabledRequest(BaseModel):
    agent_id: str
    enabled: bool

def create_send_message_payload(
    text: str, task_id: str | None = None, context_id: str | None = None
) -> dict[str, Any]:
    """Helper function to create the payload for sending a task."""
    payload: dict[str, Any] = {
        "message": {
            "role": "user",
            "parts": [{"type": "text", "text": text}],
            "messageId": uuid.uuid4().hex,
        },
    }

    if task_id:
        payload["message"]["taskId"] = task_id

    if context_id:
        payload["message"]["contextId"] = context_id
    return payload

def convert_response_to_json_str(response: Any) -> str:
    if hasattr(response, "root"):
        return response.root.model_dump_json(exclude_none=True)
    else:
        return json.dumps(response.model_dump(mode='json', exclude_none=True))

def name_normalize(name: str) -> str:
    return name.replace(".", "_").replace("-", "_").replace(" ", "_").lower()

def generate_function(function_name, desc):
    """Generate synchronous tool function that uses threading for async calls"""
    
    def dynamic_func(task: str) -> str:
        """Synchronous function that runs async code in a separate thread"""
        import threading
        import queue
        import asyncio
        
        result_queue = queue.Queue()
        
        def run_async_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async function and put the result in the queue
            try:
                global a2a_manager
                if a2a_manager is None:
                    raise Exception("a2a_manager is None")
                
                result = loop.run_until_complete(
                    a2a_manager.invoke_remote_agent_streaming(task, function_name)
                )
                result_queue.put(result)
            except Exception as e:
                result_queue.put(f"Error: {str(e)}")
            finally:
                loop.close()
        
        # Start a new thread to run the async code
        thread = threading.Thread(target=run_async_in_thread)
        thread.start()
        thread.join()  # Wait for the thread to complete
        
        # Get the result from the queue
        return result_queue.get()
    
    # Set function attributes
    dynamic_func.__name__ = function_name
    dynamic_func.__qualname__ = function_name
    dynamic_func.__doc__ = desc
    
    # Apply tool decorator
    decorated_func = tool(dynamic_func)
    
    # Add to global namespace
    globals()[function_name] = decorated_func
    
    return decorated_func


# A2A Client Manager (adapted from your code)
class A2AClientManager:
    def __init__(self) -> None:
        self.a2aclient_pool = {}
        self.agent_cards = []
        self.tools = []
        
    async def add_agent_by_url(self, agent_url: str) -> str:
        """Add a single agent by URL and return agent_id."""        
        try:
            async with httpx.AsyncClient(timeout=120) as httpx_client:
                agent_card_client = A2ACardResolver(httpx_client=httpx_client, base_url=agent_url)
                agent_card = await agent_card_client.get_agent_card()
                
                a2aclient = await A2AClient.get_client_from_agent_card_url(
                    httpx_client, agent_url
                )
                
                agent_id = str(uuid.uuid4())
                normalized_name = name_normalize(agent_card.name)
                
                # Store in global registry
                skills_data = []
                for skill in agent_card.skills:
                    skills_data.append({
                        "name": skill.name,
                        "description": skill.description,
                        "examples": skill.examples
                    })
                
                agent_registry[agent_id] = {
                    "name": agent_card.name,
                    "description": agent_card.description,
                    "url": agent_url,
                    "skills": skills_data,
                    "status": "active",
                    "enabled": True,  # Default to enabled when adding new agent
                    "created_at": datetime.now().isoformat(),
                    "normalized_name": normalized_name
                }
                
                # Store A2A agent_url
                self.a2aclient_pool[normalized_name] = agent_url
                self.agent_cards.append(agent_card)
                
                # Regenerate tools
                self._generate_tools()
                
                return agent_id
            
        except Exception as e:
            raise Exception(f"Failed to add agent: {str(e)}")
    
    def remove_agent(self, agent_id: str):
        """Remove an agent by ID."""
        if agent_id in agent_registry:
            normalized_name = agent_registry[agent_id].get("normalized_name")
            if normalized_name and normalized_name in self.a2aclient_pool:
                del self.a2aclient_pool[normalized_name]
            
            # Remove from agent_cards
            agent_name = agent_registry[agent_id].get("name")
            self.agent_cards = [card for card in self.agent_cards if card.name != agent_name]
            
            # Remove from registries
            del agent_registry[agent_id]
            
            # Regenerate tools
            self._generate_tools()

    def _generate_tools(self):
        """Generate tools that invoke a2a remote agents as tools, only for enabled agents."""
        self.tools = []
        
        AGENT_DESC_TEMPLATE = """
{description}

## Description of agent skills
{skills}
"""
        
        SKILL_DESC_TEMPLATE = """### skill[{idx}]:
- Skill name:
{skill_name}

- Description:
{skill_desc}

- Examples:
{skill_examples}
"""
        
        # Only generate tools for enabled agents
        for agent_card in self.agent_cards:
            # Find the corresponding agent in the registry to check enabled status
            agent_enabled = True  # Default to True if not found in registry
            normalized_name = name_normalize(agent_card.name)
            
            # Check if this agent is enabled in the registry
            for agent_id, agent_data in agent_registry.items():
                if agent_data.get("normalized_name") == normalized_name:
                    agent_enabled = agent_data.get("enabled", True)
                    break
            
            # Only create tools for enabled agents
            if agent_enabled:
                agent_skills = []
                for id, skill in enumerate(agent_card.skills):
                    desc = SKILL_DESC_TEMPLATE.format(
                        idx=id+1,
                        skill_name=skill.name,
                        skill_desc=skill.description,
                        skill_examples=skill.examples,
                    )
                    agent_skills.append(desc)
                
                function_desc = AGENT_DESC_TEMPLATE.format(
                    description=agent_card.description,
                    skills="\n".join(agent_skills)
                )
                
                self.tools.append(self._generate_function(normalized_name, function_desc))
        
        return self.tools
    
    def _generate_function(self, function_name, desc):
        """Generate a tool function for the agent."""
        agent_tool = generate_function(function_name,desc)
        return agent_tool

    
    def invoke_remote_agent_streaming_sync(self, query: str, agent_name: str) -> str:
        """A fully synchronous method to invoke remote agents."""
        nest_asyncio.apply()
        return asyncio.run(self.invoke_remote_agent_streaming(query, agent_name))

    async def invoke_remote_agent_streaming(self, query: str, agent_name: str) -> str:
        """A single-turn streaming request to remote agent."""
        send_payload = create_send_message_payload(text=query)
        
        agent_url = self.a2aclient_pool.get(agent_name)
        async with httpx.AsyncClient(timeout=120) as httpx_client:
            a2aclient = await A2AClient.get_client_from_agent_card_url(
                httpx_client, agent_url
            )
            artifact = ""
            stream_response = a2aclient.send_message_streaming(
                SendStreamingMessageRequest(params=MessageSendParams(**send_payload))
            )
            
            async for chunk in stream_response:
                chunk = json.loads(convert_response_to_json_str(chunk))
                if "final" in chunk["result"] and chunk["result"].get("final") == False:
                    pass  # Intermediate streaming
                elif "artifact" in chunk["result"]:
                    artifact = chunk["result"]["artifact"]["parts"][0]["text"]
                    
            return artifact

# Lead Agent (adapted from your code)
class LeadAgent:
    def __init__(self, tools: List[Any]):
        self.messages = []
        self.tools = tools
        self.conversation_manager = SlidingWindowConversationManager(
            window_size=20,
        )
        
    def get_agent(self):
        agent = Agent(
            model=MODEL,
            messages=self.messages,
            conversation_manager=self.conversation_manager,
            system_prompt="""You are a coordinator agent, you can communicate with other remote agents to resolve problems.""",
            tools=self.tools
        )
        return agent
        
    async def stream(self, query: str, session_id: str = None):      
        """Stream responses from the lead agent."""
        tool_use_buffer_start = False
        tool_use_name_buffer = ""
        tool_use_input_buffer = ""
        try:
            async for event in self.get_agent().stream_async(query):
                if "data" in event:
                    if tool_use_buffer_start:
                        yield {"current_tool_use":tool_use_name_buffer}
                        yield {"current_tool_use_input":tool_use_input_buffer}
                        tool_use_buffer_start = False
                        tool_use_name_buffer = ""
                        tool_use_input_buffer = ""
                    yield {"data":event["data"]}
                        
                elif "current_tool_use" in event and event["current_tool_use"].get("name"):
                    # logger.info(f"{event['current_tool_use']}")
                    tool_use_name_buffer = event["current_tool_use"]["name"]
                    tool_use_input_buffer = event["current_tool_use"]["input"]
                    tool_use_buffer_start = True
            
                    
            self.messages = self.get_agent().messages
        except Exception as e:
            yield f"Error: {str(e)}"

# Global instances
a2a_manager = A2AClientManager()

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global  lead_agent_instance
    yield

# FastAPI app
app = FastAPI(
    title="A2A Remote Agents API",
    description="API for managing and invoking remote agents using A2A protocol with Strands SDK",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/list_agents", response_model=List[AgentInfo])
async def list_agents():
    """Get all registered remote agents information."""
    agents_list = []
    for agent_id, agent_data in agent_registry.items():
        # Get the first skill for backward compatibility
        skill_name = ""
        skill_description = ""
        skills_data = agent_data.get("skills", [])
        
        # Ensure skills data is in the correct format
        skills = []
        if skills_data:
            first_skill = skills_data[0]
            skill_name = first_skill.get("name", "")
            skill_description = first_skill.get("description", "")
            
            # Convert skills to the expected format
            for skill in skills_data:
                skills.append({
                    "name": skill.get("name", ""),
                    "description": skill.get("description", "")
                })
        
        agents_list.append(AgentInfo(
            id=agent_id,
            name=agent_data.get("name", ""),
            description=agent_data.get("description", ""),
            url=agent_data.get("url", ""),
            skill_name=skill_name,
            skill_description=skill_description,
            skills=skills if skills else None,  # Include all skills
            status=agent_data.get("status", "unknown"),
            enabled=agent_data.get("enabled", True)
        ))
    
    return agents_list

@app.post("/preview_agent")
async def preview_agent(request: PreviewAgentRequest):
    """Preview agent information before adding."""
    try:        
        agent_url = request.url
        async with httpx.AsyncClient(timeout=120) as httpx_client:
            # Get agent card
            agent_card_client = A2ACardResolver(httpx_client=httpx_client, base_url=agent_url)
            agent_card = await agent_card_client.get_agent_card()
            
            # Format skills data
            skills_data = []
            for skill in agent_card.skills:
                skills_data.append({
                    "name": skill.name,
                    "description": skill.description
                })
            
            return {
                "name": agent_card.name,
                "description": agent_card.description,
                "skills": skills_data
            }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to preview agent: {str(e)}")

@app.post("/add_agent")
async def add_agent(request: AddAgentRequest):
    """Register a new remote agent by URL."""
    try:
        global a2a_manager, lead_agent_instance
        
        agent_id = await a2a_manager.add_agent_by_url(request.url)
        
        # Recreate lead agent with updated tools
        lead_agent_instance = LeadAgent(tools=a2a_manager.tools)
        
        agent_name = agent_registry[agent_id].get("name", "Unknown")
        
        return {
            "message": "Agent registered successfully",
            "agent_id": agent_id,
            "agent_name": agent_name
        }
        
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/delete_agent")
async def delete_agent(request: DeleteAgentRequest):
    """Delete a registered remote agent."""
    global a2a_manager, lead_agent_instance
    
    agent_id = request.agent_id
    
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_name = agent_registry[agent_id].get("name", "Unknown")
    a2a_manager.remove_agent(agent_id)
    
    # Recreate lead agent with updated tools
    lead_agent_instance = LeadAgent(tools=a2a_manager.tools)
    
    return {
        "message": f"Agent '{agent_name}' deleted successfully",
        "agent_id": agent_id
    }

@app.put("/update_agent_enabled")
async def update_agent_enabled(request: UpdateAgentEnabledRequest):
    """Update the enabled status of a remote agent."""
    global a2a_manager, lead_agent_instance
    
    agent_id = request.agent_id
    
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update the enabled status
    agent_registry[agent_id]["enabled"] = request.enabled
    agent_name = agent_registry[agent_id].get("name", "Unknown")
    
    # Regenerate tools to reflect the enabled/disabled status
    a2a_manager._generate_tools()
    
    # Recreate lead agent with updated tools
    lead_agent_instance = LeadAgent(tools=a2a_manager.tools)
    
    return {
        "message": f"Agent '{agent_name}' {'enabled' if request.enabled else 'disabled'} successfully",
        "agent_id": agent_id,
        "enabled": request.enabled,
        "active_tools_count": len(a2a_manager.tools)
    }

@app.post("/invoke_stream")
async def invoke_stream(request: InvokeStreamRequest):
    """Invoke the lead agent with streaming response using SSE."""
    
    async def generate_stream():
        try:
            global lead_agent_instance
            
            # Filter enabled agents (for now, we use all available agents as tools)
            if not lead_agent_instance:
                lead_agent_instance = LeadAgent(tools=a2a_manager.tools)
            
            logger.info("Starting stream generation...")
            yield "data: {\"type\": \"start\", \"message\": \"Starting lead agent...\"}\n\n"
            
            # Stream from lead agent
            async for chunk in lead_agent_instance.stream(request.query):
                if chunk:
                    logger.info(chunk)
                    if "data" in chunk:
                        yield f"data: {json.dumps({'type': 'stream', 'content': chunk['data']})}\n\n"
                    if "current_tool_use" in chunk:
                        yield f"data: {json.dumps({'type': 'current_tool_use', 'content': chunk['current_tool_use']})}\n\n"
                    if "current_tool_use_input" in chunk:
                        yield f"data: {json.dumps({'type': 'current_tool_use_input', 'content': chunk['current_tool_use_input']})}\n\n"
            
            yield "data: {\"type\": \"complete\", \"message\": \"Lead agent completed\"}\n\n"
            
        except Exception as e:
            error_msg = f"Error in stream processing: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "registered_agents": len(agent_registry),
        "available_tools": len(a2a_manager.tools) if a2a_manager else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException, Header,Request
from pydantic import BaseModel
from typing import Dict, Any,Optional
from datetime import datetime, timezone
from strands import Agent
from concurrent.futures import ThreadPoolExecutor
import asyncio
from streaming_utils import StreamingQueue,pull_queue_stream,process_stream_response
import logging
from contextlib import asynccontextmanager
from strands.models import BedrockModel
from botocore.config import Config
import psutil
import os
from constant_helper import is_interleaved_claude_thinking,is_claude_thinking,is_prompt_cache
from strands.agent.conversation_manager import SummarizingConversationManager
from skill_tool import generate_skill_tool,SkillToolInterceptor 
from ask_user_tool import ask_user
from pathlib import Path
from strands_tools import file_read, shell, editor,file_write
from fastapi.responses import JSONResponse, StreamingResponse
import uuid
from data_types import RequestContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_ID = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
MAX_TOKENS = 16000
TEMPERATURE = 0.7

# Save agents instances
agent_pool = {}


ROOT = Path(__file__).parent
WORK_ROOT = Path(__file__).parent / "workdir"
print(f"work dir: {WORK_ROOT}")
try:
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
except PermissionError:
    logger.error(f"Error: No permission to create directory at {WORK_ROOT}")
    raise
except Exception as e:
    logger.error(f"Error creating work directory: {e}")
    raise



# Thread pool for concurrent agent processing
# Max workers can be configured based on your requirements
MAX_WORKERS = 100
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="agent-worker")

# Track active tasks for ping status
active_tasks = {}
active_tasks_lock = asyncio.Lock()
last_status_update_time = datetime.now(timezone.utc)

class InvocationRequest(BaseModel):
    payload: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]
    
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Manages thread pool lifecycle.
    """
    # Startup
    logger.info(f"Starting Strands Agent Server with {MAX_WORKERS} worker threads")
    yield
    # Shutdown
    logger.info("Shutting down thread pool...")
    executor.shutdown(wait=True)
    logger.info("Thread pool shutdown complete")

app = FastAPI(
    title="Strands Agent Server",
    version="1.0.0",
    lifespan=lifespan
)
            
# Initialize streaming stream_queue
stream_queue = StreamingQueue()

# Global variable to track current running agent task
current_agent_task: Optional[asyncio.Task] = None


async def add_active_task(request_id: str,task:asyncio.Task):
    """Add task to active tasks tracking"""
    global last_status_update_time
    async with active_tasks_lock:
        active_tasks[request_id] = task
        logger.debug(f"Active tasks count: {len(active_tasks)}")

async def remove_active_task(request_id: str):
    """Remove task from active tasks tracking"""
    global last_status_update_time
    async with active_tasks_lock:
        if request_id in active_tasks:
            del active_tasks[request_id]
            last_status_update_time = datetime.now(timezone.utc)
            logger.debug(f"Active tasks count: {len(active_tasks)}")

def init_agent(model_id:str,
                     system:str,
                     max_tokens:int,
                     temperature:float,
                     thinking:bool,
                     thinking_budget:bool):


    additional_request_fields = {
            "thinking": {
                "type":"enabled" if thinking else 'disabled',
                "budget_tokens": thinking_budget,
            }
        } if thinking else {}
    
    cache_tools = None
    cache_prompt= None
    if is_prompt_cache(model_id):
        cache_tools = "default"
        cache_prompt="default"
    
    if thinking and is_claude_thinking(model_id):
        temperature = 1.0
        max_tokens = thinking_budget+1 if max_tokens<= thinking_budget else max_tokens
        
    if is_interleaved_claude_thinking(model_id):
        additional_request_fields['anthropic_beta'] = ["interleaved-thinking-2025-05-14","fine-grained-tool-streaming-2025-05-14"]
    
    agent_model = BedrockModel(
                    model_id= model_id,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    cache_tools=cache_tools,
                    cache_prompt=cache_prompt,
                    additional_request_fields = additional_request_fields,
                    boto_client_config=Config(
                                read_timeout=1800,
                                connect_timeout=60,
                                retries=dict(max_attempts=3, mode="adaptive"),
                                ),
                )
    # Create a cheaper, faster model for summarization tasks
    summarization_model = BedrockModel(
        model_id="global.anthropic.claude-haiku-4-5-20251001-v1:0",  # More cost-effective for summarization
        max_tokens=10000,
        temperature=0.1,  # Low temperature for consistent summaries
    )
    conversation_manager = SummarizingConversationManager(
            summary_ratio=0.4,
            preserve_recent_messages=20,
            summarization_agent=Agent(model=summarization_model)
    )

    # Dynamically create skill tools, as it should read Skills folders when agent starts.
    skill_tool = generate_skill_tool()


    # Create agent with MCP tools
    agent = Agent(
            model=agent_model,
            system_prompt=f"""{system}
    You are can access to various skills that enhance your capabilities.
    <IMPORTANT>
    - Your current project root is {ROOT} and your working directory is {WORK_ROOT}, you are grant write permissions with file system (create/edit/delete etc) in the working directory {WORK_ROOT}.
    Don't create files outside the working directory.    
    - Use 'AskUserQuestion' tool when you need to ask the user questions during execution. 
    </IMPORTANT>
    """,
            tools=[file_read, shell, editor,file_write, skill_tool,ask_user],
            conversation_manager=conversation_manager,
            hooks=[SkillToolInterceptor(cache_enabled=True if not cache_prompt else False)],
            callback_handler=None
            )

    return agent


async def process_agent_request(user_message: str, session_id:str, request_id: str) -> Dict[str, Any]:
    """
    Process agent request in a separate thread.
    Each invocation creates a new Agent instance to ensure isolation.

    Args:
        user_message: User's prompt message
        session_id: User session id
        request_id: Unique request identifier for logging

    Returns:
        Response dictionary with agent result
    """
    global agent_pool
    try:
        logger.info(f"Session {session_id} Request {request_id}: Starting agent processing")

        agent = agent_pool.get(session_id)
        assert agent is not None
        # Process the message
        stream_response = agent.stream_async(user_message)
        async for event in process_stream_response(stream_response):
            await stream_queue.put(event)
        logger.info(f"Request {request_id}: Agent processing completed")
        await stream_queue.finish()

    except Exception as e:
        logger.error(f"Request {request_id}: Agent processing failed - {str(e)}")
        raise

async def get_stats_data() -> Dict[str, Any]:
    """Get thread pool, task statistics, CPU and memory usage"""
    async with active_tasks_lock:
        active_count = len(active_tasks)

    # Get current process
    process = psutil.Process(os.getpid())

    # Get CPU usage (percent over short interval)
    cpu_percent = process.cpu_percent(interval=0.1)

    # Get memory info
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / (1024 * 1024)  # Convert bytes to MB
    memory_percent = process.memory_percent()

    # Get system-wide stats
    system_cpu_percent = psutil.cpu_percent(interval=0.1)
    system_memory = psutil.virtual_memory()

    return {
        "max_workers": MAX_WORKERS,
        "active_threads": executor._threads.__len__() if executor._threads else 0,
        "active_tasks": active_count,
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "process": {
            "cpu_percent": round(cpu_percent, 2),
            "memory_mb": round(memory_mb, 2),
            "memory_percent": round(memory_percent, 2),
            "pid": os.getpid()
        },
        "system": {
            "cpu_percent": round(system_cpu_percent, 2),
            "memory_total_mb": round(system_memory.total / (1024 * 1024), 2),
            "memory_used_mb": round(system_memory.used / (1024 * 1024), 2),
            "memory_available_mb": round(system_memory.available / (1024 * 1024), 2),
            "memory_percent": round(system_memory.percent, 2)
        }
    }


    
def build_request_context(request) -> RequestContext:
    SESSION_HEADER = "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id"
    REQUEST_ID_HEADER = "X-Amzn-Bedrock-AgentCore-Runtime-Request-Id"
    
    headers = request.headers
    request_id = headers.get(REQUEST_ID_HEADER)
    if not request_id:
        request_id = str(uuid.uuid4())
    session_id = headers.get(SESSION_HEADER)
    
    return RequestContext(session_id=session_id,request_headers=dict(request_id=request_id))

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(invocation_request: InvocationRequest,request: Request):
    """
    Handle agent invocation requests with concurrent processing.
    Each request is processed in a separate thread from the thread pool.

    Special requests:
    - If input contains 'get_stats': true, returns statistics instead of processing agent
    """
    
    global agent_pool,stream_queue
    
    request_context = build_request_context(request=request)

    logger.info(f"invocation request:{invocation_request.payload}")
    try:
        # Check if this is a stats request
        if invocation_request.payload.get("get_stats") is True:
            logger.info("Stats request received via invocations endpoint")
            stats_data = await get_stats_data()
            return InvocationResponse(output={
                "type": "stats",
                "data": stats_data
            })

        system = invocation_request.payload.get("system", "")
        thinking = invocation_request.payload.get("thinking", False)
        thinking_budget = invocation_request.payload.get("thinking_budget", 1024)
        model_id = invocation_request.payload.get("model_id", MODEL_ID)
        max_tokens =  invocation_request.payload.get("max_tokens",MAX_TOKENS)
        temperature = invocation_request.payload.get("temperature",TEMPERATURE)
        user_message = invocation_request.payload.get("prompt", "")

        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )
        session_id = request_context.session_id
        if session_id not in agent_pool:
            agent = init_agent(system=system,
                                     temperature=temperature,
                                     thinking=thinking,
                                     thinking_budget=thinking_budget,
                                     model_id=model_id,
                                     max_tokens=max_tokens)
            agent_pool[session_id] = agent
            
        # get unique request ID for tracking
        request_id = request_context.request_headers['request_id']

        logger.info(f"Request {request_id}: Received invocation request")       

        try:

            # loop = asyncio.get_event_loop()
            task = asyncio.create_task(process_agent_request(user_message,session_id, request_id))
            # Add task to active tasks tracking
            await add_active_task(request_id,task)

            async def stream_with_task():
                """Stream results while ensuring task completion."""
                try:
                    async for item in pull_queue_stream(model_id=model_id,stream_queue=stream_queue):
                        yield item
                        logger.info(item)
                    await task
                except asyncio.CancelledError:
                    logger.info("Agent task was cancelled")
                    # Don't re-raise, just complete the stream gracefully
                finally:
                    await remove_active_task(request_id)  # Clear task reference when done
            
            return StreamingResponse(
                    stream_with_task(),
                    media_type="text/event-stream",
                    headers={"X-Request-ID": request_id}  
                    )
        
        finally:
            # Remove task from active tasks tracking
            await remove_active_task(request_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Invocation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

@app.get("/ping")
async def ping():
    """
    Health check endpoint with busy status detection.
    Returns HEALTHY when no tasks are running, HEALTHY_BUSY when tasks are active.
    """
    async with active_tasks_lock:
        active_count = len(active_tasks)
        status = "HEALTHY_BUSY" if active_count > 0 else "HEALTHY"

        return {
            "status": status,
            "timeOfLastUpdate": last_status_update_time.isoformat(),
            "activeTasks": active_count
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
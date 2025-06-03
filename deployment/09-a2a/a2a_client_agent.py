from strands import Agent
from a2a.client import A2AClient,A2ACardResolver
from typing import Any,List
import json
from termcolor import colored
from uuid import uuid4
from a2a.types import (
    MessageSendParams,
    SendStreamingMessageRequest,
)
import httpx
import traceback
from strands import tool
from strands.agent.conversation_manager import SlidingWindowConversationManager
import asyncio
import nest_asyncio
MODEL = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

httpx_client = None
a2a_manager = None


import base64
import os
public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
# Set up endpoint
otel_endpoint = str(os.environ.get("LANGFUSE_HOST")) + "/api/public/otel/v1/traces"
auth_token = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = otel_endpoint
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {auth_token}"


def get_httpx_client(timeout=30):
    global httpx_client
    if httpx_client is None:
        httpx_client = httpx.AsyncClient(timeout=timeout)
    return httpx_client

async def close_httpx_client():
    global httpx_client
    if httpx_client is not None:
        await httpx_client.aclose()
        httpx_client = None

def create_send_message_payload(
    text: str, task_id: str | None = None, context_id: str | None = None
) -> dict[str, Any]:
    """Helper function to create the payload for sending a task."""
    payload: dict[str, Any] = {
        "message": {
            "role": "user",
            "parts": [{"type": "text", "text": text}],
            "messageId": uuid4().hex,
        },
    }

    if task_id:
        payload["message"]["taskId"] = task_id

    if context_id:
        payload["message"]["contextId"] = context_id
    return payload

def conver_response_to_json_str(response:Any) -> dict:
    if hasattr(response, "root"):
        return(f"{response.root.model_dump_json(exclude_none=True)}\n")
    else:
        return(f"{response.model_dump(mode='json', exclude_none=True)}\n")

def print_json_response(response: Any, description: str) -> None:
    """Helper function to print the JSON representation of a response."""
    print(f"--- {description} ---")
    if hasattr(response, "root"):
        print(f"{response.root.model_dump_json(exclude_none=True)}\n")
    else:
        print(f"{response.model_dump(mode='json', exclude_none=True)}\n")


def generate_function_2(function_name, desc):
    """Generate a tool function that properly handles async/sync boundaries."""
    
    async def async_dynamic_func(task: str) -> str:
        """Async implementation of the function."""
        global a2a_manager
        if a2a_manager is None:
            raise Exception("a2a_manager is None")
        
        try:
            # 直接调用异步方法
            return await a2a_manager.invoke_remote_agent_streaming(task, function_name)
        except Exception as e:
            return f"Error invoking {function_name}: {str(e)}"
    
    def dynamic_func(task: str) -> str:
        """Synchronous wrapper that properly handles the event loop."""
        import asyncio
        
        # 获取当前事件循环或创建新循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 执行异步函数
        if loop.is_running():
            # 如果循环已运行(使用nest_asyncio的场景)
            return asyncio.run_coroutine_threadsafe(async_dynamic_func(task), loop).result()
        else:
            # 标准执行方式
            return loop.run_until_complete(async_dynamic_func(task))
    
    # 设置函数属性
    dynamic_func.__name__ = function_name
    dynamic_func.__qualname__ = function_name
    dynamic_func.__doc__ = desc
    
    # 应用工具装饰器
    decorated_func = tool(dynamic_func)
    globals()[function_name] = decorated_func
    
    return decorated_func


def generate_function(function_name, desc):
    code = f"""
@tool
def {function_name}(task: str) -> str:
    \"""{desc}
    Args:
        task: str, the task message send to remote agent.
    Returns:
        str, the result of the task.
    \"""
    from __main__ import a2a_manager
    if a2a_manager is None:
        raise Exception("a2a_manager is None")
    
    result = a2a_manager.invoke_remote_agent_streaming_sync(task, "{function_name}") 
    print(f"result:{{result}}")
    return result
"""
    # Execute code, adding function to local namespace
    local_vars = {}
    exec(code, {"tool": tool}, local_vars)
    
    # Add function to global namespace
    globals()[function_name] = local_vars[function_name]
    return local_vars[function_name]


class LeadAgent:
    def __init__(self,tools:List[Any]):
        self.messages = []
        self.tools = tools
        self.conversation_manager = SlidingWindowConversationManager(
            window_size=10,  # Maximum number of messages to keep
        )
    
    @property
    def get_agent(self):
        agent = Agent(model=MODEL,
                    messages=self.messages,
                    conversation_manager=self.conversation_manager,
                    system_prompt="""You are a coodinator agent, you can communicate with other remote agents to resolve problems.
                    """,
                    tools=self.tools)
        return agent
        
    async def invoke(self, prompt) -> str:
        try:
            response = self.get_agent(prompt)
            self.messages = self.get_agent.messages
            print(colored(response,"blue"),end="",flush=True)
            return response
        except Exception as e:
            raise f"Error invoking agent: {e}"

        
    async def stream(self, query: str, session_id: str = None):      
        response = str()
        try:
            async for event in self.get_agent.stream_async(query):
                if "data" in event:
                    # Only stream text chunks to the client
                    response += event["data"]
                    print(colored(event["data"],"blue"),end="",flush=True)
            self.messages = self.get_agent.messages

        except Exception as e:
            print(colored(str(e),"red"),flush=True)

AGENT_DESC_TEMPLATE = """
{description}

## Description of agent skills
{skills}
"""

SKILL_DESC_TEMPLATE="""### skill[{idx}]:
- Skill name:
{skill_name}

- Description:
{skill_desc}

- Examples:
{skill_examples}
"""


class A2AClientManager:
    
    def __init__(self, agent_urls:List[str]) -> None:
        self.agent_urls = agent_urls
        self.a2aclient_pool = {}
        self.agent_cards = []
        self.messages = []
        self.tools = []
        
    def name_normalize(self, name: str) -> str:
        return name.replace(".", "_").replace("-", "_").replace(" ", "_").lower()
    
    async def init_a2aclients(self) -> []:
        """initialize a2a clients from agent urls."""
        global httpx_client
        httpx_client = get_httpx_client()
        for agent_url in self.agent_urls:
            try:
                agent_card_client = A2ACardResolver(httpx_client=httpx_client,base_url=agent_url)
                agent_card = await agent_card_client.get_agent_card()
                print(f"Found agent card: {agent_card}")
                self.agent_cards.append(agent_card)
                # a2aclient = await A2AClient.get_client_from_agent_card_url(
                #     httpx_client, agent_url
                # )
                self.a2aclient_pool[self.name_normalize(agent_card.name)] = agent_url
            except Exception as e:
                print(f"Error initializing A2AClient: {e}")
        # generate tools
        self.tools = self._generate_tools()
        return self.tools
                

    def _generate_tools(self):
        """generate tools that invoke a2a remote agents as tools."""
        for agent_card in self.agent_cards:
            agent_skills = []
            for id,skill in enumerate(agent_card.skills):
                desc = SKILL_DESC_TEMPLATE.format(
                    idx=id+1,
                    skill_name=skill.name,
                    skill_desc=skill.description,
                    skill_examples=skill.examples,
                )
                agent_skills.append(desc)
            function_desc = AGENT_DESC_TEMPLATE.format(description=agent_card.description,
                                                       skills="\n".join(agent_skills))
            print(f"function_desc: {function_desc}")
            self.tools.append(generate_function(self.name_normalize(agent_card.name), function_desc))
        return self.tools
    
    def invoke_remote_agent_streaming_sync(self, query: str, agent_name: str) -> str:
        """A fully synchronous method to invoke remote agents."""
        nest_asyncio.apply()
        return asyncio.run(self.invoke_remote_agent_streaming(query, agent_name))

        
    async def invoke_remote_agent_streaming(self, query:str, agent_name: str) -> str:
        """a single-turn streaming request to remote agent."""
        send_payload = create_send_message_payload(text=query)

        # a2aclient = self.a2aclient_pool.get(agent_name)
        # if a2aclient is None:
        #     raise Exception(f"Agent {agent_name} not found")
        agent_url = self.a2aclient_pool.get(agent_name)
        async with httpx.AsyncClient(timeout=120) as httpx_client:
            a2aclient = await A2AClient.get_client_from_agent_card_url(
                httpx_client, agent_url
            )
            artifact = ""
            stream_response = a2aclient.send_message_streaming(SendStreamingMessageRequest(params=MessageSendParams(**send_payload)))
            async for chunk in stream_response:
                chunk = json.loads(conver_response_to_json_str(chunk))
                if "final" in chunk["result"] and chunk["result"].get("final") == False:
                    print(colored(chunk["result"]["status"]["message"]["parts"][0]["text"],"green"),end="",flush=True)
                elif "artifact" in chunk["result"]:
                    artifact= chunk["result"]["artifact"]["parts"][0]["text"]
                
        return artifact


def test_generate_function():
    tool = generate_function("test_function", "test function description")
    
    tool("hello")
    
async def main() -> None:
    import time
    global a2a_manager
    
    user_queries = [
        "what is result of 2 * sin(pi/5.1) + log(e**2.1)",
        "what time is now in beijing?",
        "How to integrate AWS Lambda with SNS?",
        "What are the IAM policies that AWS lambda should have?"
    ]
    
    AGENT_URLs = [
        # "http://localhost:10000",
                #   "http://localhost:10001",
                  "http://localhost:10002"]
    
    a2a_manager = A2AClientManager(AGENT_URLs)
    
    # 把remote agent，转化成tools
    tools = await a2a_manager.init_a2aclients()

    # 创建agent
    lead_agent = LeadAgent(tools=tools).get_agent
    
    # 测试remote agent
    lead_agent(user_queries[0])
    lead_agent(user_queries[1])
    
    # a2a_manager.invoke_remote_agent_streaming_sync(user_queries[0], "calculator")

    # 关闭连接
    await close_httpx_client()



if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

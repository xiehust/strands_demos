from strands import Agent
from strands.models import BedrockModel
from strands.agent.conversation_manager import SummarizingConversationManager,SlidingWindowConversationManager
from strands_tools import file_read, shell, editor,file_write,tavily
import boto3
import json
import os
import asyncio
import argparse
from strands.hooks import HookProvider,HookRegistry,BeforeModelCallEvent
import os
import re
import traceback
import logging
from ask_user_tool import ask_user
from pathlib import Path
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient

# 配置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


from dotenv import load_dotenv
load_dotenv()
session = boto3.Session(region_name = os.environ.get('region_name','us-west-2'))
os.environ['BYPASS_TOOL_CONSENT'] = "true"

ROOT = Path(__file__).parent
WORK_ROOT = Path(__file__).parent / "workdir"
print(f"work dir: {WORK_ROOT}")
try:
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
except PermissionError:
    print(f"Error: No permission to create directory at {WORK_ROOT}")
    raise
except Exception as e:
    print(f"Error creating work directory: {e}")
    raise

class CachePointInterceptor(HookProvider):
    def __init__(self):
        super().__init__()
        self.tooluse_ids = {}
    
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeModelCallEvent,self.add_message_cache)
            
    def add_message_cache(self, event:BeforeModelCallEvent) -> None:
        for message in event.agent.messages:
            content = message['content']
            if any(['cachePoint' in block for block in content]):
                content = content[:-1]
                message['content'] = content
        #add prompt cache to last message
        if event.agent.messages:
            event.agent.messages[-1]['content'] += [{
                "cachePoint": {
                    "type": "default"
                }
            }]
            
# Agent Configuration
agent_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=1,
    max_tokens=24000,
    cache_prompt="default",
    cache_tools="default",
    boto_session=session,
    additional_request_fields={
        "thinking": {
            "type": "enabled",
            "budget_tokens": 1024
        },
        "anthropic_beta":["interleaved-thinking-2025-05-14","fine-grained-tool-streaming-2025-05-14"]
    }
)

# Create a cheaper, faster model for summarization tasks
summarization_model = BedrockModel(
    model_id="global.anthropic.claude-haiku-4-5-20251001-v1:0",  # More cost-effective for summarization
    max_tokens=10000,
    boto_session=session,
    temperature=0.1,  # Low temperature for consistent summaries
)

conversation_manager = SummarizingConversationManager(
    summary_ratio=0.4,
    preserve_recent_messages=20,
    summarization_agent=Agent(model=summarization_model)
)

def get_skill_resource(client: MCPClient):
    """Display available resources with human-readable names."""
    print("\n📚 Step 1b: Discovering available resources...")
    print("-"*80)

    # List resources
    resources_response = client.list_resources_sync()
    print(f"✅ Found {len(resources_response.resources)} resources:\n")
    all_skills = None
    for resource in resources_response.resources:
        print(f"  📄 {resource.name}")
        print(f"     URI: {resource.uri}")
        if hasattr(resource, 'description') and resource.description:
            print(f"     Description: {resource.description}")
        if resource.name == "list_skills":
            source = client.read_resource_sync(resource.uri)
            all_skills = source.contents[0].text
            print(all_skills)
            break 
    return all_skills


async def main(user_input_arg: str = None, messages_arg: str = None):
    mcp_client = MCPClient(
        lambda: streamablehttp_client("http://localhost:8000/mcp/")
    )
    with mcp_client:
        skill_tool = mcp_client.list_tools_sync()
        print(f"✅ Connected! Loaded {len(skill_tool)} tools:")
        for tool in skill_tool:
            print(f"   - {tool.tool_name}")
        
        # read skills resources from MCP
        
        skills_desc = get_skill_resource(mcp_client)
        # Create agent with MCP tools
        agent = Agent(
                model=agent_model,
                system_prompt=f"""You are a helpful AI assistant with access to various skills that enhance your capabilities.
        You are equipped with skills:\n{skills_desc}
        <IMPORTANT>
        - Your current project root is {ROOT} and your working directory is {WORK_ROOT}, you are grant write permissions with file system (create/edit/delete etc) in the working directory {WORK_ROOT}.
        Don't create files outside the working directory.    
        - Use 'AskUserQuestion' tool when you need to ask the user questions during execution. 
        </IMPORTANT>
        """,
                tools=skill_tool+[file_read, shell, editor,file_write,ask_user,tavily],
                conversation_manager=conversation_manager,
                hooks=[CachePointInterceptor()]
                )


        # User input from command-line arguments with priority: --messages > --user-input > default
        if messages_arg is not None and messages_arg.strip():
            # Parse messages JSON and pass full conversation history to agent
            try:
                messages_list = json.loads(messages_arg)
                # Pass the full messages list to the agent
                user_input = messages_list
            except (json.JSONDecodeError, KeyError, TypeError):
                user_input = "Hello, how can you help me?"
        elif user_input_arg is not None and user_input_arg.strip():
            user_input = user_input_arg.strip()
        # Execute agent with streaming
        async for event in agent.stream_async(user_input):
            if "data" in event:
                print(event['data'],end='',flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Execute Strands Agent')
    parser.add_argument('--prompt', type=str, help='User input prompt')
    parser.add_argument('--messages', type=str, help='JSON string of conversation messages')

    args = parser.parse_args()

    user_input_param = args.prompt
    messages_param = args.messages

    asyncio.run(main(user_input_param, messages_param))
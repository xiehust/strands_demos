from strands import Agent
from strands.models import BedrockModel
from strands.agent.conversation_manager import SummarizingConversationManager,SlidingWindowConversationManager
from strands_tools import file_read, shell, editor,file_write,tavily
import boto3
import json
import os
import asyncio
import argparse
from skill_tool import generate_skill_tool,SkillToolInterceptor 
from ask_user_tool import ask_user
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
session = boto3.Session(region_name = os.environ.get('region_name','us-west-2'))
os.environ['BYPASS_TOOL_CONSENT'] = "true"

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

# Agent Configuration
agent_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=1,
    max_tokens=16000,
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
    max_tokens=4000,
    boto_session=session,
    temperature=0.1,  # Low temperature for consistent summaries
)

conversation_manager = SummarizingConversationManager(
    summary_ratio=0.3,
    preserve_recent_messages=20,
    summarization_agent=Agent(model=summarization_model)
)

# Dynamically create skill tools, as it should read Skills folders when agent starts.
skill_tool = generate_skill_tool()


# Create agent with MCP tools
agent = Agent(
        model=agent_model,
        system_prompt=f"""You are a helpful AI assistant with access to various skills that enhance your capabilities.
<IMPORTANT>
- Your current working directory is {WORK_ROOT}, you are grant permissions with file system (read/write/create/edit etc) in the working directory {WORK_ROOT}.
Don't create files outside the working directory.    
- Use 'AskUserQuestion' tool when you need to ask the user questions during execution. 
</IMPORTANT>
""",
        tools=[file_read, shell, editor,file_write, skill_tool,ask_user,tavily],
        conversation_manager=conversation_manager,
        hooks=[SkillToolInterceptor()]
        )


async def main(user_input_arg: str = None, messages_arg: str = None):
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
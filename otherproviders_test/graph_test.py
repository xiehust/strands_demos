from strands import Agent
from strands_tools import agent_graph

from dotenv import load_dotenv
import os
import base64
load_dotenv()
from strands.models.openai import OpenAIModel

# MODEL = "us.amazon.nova-pro-v1:0"
MODEL = OpenAIModel(
    client_args={
        "api_key": os.environ.get("API_KEY"),
        "base_url": "https://api.siliconflow.cn/v1",
    },
    # model_id="Pro/deepseek-ai/DeepSeek-R1",
    model_id = "Pro/deepseek-ai/DeepSeek-V3",
    # model_id = "Qwen/Qwen3-235B-A22B",
    # model_id = "Qwen/Qwen3-30B-A3B",
    params={
        "max_tokens": 8100,
        "temperature": 0.7,
    }
)


# Initialize Agent with agent_graph
agent = Agent(model=MODEL,tools=[agent_graph])

# Create a network through natural language
agent("Create a research team with a coordinator, data analyst, and domain expert in a star topology")

# Send a task to the team
agent("Ask the research team to analyze emerging technology adoption in healthcare")

# Check status and manage the network
agent("Show me the status of the research team")
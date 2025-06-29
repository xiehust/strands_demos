from strands import Agent
from strands_tools import calculator,current_time,http_request,shell
import asyncio
from strands.models import BedrockModel
import os

os.environ["BYPASS_TOOL_CONSENT"] = "true"

from dotenv import load_dotenv
import os
import base64
load_dotenv()
from strands.models.openai import OpenAIModel

MODEL = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

# MODEL = OpenAIModel(
#     client_args={
#         "api_key": os.environ.get("API_KEY"),
#         "base_url": "https://api.siliconflow.cn/v1",
#     },
#     # model_id="Pro/deepseek-ai/DeepSeek-R1",
#     # model_id = "Pro/deepseek-ai/DeepSeek-V3",
#     # model_id = "Qwen/Qwen3-235B-A22B",
#     model_id = "Qwen/Qwen3-30B-A3B",
#     params={
#         "max_tokens": 8100,
#         "temperature": 0.7,
#     }
# )


class CalcAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]
    
    def __init__(self):
        self.agent = Agent(
                    model=MODEL,
                    tools=[calculator,current_time,shell],
                    callback_handler=None,
                )        
        
    async def stream(self, query: str, session_id: str):      
        response = str()
        try:
            async for event in self.agent.stream_async(query):
                if "data" in event:
                    # Only stream text chunks to the client
                    response += event["data"]
                    yield {
                        "is_task_complete": "complete" in event,
                        "require_user_input": False,
                        "content": event["data"],
                    }

        except Exception as e:
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"We are unable to process your request at the moment. Error: {e}",
            }
        finally:
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response,
            }
            
class WeatherAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]
    
    # Define a weather-focused system prompt
    WEATHER_SYSTEM_PROMPT = """You are a weather assistant with HTTP capabilities. You can:

    1. Make HTTP requests to the National Weather Service API
    2. Process and display weather forecast data
    3. Provide weather information for locations in the United States

    When retrieving weather information:
    1. First get the coordinates or grid information using https://api.weather.gov/points/{latitude},{longitude} or https://api.weather.gov/points/{zipcode}
    2. Then use the returned forecast URL to get the actual forecast

    When displaying responses:
    - Format weather data in a human-readable way
    - Highlight important information like temperature, precipitation, and alerts
    - Handle errors appropriately
    - Convert technical terms to user-friendly language

    Always explain the weather conditions clearly and provide context for the forecast.
    """
    
    def __init__(self):
        self.agent = Agent(
                    system_prompt=self.WEATHER_SYSTEM_PROMPT,
                    model=MODEL,
                    tools=[http_request],
                    callback_handler=None,
                )        
        
    async def stream(self, query: str, session_id: str):      
        response = str()
        try:
            async for event in self.agent.stream_async(query):
                if "data" in event:
                    # Only stream text chunks to the client
                    response += event["data"]
                    yield {
                        "is_task_complete": "complete" in event,
                        "require_user_input": False,
                        "content": event["data"],
                    }

        except Exception as e:
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"We are unable to process your request at the moment. Error: {e}",
            }
        finally:
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response,
            }
            
async def main():
    # agent = CalcAgent()
    # async for chunk in agent.stream("what time is it now in beijing?", "123"):
    #     print(chunk, "")
    prompts = [
        "what it the weather forecast in new york?",
        "What is result of 2.21 * sin(pi/4.1) + log(e**2.3)?",
        "What is current time of beijing"
        
    ]
    agent = WeatherAgent()
    async for chunk in agent.stream(prompts[0], "123"):
        print(chunk, "",flush=True)

if __name__ == "__main__":
    asyncio.run(main())
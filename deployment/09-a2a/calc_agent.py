from strands import Agent
from strands_tools import calculator,current_time,http_request
import asyncio
from strands.models import BedrockModel

class CalcAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]
    
    def __init__(self):
        self.agent = Agent(
                    model="us.amazon.nova-pro-v1:0",
                    tools=[calculator,current_time],
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
                    model="us.amazon.nova-pro-v1:0",
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
    agent = WeatherAgent()
    async for chunk in agent.stream("what it the weather forecast in new york?", "123"):
        print(chunk, "")

if __name__ == "__main__":
    asyncio.run(main())
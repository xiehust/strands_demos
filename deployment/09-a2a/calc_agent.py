from strands import Agent
from strands_tools import calculator,python_repl
import asyncio
from strands.models import BedrockModel

class CalcAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]
    
    def __init__(self):
        self.agent = Agent(
                    model="us.amazon.nova-pro-v1:0",
                    tools=[calculator],
                    callback_handler=None,
                )
    
    async def invoke(self, prompt) -> str:
        try:
            response = self.agent(prompt)
            return response
        except Exception as e:
            raise f"Error invoking agent: {e}"

        
        
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
    agent = CalcAgent()
    response = await agent.invoke("what is result of 2 * sin(pi/4) + log(e**2)")
    print(response)
    async for chunk in agent.stream("what is result of 2 * sin(pi/4) + log(e**2)", "123"):
        print(chunk, "")

if __name__ == "__main__":
    asyncio.run(main())
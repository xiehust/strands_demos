import click
from calc_agent import WeatherAgent

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from agent_executor import StrandsAgentExecutor


@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10001)
def main(host: str, port: int):
    request_handler = DefaultRequestHandler(
        agent_executor=StrandsAgentExecutor(WeatherAgent()),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=get_agent_card(host, port), http_handler=request_handler
    )
    import uvicorn

    uvicorn.run(server.build(), host=host, port=port)

def get_agent_card(host: str, port: int):
    """Returns the Agent Card for the Currency Agent."""
    capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
    skill_1 = AgentSkill(
        id="weather_forecast",
        name="weather_forecast",
        description="""It can:
1. Make HTTP requests to the National Weather Service API
2. Process and display weather forecast data
3. Provide weather information for locations in the United States""",
        tags=["weather_forecast"],
        examples=[
            "What's the weather like in Seattle?",
            "Will it rain tomorrow in Miami?",
            "Compare the temperature in New York and Chicago this weekend"
        ],
    )
    return AgentCard(
        name="weather_forecast",
        description="A weather assistant with HTTP capabilities.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=WeatherAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=WeatherAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill_1],
        authentication=AgentAuthentication(schemes=["public"]),
    )
    

if __name__ == "__main__":
    main()

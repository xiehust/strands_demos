import click
from calc_agent import CalcAgent

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
from dotenv import load_dotenv
import os 
load_dotenv()



@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10002)
def main(host: str, port: int):
    request_handler = DefaultRequestHandler(
        agent_executor=StrandsAgentExecutor(CalcAgent()),
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
        id="calculator",
        name="calculator",
        description="Performing mathematical operations, symbolic math, equation solving.",
        tags=["calculator"],
        examples=[
            "What is result of 2 * sin(pi/4) + log(e**2)?",
        ],
    )
    skill_2 = AgentSkill(
        id="current_time",
        name="current_time",
        description="returns the current date and time in ISO 8601 format (e.g., 2023-04-15T14:32:16.123456+00:00) "
    "for the specified timezone. If no timezone is provided, the value from the DEFAULT_TIMEZONE",
        tags=["time"],
        examples=[
            "What is current time of beijing",
        ],
    )
    skill_3 = AgentSkill(
        id="shell",
        name="shell",
        description="Interactive shell with PTY support for real-time command execution and interaction.",
        tags=["shell"],
        examples=[
            "list current file path",
        ],
    )
    return AgentCard(
        name="utils_agent",
        description="get calculator and current time, and execute shell commands",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=CalcAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=CalcAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill_1,skill_2,skill_3],
        authentication=AgentAuthentication(schemes=["public"]),
    )
    



if __name__ == "__main__":
    main()

from strands.multiagent.a2a import A2AAgent
from strands import Agent
from strands_tools import calculator,current_time

MODEL = "us.amazon.nova-pro-v1:0"

# Create a basic agent
agent = Agent(
        name="utils agent",
        description="This agent is a simple agent that can calculate and tell the current time",
        model=MODEL,
        tools=[calculator,current_time],
        callback_handler=None,
        )   
# Wrap it with A2A capabilities
a2a_agent = A2AAgent(agent=agent)

# Start the A2A server
print("Starting A2A server on http://localhost:9000")
a2a_agent.serve()
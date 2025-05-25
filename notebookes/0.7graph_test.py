from strands import Agent
from strands_tools import agent_graph
# Initialize Agent with agent_graph
agent = Agent(tools=[agent_graph])

# Create a network through natural language
agent("Create a research team with a coordinator, data analyst, and domain expert in a star topology")

# Send a task to the team
agent("Ask the research team to analyze emerging technology adoption in healthcare")

# Check status and manage the network
agent("Show me the status of the research team")
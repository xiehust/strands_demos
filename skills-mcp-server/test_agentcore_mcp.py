import boto3
import utils
import os
import asyncio
from strands.models import BedrockModel
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp.mcp_client import MCPClient
from strands import Agent
import requests
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from dotenv import load_dotenv
load_dotenv('.cognito-s2.env')
REGION = 'us-east-1'

# runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:434444145045:runtime/skills_mcp-zL6Jpj23bp"
# runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:434444145045:runtime/skills_mcp3-hfrnA469mY"
runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:434444145045:runtime/skills_mcp-ECXa5Z6q1x"


runtime_user_pool_id = os.environ.get("POOL_ID")
runtime_client_id= os.environ.get("CLIENT_ID")
runtime_client_secret= os.environ.get("CLIENT_SECRET")
TOKEN_ENDPOINT = os.environ.get("TOKEN_ENDPOINT")
scopeString = "my-api/read my-api/write"

cognito = boto3.client("cognito-idp", region_name=REGION)

def get_token(client_id: str, client_secret: str, scope_string: str) -> dict:
    try:
        url = TOKEN_ENDPOINT
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope_string,

        }
        print(data)
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as err:
        return {"error": str(err)}
    
token_response = get_token( runtime_client_id, runtime_client_secret, scopeString )
print("Token response:", token_response)
token = token_response["access_token"]
print("Token response:", token)


print("==================")


mcpURL = f"https://bedrock-agentcore.{REGION}.amazonaws.com/runtimes/{runtime_arn.replace(":","%3A").replace("/","%2F")}/invocations?qualifier=DEFAULT"
print(mcpURL)
def create_streamable_http_transport():
    return streamablehttp_client(
        mcpURL, headers={"Authorization": f"Bearer {token}"}
    )


async def main():
    mcp_url = mcpURL
    headers ={"Authorization": f"Bearer {token}"}

    async with streamablehttp_client(mcp_url, headers, timeout=30, terminate_on_close=False) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tool_result = await session.list_tools()
            print(tool_result)

asyncio.run(main())


client = MCPClient(create_streamable_http_transport)

## The IAM group/user/ configured in ~/.aws/credentials should have access to Bedrock model
yourmodel = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0", # may need to update model_id depending on region
    temperature=0.7,
    max_tokens=2000,  # Limit response length
)

with client:
    # Call the listTools
    tools = client.list_tools_sync()
    # Create an Agent with the model and tools
    agent = Agent(
        model=yourmodel, tools=tools
    )  ## you can replace with any model you like
    # Invoke the agent with the sample prompt. This will only invoke MCP listTools and retrieve the list of tools the LLM has access to. The below does not actually call any tool.
    # agent("Hi, can you list all tools available to you")
    agent("list all your tools")
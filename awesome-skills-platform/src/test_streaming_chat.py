"""
Test script for streaming chat endpoint.
"""
import requests
import json
import sys

def test_streaming_chat():
    """Test the streaming chat endpoint."""
    print("🧪 Testing Streaming Chat Endpoint")
    print("=" * 60)

    # Use test agent with skills
    agent_id = "test-agent-skills"
    message = "Hello! Can you tell me a short joke?"

    url = "http://localhost:8000/api/chat/stream"
    payload = {
        "agentId": agent_id,
        "message": message
    }

    print(f"Agent ID: {agent_id}")
    print(f"Message: {message}")
    print("-" * 60)
    print("Response stream:")
    print()

    try:
        # Make streaming request
        with requests.post(url, json=payload, stream=True, timeout=60) as response:
            response.raise_for_status()

            # Process SSE stream
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')

                    # SSE format: "data: {json}"
                    if line_str.startswith('data: '):
                        data_json = line_str[6:]  # Remove "data: " prefix
                        try:
                            data = json.loads(data_json)
                            event_type = data.get('type')

                            if event_type == 'start':
                                print(f"✅ Stream started")
                                print(f"   Conversation ID: {data.get('conversationId')}")
                                print()

                            elif event_type == 'text':
                                # Print text chunks without newline
                                print(data.get('content', ''), end='', flush=True)

                            elif event_type == 'thinking':
                                print(f"\n💭 Thinking: {data.get('content')}")

                            elif event_type == 'tool_use':
                                tool = data.get('tool', {})
                                print(f"\n🔧 Tool use: {tool.get('name')}")

                            elif event_type == 'tool_result':
                                print(f"\n✅ Tool result received")

                            elif event_type == 'done':
                                print(f"\n\n✅ Stream complete")
                                print(f"   Model: {data.get('modelId')}")

                            elif event_type == 'error':
                                print(f"\n❌ Error: {data.get('error')}")

                        except json.JSONDecodeError:
                            print(f"Warning: Could not parse JSON: {data_json}")

        print()
        print("=" * 60)
        print("✅ Test completed successfully!")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    test_streaming_chat()

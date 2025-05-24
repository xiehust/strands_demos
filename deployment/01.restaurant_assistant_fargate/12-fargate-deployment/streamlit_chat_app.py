import streamlit as st
import requests
import uuid
from datetime import datetime
import time
import json
import re

# Page configuration
st.set_page_config(
    page_title="Chat Agent Service",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .message-content {
        flex: 1;
        padding: 0 1rem;
    }
    .message-icon {
        font-size: 1.5rem;
    }
    .timestamp {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'service_url' not in st.session_state:
    st.session_state.service_url = ""
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# Sidebar for configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Service URL input
    service_url = st.text_input(
        "Service URL",
        value=st.session_state.service_url,
        placeholder="Enter your service URL (without http://)",
        help="Enter the ALB DNS for your chat service"
    )
    
    # API Key input
    api_key = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="Enter your API key",
        help="Your authentication API key"
    )
    
    # Save configuration
    if st.button("💾 Save Configuration", use_container_width=True):
        st.session_state.service_url = service_url
        st.session_state.api_key = api_key
        st.success("Configuration saved!")
    
    st.divider()
    
    # Session management
    st.subheader("Session Management")
    
    # Display current session ID
    st.info(f"Session ID: {st.session_state.session_id[:8]}...")
    
    col1, col2 = st.columns(2)
    
    # New session button
    with col1:
        if st.button("🆕 New Session", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()
    
    # Clear history button
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# Main chat interface
st.title("💬 Chat Agent Service")

# Check if configuration is complete
if not st.session_state.service_url or not st.session_state.api_key:
    st.warning("⚠️ Please configure the Service URL and API Key in the sidebar to start chatting.")
else:
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-icon">👤</div>
                <div class="message-content">
                    <strong>You</strong><br>
                    {message["content"]}
                    <div class="timestamp">{message["timestamp"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-icon">🤖</div>
                <div class="message-content">
                    <strong>Assistant</strong><br>
                    {message["content"]}
                    <div class="timestamp">{message["timestamp"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to history
        timestamp = datetime.now().strftime("%I:%M %p")
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message immediately
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-icon">👤</div>
            <div class="message-content">
                <strong>You</strong><br>
                {prompt}
                <div class="timestamp">{timestamp}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create placeholder for streaming response
        response_container = st.container()
        with response_container:
            assistant_message = st.empty()
            
        full_response = ""
        
        # Show typing indicator
        with assistant_message.container():
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-icon">🤖</div>
                <div class="message-content">
                    <strong>Assistant</strong><br>
                    <em>Typing...</em>
                    <div class="timestamp">{timestamp}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        try:
            # Make the POST request to the agent service
            response = requests.post(
                f"http://{st.session_state.service_url}/invoke-streaming",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {st.session_state.api_key}"
                },
                json={
                    "prompt": prompt,
                    "session_id": st.session_state.session_id
                },
                stream=True,
                timeout=60  # Add timeout for long responses
            )
            
            # Check if request was successful
            if response.status_code == 200:
                # Stream the response
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        # Handle different line formats (some APIs send data: prefix)
                        if decoded_line.startswith('data: '):
                            decoded_line = decoded_line[6:]
                        
                        # Skip empty lines or special markers
                        if decoded_line.strip() and decoded_line.strip() != '[DONE]':
                            full_response += decoded_line + " "
                            
                            # Update the assistant message with streaming content
                            with assistant_message.container():
                                st.markdown(f"""
                                <div class="chat-message assistant-message">
                                    <div class="message-icon">🤖</div>
                                    <div class="message-content">
                                        <strong>Assistant</strong><br>
                                        {full_response}
                                        <div class="timestamp">{timestamp}</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Small delay for visual effect
                            time.sleep(0.01)
                
                # Add assistant message to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response.strip(),
                    "timestamp": timestamp
                })
                
            else:
                error_message = f"Error: {response.status_code} - {response.text}"
                with assistant_message.container():
                    st.error(error_message)
                
        except requests.exceptions.RequestException as e:
            error_message = f"Connection error: {str(e)}"
            with assistant_message.container():
                st.error(error_message)
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            with assistant_message.container():
                st.error(error_message)

# Footer
st.markdown("---")
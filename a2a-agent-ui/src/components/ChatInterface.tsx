'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Container,
  Header,
  SpaceBetween,
  Button,
  Textarea,
  Box,
  Alert,
  StatusIndicator,
  ExpandableSection,
} from '@cloudscape-design/components';
import { apiService } from '@/services/api';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  remoteAgent?: string;
  task?: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentRemoteAgent, setCurrentRemoteAgent] = useState<string>('');
  const [currentTask, setCurrentTask] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const cancelStreamRef = useRef<(() => void) | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  const addMessage = (type: Message['type'], content: string, remoteAgent?: string, task?: string) => {
    const newMessage: Message = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      content,
      timestamp: new Date(),
      remoteAgent,
      task,
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  };

  const updateLastMessage = (newContent: string, remoteAgent?: string, task?: string) => {
    setMessages(prev => {
      const newMessages = [...prev];
      if (newMessages.length > 0 && newMessages[newMessages.length - 1].type === 'assistant') {
        // Append new content to existing content and update remote agent/task if provided
        const lastMessage = newMessages[newMessages.length - 1];
        newMessages[newMessages.length - 1] = {
          ...lastMessage,
          content: lastMessage.content + newContent,
          remoteAgent: remoteAgent || lastMessage.remoteAgent,
          task: task || lastMessage.task,
        };
      }
      return newMessages;
    });
  };

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);
    
    // Reset current remote agent and task
    setCurrentRemoteAgent('');
    setCurrentTask('');

    // Add user message
    addMessage('user', userMessage);

    // Add empty assistant message that will be updated with streaming content
    const assistantMessageId = addMessage('assistant', '');

    setIsStreaming(true);

    try {
      const cancelStream = await apiService.invokeStream(
        { query: userMessage },
        (data) => {
          if (data.type === 'stream' && data.content) {
            updateLastMessage(data.content);
          } else if (data.type === 'current_tool_use' && data.content) {
            setCurrentRemoteAgent(data.content);
            // Update the last assistant message with the new remote agent info
            // We need to get the current task from the message state, not from currentTask state
            setMessages(prev => {
              const newMessages = [...prev];
              if (newMessages.length > 0 && newMessages[newMessages.length - 1].type === 'assistant') {
                const lastMessage = newMessages[newMessages.length - 1];
                newMessages[newMessages.length - 1] = {
                  ...lastMessage,
                  remoteAgent: data.content,
                };
              }
              return newMessages;
            });
          } else if (data.type === 'current_tool_use_input' && data.content) {
            setCurrentTask(data.content);
            // Update the last assistant message with the new task info
            // We need to get the current remote agent from the message state, not from currentRemoteAgent state
            setMessages(prev => {
              const newMessages = [...prev];
              if (newMessages.length > 0 && newMessages[newMessages.length - 1].type === 'assistant') {
                const lastMessage = newMessages[newMessages.length - 1];
                newMessages[newMessages.length - 1] = {
                  ...lastMessage,
                  task: data.content,
                };
              }
              return newMessages;
            });
          } else if (data.type === 'error') {
            setError(data.content || 'An error occurred during streaming');
          } else if (data.type === 'complete') {
            setIsStreaming(false);
          }
        },
        (error) => {
          setError(error.message);
          setIsStreaming(false);
        },
        () => {
          setIsStreaming(false);
        }
      );

      cancelStreamRef.current = cancelStream;
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to send message');
      setIsStreaming(false);
    }
  };

  const handleStop = () => {
    if (cancelStreamRef.current) {
      cancelStreamRef.current();
      cancelStreamRef.current = null;
    }
    setIsStreaming(false);
    setCurrentRemoteAgent('');
    setCurrentTask('');
  };

  const handleKeyPress = (event: any) => {
    if (event.detail?.key === 'Enter' && !event.detail?.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Container
      header={
        <Header
          variant="h1"
          description="Chat with your remote agents through the Lead Agent"
          actions={
            <SpaceBetween direction="horizontal" size="xs">
              <StatusIndicator type={isStreaming ? "loading" : "success"}>
                {isStreaming ? "Streaming..." : "Ready"}
              </StatusIndicator>
              {messages.length > 0 && (
                <Button onClick={() => {
                  setMessages([]);
                  setCurrentRemoteAgent('');
                  setCurrentTask('');
                }}>
                  Clear Chat
                </Button>
              )}
            </SpaceBetween>
          }
        >
          Chat Interface
        </Header>
      }
    >
      <SpaceBetween direction="vertical" size="l">
        {error && (
          <Alert
            statusIconAriaLabel="Error"
            type="error"
            header="Error"
            dismissible
            onDismiss={() => setError(null)}
          >
            {error}
          </Alert>
        )}

        {/* Messages Area */}
        <Box>
          <div style={{ 
            height: '600px', 
            overflowY: 'auto', 
            border: '1px solid #e9ebed', 
            borderRadius: '8px',
            padding: '16px',
            backgroundColor: '#fafbfc'
          }}>
            {messages.length === 0 ? (
              <Box textAlign="center" color="text-body-secondary" padding="xl">
                <SpaceBetween direction="vertical" size="m">
                  <Box fontSize="heading-m">👋 Welcome to the Chat Interface</Box>
                  <Box>Start a conversation with your remote agents. They will work together through the Lead Agent to help you.</Box>
                </SpaceBetween>
              </Box>
            ) : (
              <SpaceBetween direction="vertical" size="m">
                {messages.map((message) => (
                  <div key={message.id}>
                    <div
                      style={{
                        padding: '12px',
                        backgroundColor: message.type === 'user' ? '#232f3e' : '#ffffff',
                        color: message.type === 'user' ? '#ffffff' : '#000000',
                        borderRadius: '8px',
                        marginLeft: message.type === 'user' ? '48px' : '0',
                        marginRight: message.type === 'user' ? '0' : '48px',
                        border: message.type === 'user' ? 'none' : '1px solid #e9ebed'
                      }}
                    >
                      <SpaceBetween direction="vertical" size="xs">
                        {message.type === 'user' ? (
                          <div
                            style={{
                              fontSize: '12px',
                              color: '#ffffff',
                              opacity: 0.9
                            }}
                          >
                            You • {formatTime(message.timestamp)}
                          </div>
                        ) : (
                          <Box
                            fontSize="body-s"
                            color="text-body-secondary"
                          >
                            Assistant • {formatTime(message.timestamp)}
                          </Box>
                        )}
                        <div style={{ whiteSpace: 'pre-wrap' }}>
                          {message.content || (message.type === 'assistant' && isStreaming ? '...' : '')}
                        </div>
                        {message.type === 'assistant' && (message.remoteAgent || message.task) && (
                          <ExpandableSection
                            headerText="Trace"
                            variant="footer"
                          >
                            <Box padding="s" color="text-status-info">
                              remote_agent: {message.remoteAgent || 'N/A'}, input: {JSON.stringify(message.task) || 'N/A'}
                            </Box>
                          </ExpandableSection>
                        )}
                      </SpaceBetween>
                    </div>
                  </div>
                ))}
              </SpaceBetween>
            )}
            <div ref={messagesEndRef} />
          </div>
        </Box>

        {/* Input Area */}
        <SpaceBetween direction="vertical" size="s">
          <Textarea
            value={input}
            onChange={({ detail }) => setInput(detail.value)}
            placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
            rows={3}
            disabled={isStreaming}
            onKeyDown={handleKeyPress}
          />
          <Box float="right">
            <SpaceBetween direction="horizontal" size="xs">
              {isStreaming && (
                <Button onClick={handleStop}>
                  Stop
                </Button>
              )}
              <Button
                variant="primary"
                onClick={handleSend}
                disabled={!input.trim() || isStreaming}
              >
                {isStreaming ? 'Sending...' : 'Send'}
              </Button>
            </SpaceBetween>
          </Box>
        </SpaceBetween>
      </SpaceBetween>
    </Container>
  );
}
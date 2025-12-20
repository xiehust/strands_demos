import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { chatApi } from '../services/chat';
import { agentsApi } from '../services/agents';
import { Button } from '../components/common/Button';
import type { ChatResponse, Agent } from '../types';

interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  thinking?: string[];
  timestamp: string;
}

export function ChatPage() {
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');
  const [conversationId, setConversationId] = useState<string>('');
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');

  // Load available agents
  const { data: agents, isLoading: agentsLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: agentsApi.list,
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: chatApi.sendMessage,
    onSuccess: (response: ChatResponse) => {
      // Update conversation ID if it's a new conversation
      if (!conversationId) {
        setConversationId(response.conversationId);
      }

      // Add assistant's response to messages
      const assistantMessage: ConversationMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        thinking: response.thinking,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    },
    onError: (error) => {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    },
  });

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !selectedAgentId) {
      return;
    }

    // Add user message to UI immediately
    const userMessage: ConversationMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Send to API
    sendMessageMutation.mutate({
      agentId: selectedAgentId,
      message: inputMessage,
      conversationId: conversationId || undefined,
    });

    // Clear input
    setInputMessage('');
  };

  const handleNewChat = () => {
    setConversationId('');
    setMessages([]);
    setInputMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex h-full">
      {/* Conversations Sidebar */}
      <div className="w-72 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-lg font-semibold mb-4">Conversations</h2>
          <Button className="w-full" onClick={handleNewChat}>
            <span className="material-symbols-outlined text-lg">add</span>
            New Chat
          </Button>
        </div>

        {/* Agent Selection */}
        <div className="p-4 border-b border-gray-800">
          <label className="block text-sm font-medium mb-2">Select Agent</label>
          {agentsLoading ? (
            <div className="text-sm text-text-muted">Loading agents...</div>
          ) : agents && agents.length > 0 ? (
            <select
              value={selectedAgentId}
              onChange={(e) => setSelectedAgentId(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 focus:outline-none focus:border-primary"
            >
              <option value="">Choose an agent...</option>
              {agents.map((agent: Agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name}
                </option>
              ))}
            </select>
          ) : (
            <div className="text-sm text-text-muted">
              No agents available. Create one first!
            </div>
          )}
        </div>

        {/* Conversation History (placeholder) */}
        <div className="flex-1 overflow-y-auto p-2">
          {conversationId ? (
            <div className="p-3 bg-primary rounded-lg">
              <div className="flex items-start gap-2">
                <span className="material-symbols-outlined text-lg">chat</span>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">Current Conversation</p>
                  <p className="text-sm opacity-70 mt-0.5">{messages.length} messages</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-sm text-text-muted text-center p-4">
              No active conversation
            </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-800">
          <button className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
            <span className="material-symbols-outlined">settings</span>
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-primary">smart_toy</span>
            <h1 className="text-xl font-semibold">
              {selectedAgentId
                ? `Chat with ${agents?.find((a: Agent) => a.id === selectedAgentId)?.name || 'Agent'}`
                : 'Select an agent to start chatting'}
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
              <span className="material-symbols-outlined">code</span>
            </button>
            <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
              <span className="material-symbols-outlined">account_circle</span>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <span className="material-symbols-outlined text-6xl text-text-muted mb-4 block">
                  chat_bubble_outline
                </span>
                <p className="text-text-muted text-lg">
                  {selectedAgentId
                    ? 'Start a conversation by typing a message below'
                    : 'Select an agent to begin'}
                </p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center">
                  <span className="material-symbols-outlined">
                    {message.role === 'user' ? 'person' : 'smart_toy'}
                  </span>
                </div>
                <div className="flex-1">
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="font-semibold">
                      {message.role === 'user' ? 'You' : 'AI Agent'}
                    </span>
                    <span className="text-sm text-text-muted">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>

                  {/* Thinking Block */}
                  {message.thinking && message.thinking.length > 0 && (
                    <div className="mb-3 p-3 bg-gray-800 rounded-lg border border-gray-700">
                      <div className="flex items-center gap-2 text-sm text-text-muted mb-2">
                        <span className="material-symbols-outlined text-base">psychology</span>
                        <span className="font-medium">Thinking...</span>
                      </div>
                      <div className="space-y-2">
                        {message.thinking.map((thought, idx) => (
                          <p key={idx} className="text-sm italic text-gray-300">
                            {thought}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Message Content */}
                  <div className="prose prose-invert max-w-none">
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              </div>
            ))
          )}

          {/* Loading Indicator */}
          {sendMessageMutation.isPending && (
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center">
                <span className="material-symbols-outlined">smart_toy</span>
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 text-text-muted">
                  <span className="material-symbols-outlined animate-spin">progress_activity</span>
                  <span>AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-gray-800">
          <div className="flex gap-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={!selectedAgentId || sendMessageMutation.isPending}
              placeholder={
                selectedAgentId
                  ? 'Type your message...'
                  : 'Select an agent first...'
              }
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              disabled
              className="p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors opacity-50 cursor-not-allowed"
              title="File upload coming soon"
            >
              <span className="material-symbols-outlined">attach_file</span>
            </button>
            <Button
              size="lg"
              onClick={handleSendMessage}
              disabled={!selectedAgentId || !inputMessage.trim() || sendMessageMutation.isPending}
            >
              <span className="material-symbols-outlined">send</span>
            </Button>
          </div>
          <div className="mt-3 text-xs text-text-muted text-center">
            {selectedAgentId && agents?.find((a: Agent) => a.id === selectedAgentId) && (
              <span>
                Model: {agents.find((a: Agent) => a.id === selectedAgentId)?.modelId.split('.').pop() || 'Unknown'} •
                Skills: {agents.find((a: Agent) => a.id === selectedAgentId)?.skillIds.length || 0} enabled
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

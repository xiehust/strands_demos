import { useState, useRef, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import clsx from 'clsx';
import type { Message, ContentBlock, StreamEvent, AskUserQuestion as AskUserQuestionType, ChatSession } from '../types';
import { chatService } from '../services/chat';
import { agentsService } from '../services/agents';
import { skillsService } from '../services/skills';
import { mcpService } from '../services/mcp';
import { Spinner, ReadOnlyChips, AskUserQuestion, Dropdown, MarkdownRenderer, ConfirmDialog } from '../components/common';

// Pending question state
interface PendingQuestion {
  toolUseId: string;
  questions: AskUserQuestionType[];
}

export default function ChatPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [pendingQuestion, setPendingQuestion] = useState<PendingQuestion | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [deleteConfirmSession, setDeleteConfirmSession] = useState<ChatSession | null>(null);

  // Fetch agents list
  const { data: agents = [], isLoading: isLoadingAgents } = useQuery({
    queryKey: ['agents'],
    queryFn: agentsService.list,
  });

  // Fetch skills list
  const { data: skills = [], isLoading: isLoadingSkills } = useQuery({
    queryKey: ['skills'],
    queryFn: skillsService.list,
  });

  // Fetch MCP servers list
  const { data: mcpServers = [], isLoading: isLoadingMCPs } = useQuery({
    queryKey: ['mcpServers'],
    queryFn: mcpService.list,
  });

  // Fetch chat sessions for the selected agent
  const { data: sessions = [], refetch: refetchSessions } = useQuery({
    queryKey: ['chatSessions', selectedAgentId],
    queryFn: () => chatService.listSessions(selectedAgentId || undefined),
    enabled: !!selectedAgentId,
  });

  // Get the selected agent object
  const selectedAgent = agents.find((a) => a.id === selectedAgentId);

  // Get configured skills for selected agent
  const agentSkills = selectedAgent?.skillIds
    ? skills.filter((s) => selectedAgent.skillIds.includes(s.id))
    : [];

  // Get configured MCPs for selected agent
  const agentMCPs = selectedAgent?.mcpIds
    ? mcpServers.filter((m) => selectedAgent.mcpIds.includes(m.id))
    : [];

  // Determine if skills and MCPs should be enabled based on agent config
  const enableSkills = agentSkills.length > 0;
  const enableMCP = agentMCPs.length > 0;

  // Load session messages
  const loadSessionMessages = useCallback(async (sid: string) => {
    setIsLoadingHistory(true);
    try {
      const sessionMessages = await chatService.getSessionMessages(sid);
      // Convert to Message format
      const formattedMessages: Message[] = sessionMessages.map((msg) => ({
        id: msg.id,
        role: msg.role as 'user' | 'assistant',
        content: msg.content as ContentBlock[],
        timestamp: msg.createdAt,
        model: msg.model,
      }));
      setMessages(formattedMessages);
      setSessionId(sid);
      setPendingQuestion(null);
    } catch (error) {
      console.error('Failed to load session messages:', error);
    } finally {
      setIsLoadingHistory(false);
    }
  }, []);

  // Handle session selection from history
  const handleSelectSession = useCallback(async (session: ChatSession) => {
    // Set the agent for this session
    if (session.agentId && session.agentId !== selectedAgentId) {
      setSelectedAgentId(session.agentId);
    }
    await loadSessionMessages(session.id);
  }, [selectedAgentId, loadSessionMessages]);

  // Handle new chat
  const handleNewChat = useCallback(() => {
    setMessages([]);
    setSessionId(undefined);
    setPendingQuestion(null);
    if (selectedAgent) {
      // Add welcome message
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: [
            {
              type: 'text',
              text: `Hello, I'm ${selectedAgent.name}. ${selectedAgent.description || 'How can I assist you today?'}`,
            },
          ],
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  }, [selectedAgent]);

  // Handle delete session
  const handleDeleteSession = async (session: ChatSession) => {
    try {
      await chatService.deleteSession(session.id);
      refetchSessions();
      // If deleted the current session, start a new chat
      if (sessionId === session.id) {
        handleNewChat();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
    setDeleteConfirmSession(null);
  };

  // Handle URL parameter for agent selection
  useEffect(() => {
    const agentIdFromUrl = searchParams.get('agentId');
    if (agentIdFromUrl && agents.length > 0) {
      const agent = agents.find((a) => a.id === agentIdFromUrl);
      if (agent && selectedAgentId !== agentIdFromUrl) {
        setSelectedAgentId(agentIdFromUrl);
        // Initialize chat with welcome message
        setMessages([
          {
            id: '1',
            role: 'assistant',
            content: [
              {
                type: 'text',
                text: `Hello, I'm ${agent.name}. ${agent.description || 'How can I assist you today?'}`,
              },
            ],
            timestamp: new Date().toISOString(),
          },
        ]);
        setSessionId(undefined);
        // Clear the URL parameter after processing
        setSearchParams({});
      }
    }
  }, [agents, searchParams, selectedAgentId, setSearchParams]);

  // Refetch sessions when conversation completes
  useEffect(() => {
    if (sessionId && !isStreaming) {
      refetchSessions();
    }
  }, [sessionId, isStreaming, refetchSessions]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<(() => void) | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isStreaming || !selectedAgentId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: [{ type: 'text', text: inputValue }],
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsStreaming(true);

    // Create a placeholder for streaming response
    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: [],
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    // Start streaming
    const abort = chatService.streamChat(
      {
        agentId: selectedAgentId,
        message: inputValue,
        sessionId,
        enableSkills,
        enableMCP,
      },
      (event: StreamEvent) => {
        // Handle session_start event to get session_id early for stop functionality
        if (event.type === 'session_start' && event.sessionId) {
          setSessionId(event.sessionId);
        } else if (event.type === 'assistant' && event.content) {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: [...msg.content, ...event.content!], model: event.model }
                : msg
            )
          );
        } else if (event.type === 'ask_user_question' && event.questions && event.toolUseId) {
          // Store pending question for user to answer
          setPendingQuestion({
            toolUseId: event.toolUseId,
            questions: event.questions,
          });
          // Set session ID from the event if available
          if (event.sessionId) {
            setSessionId(event.sessionId);
          }
          // Add question to messages as a content block
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: [
                      ...msg.content,
                      {
                        type: 'ask_user_question' as const,
                        toolUseId: event.toolUseId!,
                        questions: event.questions!,
                      },
                    ],
                  }
                : msg
            )
          );
          setIsStreaming(false);
        } else if (event.type === 'result') {
          if (event.sessionId) {
            setSessionId(event.sessionId);
          }
        } else if (event.type === 'error') {
          const errorMsg = event.message || event.error || event.detail || 'An unknown error occurred';
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: [{ type: 'text', text: `Error: ${errorMsg}` }],
                  }
                : msg
            )
          );
        }
      },
      (error) => {
        console.error('Stream error:', error);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? {
                  ...msg,
                  content: [{ type: 'text', text: `Connection error: ${error.message}` }],
                }
              : msg
          )
        );
        setIsStreaming(false);
      },
      () => {
        setIsStreaming(false);
      }
    );

    abortRef.current = abort;
  };

  // Handle answering AskUserQuestion
  const handleAnswerQuestion = (toolUseId: string, answers: Record<string, string>) => {
    if (!selectedAgentId || !sessionId) return;

    setPendingQuestion(null);
    setIsStreaming(true);

    // Create assistant message placeholder for continued response
    const assistantMessageId = Date.now().toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: [],
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    const abort = chatService.streamAnswerQuestion(
      {
        agentId: selectedAgentId,
        sessionId,
        toolUseId,
        answers,
        enableSkills,
        enableMCP,
      },
      (event: StreamEvent) => {
        // Handle session_start event to get session_id early for stop functionality
        if (event.type === 'session_start' && event.sessionId) {
          setSessionId(event.sessionId);
        } else if (event.type === 'assistant' && event.content) {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: [...msg.content, ...event.content!], model: event.model }
                : msg
            )
          );
        } else if (event.type === 'ask_user_question' && event.questions && event.toolUseId) {
          setPendingQuestion({
            toolUseId: event.toolUseId,
            questions: event.questions,
          });
          // Set session ID from the event if available
          if (event.sessionId) {
            setSessionId(event.sessionId);
          }
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: [
                      ...msg.content,
                      {
                        type: 'ask_user_question' as const,
                        toolUseId: event.toolUseId!,
                        questions: event.questions!,
                      },
                    ],
                  }
                : msg
            )
          );
          setIsStreaming(false);
        } else if (event.type === 'result') {
          if (event.sessionId) {
            setSessionId(event.sessionId);
          }
        } else if (event.type === 'error') {
          const errorMsg = event.message || event.error || event.detail || 'An unknown error occurred';
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: [{ type: 'text', text: `Error: ${errorMsg}` }] }
                : msg
            )
          );
        }
      },
      (error) => {
        console.error('Stream error:', error);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, content: [{ type: 'text', text: `Connection error: ${error.message}` }] }
              : msg
          )
        );
        setIsStreaming(false);
      },
      () => {
        setIsStreaming(false);
      }
    );

    abortRef.current = abort;
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle stop button
  const handleStop = async () => {
    if (!sessionId) return;

    try {
      // Abort the current stream if there's an abort function
      if (abortRef.current) {
        abortRef.current();
        abortRef.current = null;
      }

      // Call the backend to interrupt the session
      await chatService.stopSession(sessionId);

      // Add a system message indicating the stop
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: [{ type: 'text', text: '⏹️ Generation stopped by user.' }],
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (error) {
      console.error('Failed to stop session:', error);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleSelectAgent = (agentId: string) => {
    const agent = agents.find((a) => a.id === agentId);
    if (!agent) return;

    setSelectedAgentId(agentId);
    // Reset chat state when switching agents
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: [
          {
            type: 'text',
            text: `Hello, I'm ${agent.name}. ${agent.description || 'How can I assist you today?'}`,
          },
        ],
        timestamp: new Date().toISOString(),
      },
    ]);
    setSessionId(undefined);
  };

  // Format timestamp for display
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="flex h-full">
      {/* Chat History Sidebar */}
      <div className="w-64 bg-dark-card border-r border-dark-border flex flex-col">
        {/* Agent Selector */}
        <div className="p-3 border-b border-dark-border">
          {isLoadingAgents ? (
            <div className="flex items-center justify-center py-3">
              <Spinner size="sm" />
            </div>
          ) : agents.length === 0 ? (
            <div className="text-sm text-muted text-center py-3">
              No agents available.
              <br />
              <a href="/agents" className="text-primary hover:underline">
                Create one first
              </a>
            </div>
          ) : (
            <Dropdown
              label="Select Agent"
              placeholder="Choose an agent..."
              options={agents.map((agent) => ({
                id: agent.id,
                name: agent.name,
                description: agent.description,
              }))}
              selectedId={selectedAgentId}
              onChange={handleSelectAgent}
            />
          )}
        </div>

        {/* Header with New Chat button */}
        <div className="p-3 border-b border-dark-border">
          <button
            onClick={handleNewChat}
            disabled={!selectedAgentId}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            <span className="material-symbols-outlined text-xl">add</span>
            New Chat
          </button>
        </div>

        {/* Chat History List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          <p className="px-3 py-2 text-xs font-medium text-muted uppercase tracking-wider">Recent Chats</p>
          {sessions.length === 0 ? (
            <p className="px-3 py-2 text-xs text-muted">No chat history yet</p>
          ) : (
            sessions.map((session) => {
              const agentForSession = agents.find((a) => a.id === session.agentId);
              return (
                <div
                  key={session.id}
                  className={clsx(
                    'group w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-left transition-colors cursor-pointer',
                    sessionId === session.id
                      ? 'bg-primary text-white'
                      : 'text-muted hover:bg-dark-hover hover:text-white'
                  )}
                  onClick={() => handleSelectSession(session)}
                >
                  <span className="material-symbols-outlined text-lg flex-shrink-0">chat_bubble_outline</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{session.title}</p>
                    <p className="text-xs opacity-70">
                      {agentForSession?.name || 'Unknown'} • {formatTimestamp(session.lastAccessedAt)}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setDeleteConfirmSession(session);
                    }}
                    className={clsx(
                      'p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity',
                      sessionId === session.id
                        ? 'hover:bg-white/20 text-white'
                        : 'hover:bg-dark-border text-muted hover:text-white'
                    )}
                  >
                    <span className="material-symbols-outlined text-sm">delete</span>
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!deleteConfirmSession}
        title="Delete Chat"
        message={`Are you sure you want to delete "${deleteConfirmSession?.title}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
        onConfirm={() => deleteConfirmSession && handleDeleteSession(deleteConfirmSession)}
        onClose={() => setDeleteConfirmSession(null)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="h-16 px-6 flex items-center justify-between border-b border-dark-border">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-primary">smart_toy</span>
            <div>
              <h1 className="font-semibold text-white">
                {selectedAgent ? selectedAgent.name : 'Select an Agent'}
              </h1>
              {selectedAgent && (
                <p className="text-xs text-muted">{selectedAgent.description || 'AI Assistant'}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {selectedAgent && (
              <span className="px-2 py-1 text-xs bg-dark-hover text-muted rounded">
                {selectedAgent.model || 'Default Model'}
              </span>
            )}
            <button className="p-2 rounded-lg text-muted hover:bg-dark-hover hover:text-white transition-colors">
              <span className="material-symbols-outlined">settings</span>
            </button>
          </div>
        </div>

        {/* Messages or Empty State */}
        {!selectedAgentId ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <span className="material-symbols-outlined text-6xl text-muted mb-4">smart_toy</span>
              <h2 className="text-xl font-semibold text-white mb-2">Select an Agent to Start</h2>
              <p className="text-muted max-w-md">
                Choose an agent from the dropdown on the left to begin chatting.
                Each agent has unique capabilities and configurations.
              </p>
              {agents.length === 0 && !isLoadingAgents && (
                <a
                  href="/agents"
                  className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg transition-colors"
                >
                  <span className="material-symbols-outlined">add</span>
                  Create Your First Agent
                </a>
              )}
            </div>
          </div>
        ) : isLoadingHistory ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <Spinner size="lg" />
              <p className="text-muted mt-4">Loading conversation history...</p>
            </div>
          </div>
        ) : (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  onAnswerQuestion={handleAnswerQuestion}
                  pendingToolUseId={pendingQuestion?.toolUseId}
                  isStreaming={isStreaming}
                />
              ))}
              {isStreaming && (
                <div className="flex items-center gap-2 text-muted">
                  <Spinner size="sm" />
                  <span className="text-sm">AI is thinking...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-6 border-t border-dark-border">
              <div className="relative">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message, or upload an image..."
                  rows={1}
                  className="w-full px-4 py-3 pr-12 bg-dark-card border border-dark-border rounded-xl text-white placeholder:text-muted resize-none focus:outline-none focus:border-primary transition-colors"
                />
                <button
                  onClick={isStreaming ? handleStop : handleSendMessage}
                  disabled={!isStreaming && (!inputValue.trim() || !selectedAgentId)}
                  className={`absolute right-3 top-1/2 -translate-y-1/2 p-2 ${
                    isStreaming
                      ? 'bg-red-500 hover:bg-red-600'
                      : 'bg-primary hover:bg-primary-hover'
                  } disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center justify-center min-w-[36px] min-h-[36px]`}
                  title={isStreaming ? 'Stop generation' : 'Send message'}
                >
                  {isStreaming ? (
                    <span className="material-symbols-outlined text-white">stop</span>
                  ) : (
                    <span className="material-symbols-outlined text-white">arrow_upward</span>
                  )}
                </button>
              </div>

              {/* Agent Config Display */}
              <div className="flex items-center gap-6 mt-4">
                <button className="p-2 rounded-lg text-muted hover:bg-dark-hover hover:text-white transition-colors">
                  <span className="material-symbols-outlined">attach_file</span>
                </button>

                <ReadOnlyChips
                  label="Skills"
                  icon="extension"
                  items={agentSkills.map((s) => ({
                    id: s.id,
                    name: s.name,
                    description: s.description,
                  }))}
                  emptyText="No skills"
                  loading={isLoadingSkills}
                />

                <ReadOnlyChips
                  label="MCPs"
                  icon="hub"
                  items={agentMCPs.map((m) => ({
                    id: m.id,
                    name: m.name,
                    description: m.description,
                  }))}
                  emptyText="No MCPs"
                  loading={isLoadingMCPs}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// Message Bubble Component
interface MessageBubbleProps {
  message: Message;
  onAnswerQuestion?: (toolUseId: string, answers: Record<string, string>) => void;
  pendingToolUseId?: string;
  isStreaming?: boolean;
}

function MessageBubble({ message, onAnswerQuestion, pendingToolUseId, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={clsx('flex gap-4', isUser && 'flex-row-reverse')}>
      <div
        className={clsx(
          'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0',
          isUser ? 'bg-orange-500/20' : 'bg-dark-card'
        )}
      >
        <span className={clsx('material-symbols-outlined', isUser ? 'text-orange-400' : 'text-primary')}>
          {isUser ? 'person' : 'smart_toy'}
        </span>
      </div>

      <div className={clsx('flex-1 max-w-3xl', isUser && 'text-right')}>
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-white">{isUser ? 'User' : 'AI Agent'}</span>
          <span className="text-xs text-muted">
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        <div className={clsx('space-y-3', isUser && 'inline-block text-left')}>
          {message.content.map((block, index) => (
            <ContentBlockRenderer
              key={index}
              block={block}
              onAnswerQuestion={onAnswerQuestion}
              pendingToolUseId={pendingToolUseId}
              isStreaming={isStreaming}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// Content Block Renderer
interface ContentBlockRendererProps {
  block: ContentBlock;
  onAnswerQuestion?: (toolUseId: string, answers: Record<string, string>) => void;
  pendingToolUseId?: string;
  isStreaming?: boolean;
}

function ContentBlockRenderer({ block, onAnswerQuestion, pendingToolUseId, isStreaming }: ContentBlockRendererProps) {
  if (block.type === 'text') {
    return <MarkdownRenderer content={block.text || ''} />;
  }

  if (block.type === 'tool_use') {
    return (
      <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden">
        <div className="flex items-center justify-between px-4 py-2 bg-dark-hover">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-sm">terminal</span>
            <span className="text-sm font-medium text-white">Tool Call: {block.name}</span>
          </div>
          <span className="text-xs text-status-online">Success</span>
        </div>
        <div className="p-4 relative">
          <button className="absolute top-2 right-2 flex items-center gap-1 px-2 py-1 text-xs text-muted hover:text-white bg-dark-hover rounded transition-colors">
            <span className="material-symbols-outlined text-sm">content_copy</span>
            Copy
          </button>
          <pre className="text-sm text-muted overflow-x-auto">
            <code>{JSON.stringify(block.input, null, 2)}</code>
          </pre>
        </div>
      </div>
    );
  }

  if (block.type === 'tool_result') {
    return (
      <div className="bg-dark-card border border-dark-border rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="material-symbols-outlined text-status-online text-sm">check_circle</span>
          <span className="text-sm font-medium text-white">Tool Result</span>
        </div>
        <pre className="text-sm text-muted overflow-x-auto">
          <code>{block.content}</code>
        </pre>
      </div>
    );
  }

  if (block.type === 'ask_user_question') {
    const isPending = pendingToolUseId === block.toolUseId;
    const isAnswered = !isPending && !isStreaming;

    return (
      <AskUserQuestion
        questions={block.questions}
        toolUseId={block.toolUseId}
        onSubmit={onAnswerQuestion || (() => {})}
        disabled={isAnswered || isStreaming}
      />
    );
  }

  return null;
}

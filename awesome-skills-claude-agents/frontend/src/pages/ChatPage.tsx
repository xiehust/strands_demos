import { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import type { Message, ContentBlock, StreamEvent } from '../types';
import { chatService } from '../services/chat';
import { Spinner } from '../components/common';

// Chat history sidebar item
interface ChatHistoryItem {
  id: string;
  title: string;
  timestamp: string;
  isActive?: boolean;
}

// Mock chat history for demo
const mockChatHistory: ChatHistoryItem[] = [
  { id: '1', title: 'Python script for data analysis', timestamp: '10:30 AM', isActive: true },
  { id: '2', title: 'Image generation prompt', timestamp: 'Yesterday' },
  { id: '3', title: 'Summarize Q3 report', timestamp: 'Yesterday' },
  { id: '4', title: 'Translate this email', timestamp: '2 days ago' },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: [
        {
          type: 'text',
          text: "Hello, I'm your AI Agent. How can I assist you today? You can ask me questions, upload images, or enable Skills for advanced tasks.",
        },
      ],
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [enableSkills, setEnableSkills] = useState(false);
  const [enableMCP, setEnableMCP] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [chatHistory, setChatHistory] = useState(mockChatHistory);
  const [activeChat, setActiveChat] = useState('1');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<(() => void) | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isStreaming) return;

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
        agentId: 'default',
        message: inputValue,
        sessionId,
        enableSkills,
        enableMCP,
      },
      (event: StreamEvent) => {
        if (event.type === 'assistant' && event.content) {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: [...msg.content, ...event.content!], model: event.model }
                : msg
            )
          );
        } else if (event.type === 'result') {
          if (event.sessionId) {
            setSessionId(event.sessionId);
          }
        } else if (event.type === 'error') {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: [{ type: 'text', text: `Error: ${event.error}` }],
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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewChat = () => {
    const newId = Date.now().toString();
    setChatHistory((prev) => [
      { id: newId, title: 'New Chat', timestamp: 'Just now', isActive: true },
      ...prev.map((item) => ({ ...item, isActive: false })),
    ]);
    setActiveChat(newId);
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: [
          {
            type: 'text',
            text: "Hello, I'm your AI Agent. How can I assist you today?",
          },
        ],
        timestamp: new Date().toISOString(),
      },
    ]);
    setSessionId(undefined);
  };

  return (
    <div className="flex h-full">
      {/* Chat History Sidebar */}
      <div className="w-64 bg-dark-card border-r border-dark-border flex flex-col">
        {/* Header with New Chat button */}
        <div className="p-3 border-b border-dark-border">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary hover:bg-primary-hover text-white rounded-lg transition-colors"
          >
            <span className="material-symbols-outlined text-xl">add</span>
            New Chat
          </button>
        </div>

        {/* Chat History List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          <p className="px-3 py-2 text-xs font-medium text-muted uppercase tracking-wider">Recent Chats</p>
          {chatHistory.map((chat) => (
            <button
              key={chat.id}
              onClick={() => setActiveChat(chat.id)}
              className={clsx(
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors',
                activeChat === chat.id
                  ? 'bg-primary text-white'
                  : 'text-muted hover:bg-dark-hover hover:text-white'
              )}
            >
              <span className="material-symbols-outlined text-lg">chat_bubble_outline</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{chat.title}</p>
                <p className="text-xs opacity-70">{chat.timestamp}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="h-16 px-6 flex items-center justify-between border-b border-dark-border">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-primary">smart_toy</span>
            <h1 className="font-semibold text-white">
              Agent Chat: {chatHistory.find((c) => c.id === activeChat)?.title || 'New Chat'}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 rounded-lg text-muted hover:bg-dark-hover hover:text-white transition-colors">
              <span className="material-symbols-outlined">code</span>
            </button>
            <button className="p-2 rounded-lg text-muted hover:bg-dark-hover hover:text-white transition-colors">
              <span className="material-symbols-outlined">account_circle</span>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
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
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isStreaming}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-primary hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center justify-center min-w-[36px] min-h-[36px]"
            >
              {isStreaming ? (
                <Spinner size="sm" color="#ffffff" />
              ) : (
                <span className="material-symbols-outlined text-white">arrow_upward</span>
              )}
            </button>
          </div>

          {/* Toggles */}
          <div className="flex items-center gap-6 mt-4">
            <button className="p-2 rounded-lg text-muted hover:bg-dark-hover hover:text-white transition-colors">
              <span className="material-symbols-outlined">attach_file</span>
            </button>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={enableSkills}
                onChange={(e) => setEnableSkills(e.target.checked)}
                className="w-4 h-4 rounded border-dark-border bg-dark-card text-primary focus:ring-primary"
              />
              <span className="text-sm text-muted">Enable Skills</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={enableMCP}
                onChange={(e) => setEnableMCP(e.target.checked)}
                className="w-4 h-4 rounded border-dark-border bg-dark-card text-primary focus:ring-primary"
              />
              <span className="text-sm text-muted">Enable MCP</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}

// Message Bubble Component
function MessageBubble({ message }: { message: Message }) {
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
            <ContentBlockRenderer key={index} block={block} />
          ))}
        </div>
      </div>
    </div>
  );
}

// Content Block Renderer
function ContentBlockRenderer({ block }: { block: ContentBlock }) {
  if (block.type === 'text') {
    return <p className="text-white whitespace-pre-wrap">{block.text}</p>;
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

  return null;
}

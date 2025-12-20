import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatPage from '../../pages/ChatPage';
import { chatService } from '../../services/chat';

// Mock the chat service
vi.mock('../../services/chat', () => ({
  chatService: {
    streamChat: vi.fn(),
  },
}));

describe('ChatPage', () => {
  const mockStreamChat = vi.mocked(chatService.streamChat);

  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementation
    mockStreamChat.mockImplementation((_request, onMessage, _onError, onComplete) => {
      // Simulate async streaming
      setTimeout(() => {
        onMessage({
          type: 'assistant',
          content: [{ type: 'text', text: 'Hello from the agent!' }],
          model: 'claude-sonnet-4',
        });
        setTimeout(() => {
          onMessage({
            type: 'result',
            sessionId: 'session-123',
          });
          onComplete?.();
        }, 100);
      }, 100);

      return () => {}; // Return abort function
    });
  });

  it('renders initial welcome message', () => {
    render(<ChatPage />);

    expect(screen.getByText(/Hello, I'm your AI Agent/i)).toBeInTheDocument();
  });

  it('renders chat input area', () => {
    render(<ChatPage />);

    expect(screen.getByPlaceholderText(/Type your message/i)).toBeInTheDocument();
  });

  it('renders new chat button', () => {
    render(<ChatPage />);

    expect(screen.getByRole('button', { name: /new chat/i })).toBeInTheDocument();
  });

  it('renders skills and MCP toggles', () => {
    render(<ChatPage />);

    expect(screen.getByLabelText(/enable skills/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/enable mcp/i)).toBeInTheDocument();
  });

  it('send button is disabled when input is empty', () => {
    render(<ChatPage />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    expect(input).toHaveValue('');

    // Find the send button by checking for arrow_upward icon
    const buttons = screen.getAllByRole('button');
    const sendBtn = buttons.find(btn => btn.closest('.absolute'));
    expect(sendBtn).toBeDisabled();
  });

  it('allows typing in the input field', async () => {
    const user = userEvent.setup();
    render(<ChatPage />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, 'Hello, agent!');

    expect(input).toHaveValue('Hello, agent!');
  });

  it('clears input after sending message', async () => {
    const user = userEvent.setup();
    render(<ChatPage />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, 'Test message');

    // Press Enter to send
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });

  it('displays user message after sending', async () => {
    const user = userEvent.setup();
    render(<ChatPage />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, 'Test message');
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });
  });

  it('shows loading state while streaming', async () => {
    const user = userEvent.setup();

    // Make streaming take longer
    mockStreamChat.mockImplementation((_request, onMessage, _onError, onComplete) => {
      setTimeout(() => {
        onMessage({
          type: 'assistant',
          content: [{ type: 'text', text: 'Response' }],
        });
        onComplete?.();
      }, 500);
      return () => {};
    });

    render(<ChatPage />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, 'Test');
    await user.keyboard('{Enter}');

    // Should show loading indicator
    await waitFor(() => {
      expect(screen.getByText(/AI is thinking/i)).toBeInTheDocument();
    });
  });

  it('toggles skills checkbox', async () => {
    const user = userEvent.setup();
    render(<ChatPage />);

    const skillsCheckbox = screen.getByLabelText(/enable skills/i);
    expect(skillsCheckbox).not.toBeChecked();

    await user.click(skillsCheckbox);
    expect(skillsCheckbox).toBeChecked();
  });

  it('toggles MCP checkbox', async () => {
    const user = userEvent.setup();
    render(<ChatPage />);

    const mcpCheckbox = screen.getByLabelText(/enable mcp/i);
    expect(mcpCheckbox).not.toBeChecked();

    await user.click(mcpCheckbox);
    expect(mcpCheckbox).toBeChecked();
  });

  it('creates new chat when button clicked', async () => {
    const user = userEvent.setup();
    render(<ChatPage />);

    // Send a message first
    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, 'First message');
    await user.keyboard('{Enter}');

    // Click new chat button
    const newChatButton = screen.getByRole('button', { name: /new chat/i });
    await user.click(newChatButton);

    // Should see welcome message again (fresh chat)
    await waitFor(() => {
      const welcomeMessages = screen.getAllByText(/Hello, I'm your AI Agent/i);
      expect(welcomeMessages.length).toBeGreaterThan(0);
    });
  });

  it('handles streaming error', async () => {
    const user = userEvent.setup();

    mockStreamChat.mockImplementation((_request, _onMessage, onError, _onComplete) => {
      setTimeout(() => {
        onError?.(new Error('Connection failed'));
      }, 100);
      return () => {};
    });

    render(<ChatPage />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, 'Test');
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(screen.getByText(/Connection error/i)).toBeInTheDocument();
    });
  });

  it('calls streamChat with correct parameters', async () => {
    const user = userEvent.setup();
    render(<ChatPage />);

    // Enable skills
    const skillsCheckbox = screen.getByLabelText(/enable skills/i);
    await user.click(skillsCheckbox);

    // Send message
    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, 'Hello');
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(mockStreamChat).toHaveBeenCalledWith(
        expect.objectContaining({
          agentId: 'default',
          message: 'Hello',
          enableSkills: true,
          enableMCP: false,
        }),
        expect.any(Function),
        expect.any(Function),
        expect.any(Function)
      );
    });
  });

  it('prevents sending while already streaming', async () => {
    const user = userEvent.setup();

    // Make streaming never complete
    mockStreamChat.mockImplementation((_request, _onMessage, _onError, _onComplete) => {
      return () => {};
    });

    render(<ChatPage />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, 'First message');
    await user.keyboard('{Enter}');

    // Clear and type again
    await user.type(input, 'Second message');
    await user.keyboard('{Enter}');

    // Should only have called once
    expect(mockStreamChat).toHaveBeenCalledTimes(1);
  });

  it('does not send on Shift+Enter', async () => {
    const user = userEvent.setup();
    render(<ChatPage />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, 'Test message');
    await user.keyboard('{Shift>}{Enter}{/Shift}');

    // Should not have sent the message
    expect(mockStreamChat).not.toHaveBeenCalled();
  });
});

describe('ChatPage Chat History', () => {
  it('renders chat history sidebar', () => {
    render(<ChatPage />);

    expect(screen.getByText('Recent Chats')).toBeInTheDocument();
  });

  it('displays chat history items', () => {
    render(<ChatPage />);

    // Should have mock chat history items
    expect(screen.getByText('Python script for data analysis')).toBeInTheDocument();
  });

  it('can switch between chat history items', async () => {
    const user = userEvent.setup();
    render(<ChatPage />);

    // Click on a different chat in history
    const historyItem = screen.getByText('Image generation prompt');
    await user.click(historyItem);

    // The clicked item should now be active (visually highlighted)
    const parentButton = historyItem.closest('button');
    expect(parentButton).toHaveClass('bg-primary');
  });
});

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChat } from './useChat';
import { streamChatMessage, type StreamEvent } from '../services/chat';

// Mock the chat service
vi.mock('../services/chat', () => ({
  streamChatMessage: vi.fn(),
}));

describe('useChat', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with empty messages', () => {
    const { result } = renderHook(() => useChat({ agentId: 'test-agent' }));

    expect(result.current.messages).toEqual([]);
    expect(result.current.isStreaming).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should use provided conversationId', () => {
    const { result } = renderHook(() =>
      useChat({ agentId: 'test-agent', conversationId: 'existing-conv' })
    );

    expect(result.current.conversationId).toBe('existing-conv');
  });

  it('should add user message when sending', async () => {
    // Mock streaming to complete immediately
    vi.mocked(streamChatMessage).mockImplementation(async (_, callback) => {
      callback({ type: 'start', conversationId: 'conv-123' });
      callback({ type: 'text', content: 'Hello!' });
      callback({ type: 'done' });
    });

    const { result } = renderHook(() => useChat({ agentId: 'test-agent' }));

    await act(async () => {
      await result.current.sendMessage('Hi there');
    });

    expect(result.current.messages.length).toBe(2);
    expect(result.current.messages[0]).toMatchObject({
      role: 'user',
      content: 'Hi there',
    });
  });

  it('should create assistant message on stream start', async () => {
    vi.mocked(streamChatMessage).mockImplementation(async (_, callback) => {
      callback({ type: 'start', conversationId: 'conv-123' });
      callback({ type: 'done' });
    });

    const { result } = renderHook(() => useChat({ agentId: 'test-agent' }));

    await act(async () => {
      await result.current.sendMessage('Test');
    });

    // Check that an assistant message was created
    expect(result.current.messages.length).toBe(2);
    expect(result.current.messages[1].role).toBe('assistant');
  });

  it('should handle thinking blocks', async () => {
    vi.mocked(streamChatMessage).mockImplementation(async (_, callback) => {
      callback({ type: 'start', conversationId: 'conv-123' });
      callback({ type: 'thinking', content: 'Let me think...' });
      callback({ type: 'text', content: 'Answer' });
      callback({ type: 'done' });
    });

    const { result } = renderHook(() => useChat({ agentId: 'test-agent' }));

    await act(async () => {
      await result.current.sendMessage('Question');
    });

    const assistantMessage = result.current.messages.find(m => m.role === 'assistant');
    expect(assistantMessage?.thinking).toContain('Let me think...');
  });

  it('should set error on stream error', async () => {
    vi.mocked(streamChatMessage).mockImplementation(async (_, callback) => {
      callback({ type: 'start', conversationId: 'conv-123' });
      callback({ type: 'error', error: 'Something went wrong' });
    });

    const { result } = renderHook(() => useChat({ agentId: 'test-agent' }));

    await act(async () => {
      await result.current.sendMessage('Test');
    });

    expect(result.current.error).toBe('Something went wrong');
    expect(result.current.isStreaming).toBe(false);
  });

  it('should clear messages', async () => {
    vi.mocked(streamChatMessage).mockImplementation(async (_, callback) => {
      callback({ type: 'start', conversationId: 'conv-123' });
      callback({ type: 'text', content: 'Response' });
      callback({ type: 'done' });
    });

    const { result } = renderHook(() => useChat({ agentId: 'test-agent' }));

    await act(async () => {
      await result.current.sendMessage('Hello');
    });

    expect(result.current.messages.length).toBe(2);

    act(() => {
      result.current.clearMessages();
    });

    expect(result.current.messages).toEqual([]);
    expect(result.current.error).toBeNull();
  });

  it('should not send message while streaming', async () => {
    // Mock a slow stream
    vi.mocked(streamChatMessage).mockImplementation(async (_, callback) => {
      callback({ type: 'start', conversationId: 'conv-123' });
      // Never call 'done' to simulate ongoing stream
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    const { result } = renderHook(() => useChat({ agentId: 'test-agent' }));

    // Start first message
    act(() => {
      result.current.sendMessage('First');
    });

    // Try to send second message while streaming
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

    await act(async () => {
      await result.current.sendMessage('Second');
    });

    expect(consoleSpy).toHaveBeenCalledWith('Already streaming a message');
    consoleSpy.mockRestore();
  });
});

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { ArrowLeft, Circle } from 'lucide-react';
import api from '@/services/api';
import { getSocket } from '@/services/socket';
import { useChatStore } from '@/store/chatStore';
import MessageInput from '@/components/chat/MessageInput';
import type { ChatConversation, ChatMessage } from '@/types/chat';

interface MessagePageResponse {
  messages: ChatMessage[];
  has_more: boolean;
  next_cursor: number | null;
}

function formatMessageTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatDateHeader(dateStr: string): string {
  const date = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) return 'Hoje';
  if (date.toDateString() === yesterday.toDateString()) return 'Ontem';
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' });
}

function getInitials(name: string): string {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('');
}

interface Props {
  conversation: ChatConversation;
  currentUserId: number;
  onBack: () => void;
}

export default function ChatWindow({ conversation, currentUserId, onBack }: Props) {
  const messages = useChatStore((s) => s.messages[conversation.id] ?? []);
  const setMessages = useChatStore((s) => s.setMessages);
  const prependMessages = useChatStore((s) => s.prependMessages);
  const clearUnread = useChatStore((s) => s.clearUnread);
  const typingUsers = useChatStore((s) =>
    s.typingUsers.filter((t) => t.conversation_id === conversation.id),
  );
  const onlineUsers = useChatStore((s) => s.onlineUsers);

  const [hasMore, setHasMore] = useState(false);
  const [nextCursor, setNextCursor] = useState<number | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [initialLoaded, setInitialLoaded] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const shouldAutoScroll = useRef(true);

  const other = conversation.participants.find((p) => p.user_id !== currentUserId);
  const otherName = other?.user.nome ?? 'Usuário';
  const isOnline = other ? onlineUsers.has(other.user_id) : false;

  useEffect(() => {
    setInitialLoaded(false);
    shouldAutoScroll.current = true;

    api
      .get<MessagePageResponse>(`/api/chat/conversations/${conversation.id}/messages`, {
        params: { limit: 50 },
      })
      .then((res) => {
        setMessages(conversation.id, res.data.messages);
        setHasMore(res.data.has_more);
        setNextCursor(res.data.next_cursor);
        setInitialLoaded(true);
      })
      .catch(() => {});

    clearUnread(conversation.id);
    const socket = getSocket();
    if (socket) {
      socket.emit('mark_as_read', { conversation_id: conversation.id });
    }
  }, [conversation.id, setMessages, clearUnread]);

  useEffect(() => {
    if (shouldAutoScroll.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: initialLoaded ? 'smooth' : 'auto' });
    }
  }, [messages, initialLoaded]);

  const handleScroll = useCallback(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const { scrollTop, scrollHeight, clientHeight } = container;
    shouldAutoScroll.current = scrollHeight - scrollTop - clientHeight < 100;

    if (scrollTop < 50 && hasMore && !loadingMore && nextCursor) {
      setLoadingMore(true);
      const prevScrollHeight = scrollHeight;

      api
        .get<MessagePageResponse>(`/api/chat/conversations/${conversation.id}/messages`, {
          params: { cursor: nextCursor, limit: 30 },
        })
        .then((res) => {
          prependMessages(conversation.id, res.data.messages);
          setHasMore(res.data.has_more);
          setNextCursor(res.data.next_cursor);

          requestAnimationFrame(() => {
            if (container) {
              container.scrollTop = container.scrollHeight - prevScrollHeight;
            }
          });
        })
        .catch(() => {})
        .finally(() => setLoadingMore(false));
    }
  }, [conversation.id, hasMore, loadingMore, nextCursor, prependMessages]);

  useEffect(() => {
    if (messages.length > 0) {
      const lastMsg = messages[messages.length - 1];
      if (lastMsg.sender_id !== currentUserId) {
        const socket = getSocket();
        if (socket) {
          socket.emit('mark_as_read', {
            conversation_id: conversation.id,
            message_id: lastMsg.id,
          });
        }
        clearUnread(conversation.id);
      }
    }
  }, [messages, conversation.id, currentUserId, clearUnread]);

  const handleSend = useCallback(
    (content: string) => {
      const socket = getSocket();
      if (!socket) return;
      socket.emit('send_message', {
        conversation_id: conversation.id,
        content,
      });
    },
    [conversation.id],
  );

  let lastDateStr = '';

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-gray-200 px-4 py-3">
        <button
          type="button"
          onClick={onBack}
          className="rounded-lg p-1.5 text-gray-400 transition-colors hover:bg-gray-100 md:hidden"
        >
          <ArrowLeft size={20} />
        </button>
        <div className="relative">
          {other?.user.foto_url ? (
            <img
              src={other.user.foto_url}
              alt={otherName}
              className="h-9 w-9 rounded-full object-cover"
            />
          ) : (
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-green-100 text-xs font-semibold text-green-700">
              {getInitials(otherName)}
            </span>
          )}
          {isOnline && (
            <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-white bg-green-500" />
          )}
        </div>
        <div>
          <p className="text-sm font-semibold text-gray-800">{otherName}</p>
          <p className="text-xs text-gray-400">{isOnline ? 'Online' : 'Offline'}</p>
        </div>
      </div>

      {/* Messages area */}
      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-4 py-3"
      >
        {loadingMore && (
          <div className="mb-2 text-center text-xs text-gray-400">Carregando mensagens...</div>
        )}

        {messages.map((msg) => {
          const isMine = msg.sender_id === currentUserId;
          const msgDate = new Date(msg.created_at).toDateString();
          let showDate = false;
          if (msgDate !== lastDateStr) {
            lastDateStr = msgDate;
            showDate = true;
          }

          return (
            <div key={msg.id}>
              {showDate && (
                <div className="my-3 flex items-center gap-3">
                  <div className="h-px flex-1 bg-gray-200" />
                  <span className="text-xs text-gray-400">{formatDateHeader(msg.created_at)}</span>
                  <div className="h-px flex-1 bg-gray-200" />
                </div>
              )}
              <div className={`mb-2 flex ${isMine ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[75%] rounded-2xl px-3.5 py-2 ${
                    isMine
                      ? 'rounded-br-md bg-green-500 text-white'
                      : 'rounded-bl-md bg-gray-100 text-gray-800'
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words text-sm">{msg.content}</p>
                  <p
                    className={`mt-0.5 text-right text-[10px] ${
                      isMine ? 'text-green-100' : 'text-gray-400'
                    }`}
                  >
                    {formatMessageTime(msg.created_at)}
                  </p>
                </div>
              </div>
            </div>
          );
        })}

        {typingUsers.length > 0 && (
          <div className="mb-2 flex items-center gap-2 text-xs text-gray-400">
            <span className="flex gap-0.5">
              <Circle size={4} className="animate-bounce fill-gray-400" style={{ animationDelay: '0ms' }} />
              <Circle size={4} className="animate-bounce fill-gray-400" style={{ animationDelay: '150ms' }} />
              <Circle size={4} className="animate-bounce fill-gray-400" style={{ animationDelay: '300ms' }} />
            </span>
            <span>
              {typingUsers.map((t) => t.username).join(', ')} está digitando...
            </span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Message input */}
      <MessageInput conversationId={conversation.id} onSend={handleSend} />
    </div>
  );
}

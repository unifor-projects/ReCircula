'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { ArrowDown, ArrowLeft, Circle } from 'lucide-react';
import Link from 'next/link';
import api from '@/services/api';
import { getSocket } from '@/services/socket';
import { useChatStore } from '@/store/chatStore';
import AnuncioContexto from '@/components/chat/AnuncioContexto';
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
  /** Anúncio de onde a pessoa veio (botão "Enviar mensagem"), para dar contexto */
  anuncioId?: number | null;
}

const SUGESTOES_INICIO = [
  'Oi! Ainda está disponível?',
  'Posso retirar hoje?',
  'Pode deixar no locker?',
];
const SUGESTOES_CONVERSA = ['Combinado!', 'Qual horário fica bom?', 'Deixo no locker', 'Obrigado!'];

export default function ChatWindow({ conversation, currentUserId, onBack, anuncioId }: Props) {
  const [tituloAnuncio, setTituloAnuncio] = useState<string | null>(null);
  const [showJump, setShowJump] = useState(false);
  const [novasFora, setNovasFora] = useState(0);
  // Local state — guaranteed to trigger re-renders when updated
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [nextCursor, setNextCursor] = useState<number | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [initialLoaded, setInitialLoaded] = useState(false);

  const clearUnread = useChatStore((s) => s.clearUnread);
  const allTypingUsers = useChatStore((s) => s.typingUsers);
  const typingUsers = allTypingUsers.filter((t) => t.conversation_id === conversation.id);
  const onlineUsers = useChatStore((s) => s.onlineUsers);
  // Realtime signal: updated by the global socket listener (useSocket) for every
  // incoming message. We react to it below instead of relying solely on this
  // component's own socket listener.
  const lastIncomingMessage = useChatStore((s) => s.lastIncomingMessage);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const shouldAutoScroll = useRef(true);
  // Primeira carga de cada conversa pula direto para o fim (sem animação de rolagem)
  const initialScrollDone = useRef(false);
  const conversationIdRef = useRef(conversation.id);
  conversationIdRef.current = conversation.id;

  const other = conversation.participants.find((p) => p.user_id !== currentUserId);
  const otherName = other?.user.nome ?? 'Usuário';
  const isOnline = other ? onlineUsers.has(other.user_id) : false;

  // Load initial messages and join the socket room
  useEffect(() => {
    setMessages([]);
    setInitialLoaded(false);
    shouldAutoScroll.current = true;
    initialScrollDone.current = false;
    setShowJump(false);
    setNovasFora(0);

    api
      .get<MessagePageResponse>(`/api/chat/conversations/${conversation.id}/messages`, {
        params: { limit: 50 },
      })
      .then((res) => {
        setMessages(res.data.messages);
        setHasMore(res.data.has_more);
        setNextCursor(res.data.next_cursor);
        setInitialLoaded(true);
      })
      .catch(() => {});

    clearUnread(conversation.id);

    const socket = getSocket();
    if (socket) {
      socket.emit('mark_as_read', { conversation_id: conversation.id });
      socket.emit('join_room', { conversation_id: conversation.id });
    }

    return () => {
      // Sair da sala ao desmontar. Estar na sala é o que diz ao servidor "estou
      // lendo esta conversa": enquanto o cliente ficava dentro dela mesmo depois
      // de sair de /chat, o servidor mandava `new_message` em vez de
      // `notification`, e o toast e o badge nunca apareciam.
      getSocket()?.emit('leave_room', { conversation_id: conversation.id });
    };
  }, [conversation.id, clearUnread]);

  // Merge an incoming message into local state. Idempotent: ignores duplicates
  // by id and replaces our own optimistic placeholder (temporary negative id).
  const mergeIncoming = useCallback(
    (msg: ChatMessage) => {
      if (msg.conversation_id !== conversationIdRef.current) return;
      setMessages((prev) => {
        if (prev.some((m) => m.id === msg.id)) return prev;
        let next = prev;
        if (msg.sender_id === currentUserId) {
          const idx = next.findIndex((m) => m.id < 0 && m.content === msg.content);
          if (idx !== -1) {
            next = [...next.slice(0, idx), ...next.slice(idx + 1)];
          }
        }
        return [...next, msg];
      });
      // Só desce sozinho se a mensagem é minha ou se já estou perto do fim
      if (msg.sender_id === currentUserId) {
        shouldAutoScroll.current = true;
      } else if (!shouldAutoScroll.current) {
        setNovasFora((n) => n + 1);
      }

      // Mark as read if we are the recipient
      if (msg.sender_id !== currentUserId) {
        clearUnread(msg.conversation_id);
        getSocket()?.emit('mark_as_read', {
          conversation_id: msg.conversation_id,
          message_id: msg.id,
        });
      }
    },
    [currentUserId, clearUnread],
  );

  // React to the global socket listener (useSocket) via the store signal. This
  // guarantees realtime updates even if this component's own listener below
  // wasn't attached in time (e.g. socket connected after mount).
  useEffect(() => {
    if (lastIncomingMessage) mergeIncoming(lastIncomingMessage);
  }, [lastIncomingMessage, mergeIncoming]);

  // Also listen directly to the socket as a second, immediate path.
  useEffect(() => {
    const convId = conversation.id;

    function handleNewMessage(msg: ChatMessage) {
      mergeIncoming(msg);
    }

    // Re-join room on socket reconnect so we never miss messages
    function handleConnect() {
      getSocket()?.emit('join_room', { conversation_id: convId });
    }

    const socket = getSocket();
    socket?.on('new_message', handleNewMessage);
    socket?.on('connect', handleConnect);

    return () => {
      socket?.off('new_message', handleNewMessage);
      socket?.off('connect', handleConnect);
    };
  }, [conversation.id, mergeIncoming]);

  // Auto-scroll when messages change
  useEffect(() => {
    if (!shouldAutoScroll.current || messages.length === 0) return;
    const container = messagesContainerRef.current;
    if (!initialScrollDone.current && initialLoaded && container) {
      container.scrollTop = container.scrollHeight;
      initialScrollDone.current = true;
      return;
    }
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, initialLoaded]);

  const handleScroll = useCallback(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const { scrollTop, scrollHeight, clientHeight } = container;
    const distanciaDoFim = scrollHeight - scrollTop - clientHeight;
    shouldAutoScroll.current = distanciaDoFim < 100;
    setShowJump(distanciaDoFim > 300);
    if (distanciaDoFim < 100) setNovasFora(0);

    if (scrollTop < 50 && hasMore && !loadingMore && nextCursor) {
      setLoadingMore(true);
      const prevScrollHeight = scrollHeight;

      api
        .get<MessagePageResponse>(`/api/chat/conversations/${conversation.id}/messages`, {
          params: { cursor: nextCursor, limit: 30 },
        })
        .then((res) => {
          setMessages((prev) => [...res.data.messages, ...prev]);
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
  }, [conversation.id, hasMore, loadingMore, nextCursor]);

  const handleSend = useCallback(
    (content: string) => {
      const socket = getSocket();
      if (!socket) return;

      // Optimistic update: show the message immediately with a temporary
      // negative id. The real message (with a positive id) arrives via the
      // "new_message" echo and replaces this placeholder in handleNewMessage.
      const me = conversation.participants.find((p) => p.user_id === currentUserId);
      const optimistic: ChatMessage = {
        id: -Date.now(),
        conversation_id: conversation.id,
        sender_id: currentUserId,
        content,
        created_at: new Date().toISOString(),
        sender: {
          id: currentUserId,
          nome: me?.user.nome ?? '',
          foto_url: me?.user.foto_url ?? null,
          localizacao: me?.user.localizacao ?? null,
          criado_em: me?.user.criado_em ?? new Date().toISOString(),
        },
      };
      setMessages((prev) => [...prev, optimistic]);
      shouldAutoScroll.current = true;

      socket.emit('send_message', {
        conversation_id: conversation.id,
        content,
      });
    },
    [conversation.id, currentUserId],
  );

  const GROUP_GAP_MS = 5 * 60 * 1000;
  // Mensagens seguidas da mesma pessoa (até 5 min) formam um grupo: horário só na última
  const sameGroup = (a: ChatMessage | undefined, b: ChatMessage | undefined) =>
    !!a &&
    !!b &&
    a.sender_id === b.sender_id &&
    new Date(a.created_at).toDateString() === new Date(b.created_at).toDateString() &&
    Math.abs(new Date(b.created_at).getTime() - new Date(a.created_at).getTime()) < GROUP_GAP_MS;

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-3">
        <button
          type="button"
          onClick={onBack}
          aria-label="Voltar para as conversas"
          className="-ml-1 flex h-10 w-10 items-center justify-center rounded-full text-gray-500 transition-colors hover:bg-gray-100 md:hidden"
        >
          <ArrowLeft size={20} />
        </button>
        <div className="relative">
          {other?.user.foto_url ? (
            <img
              src={other.user.foto_url}
              alt=""
              width={40}
              height={40}
              className="h-10 w-10 rounded-full object-cover"
            />
          ) : (
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100 text-sm font-semibold text-green-700">
              {getInitials(otherName)}
            </span>
          )}
          {isOnline && (
            <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white bg-green-500" />
          )}
        </div>
        <div className="min-w-0">
          {other ? (
            <Link
              href={`/perfil/${other.user_id}`}
              className="block truncate font-semibold text-gray-900 hover:underline"
            >
              {otherName}
            </Link>
          ) : (
            <p className="truncate font-semibold text-gray-900">{otherName}</p>
          )}
          <p className={`text-xs ${isOnline ? 'text-green-700' : 'text-gray-500'}`}>
            {isOnline ? 'Online agora' : 'Offline'}
          </p>
        </div>
      </div>

      {anuncioId ? <AnuncioContexto anuncioId={anuncioId} onCarregado={setTituloAnuncio} /> : null}

      {/* Messages area */}
      <div className="relative flex min-h-0 flex-1 flex-col">
        <div
          ref={messagesContainerRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto bg-gray-50 px-3 py-4 sm:px-6"
        >
          {loadingMore && (
            <div className="mb-3 text-center text-xs text-gray-500">Carregando mensagens…</div>
          )}

          {initialLoaded && messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center text-center text-sm text-gray-500">
              <p className="font-medium text-gray-700">Nenhuma mensagem ainda</p>
              <p className="mt-1">Diga oi para {otherName.split(' ')[0]} e combine a entrega.</p>
            </div>
          )}

          {messages.map((msg, i) => {
            const isMine = msg.sender_id === currentUserId;
            const prev = messages[i - 1];
            const next = messages[i + 1];
            const showDate =
              !prev ||
              new Date(prev.created_at).toDateString() !== new Date(msg.created_at).toDateString();
            const groupStart = !sameGroup(prev, msg);
            const groupEnd = !sameGroup(msg, next);
            const pending = msg.id < 0;

            // Canto de baixo do lado de quem falou fica reto; dentro de um grupo, o de cima também (balões "colados")
            const corners = isMine
              ? `rounded-2xl rounded-br-md ${groupStart ? '' : 'rounded-tr-md'}`
              : `rounded-2xl rounded-bl-md ${groupStart ? '' : 'rounded-tl-md'}`;

            return (
              <div key={msg.id}>
                {showDate && (
                  <div className="my-4 flex justify-center">
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-gray-500 shadow-sm ring-1 ring-gray-100">
                      {formatDateHeader(msg.created_at)}
                    </span>
                  </div>
                )}
                <div
                  className={`flex items-end gap-2 ${isMine ? 'justify-end' : 'justify-start'} ${groupEnd ? 'mb-3' : 'mb-0.5'}`}
                >
                  {!isMine &&
                    (groupEnd ? (
                      <span className="flex h-7 w-7 shrink-0 items-center justify-center overflow-hidden rounded-full bg-green-100 text-[10px] font-semibold text-green-700">
                        {other?.user.foto_url ? (
                          <img
                            src={other.user.foto_url}
                            alt=""
                            width={28}
                            height={28}
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          getInitials(otherName)
                        )}
                      </span>
                    ) : (
                      <span className="w-7 shrink-0" />
                    ))}
                  <div
                    className={`max-w-[80%] px-3.5 py-2 shadow-sm sm:max-w-[65%] ${corners} ${
                      isMine
                        ? 'bg-green-600 text-white'
                        : 'bg-white text-gray-900 ring-1 ring-gray-100'
                    } ${pending ? 'opacity-70' : ''}`}
                  >
                    <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">
                      {msg.content}
                    </p>
                    {groupEnd && (
                      <p
                        className={`mt-0.5 text-right text-[11px] tabular-nums ${isMine ? 'text-green-100' : 'text-gray-500'}`}
                      >
                        {pending ? 'Enviando…' : formatMessageTime(msg.created_at)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {typingUsers.length > 0 && (
            <div className="mb-3 flex items-center gap-2" aria-live="polite">
              <span className="flex gap-1 rounded-2xl rounded-bl-md bg-white px-3.5 py-3 shadow-sm ring-1 ring-gray-100">
                {[0, 150, 300].map((delay) => (
                  <Circle
                    key={delay}
                    size={6}
                    className="fill-gray-400 text-gray-400 motion-safe:animate-bounce"
                    style={{ animationDelay: `${delay}ms` }}
                  />
                ))}
              </span>
              <span className="text-xs text-gray-500">
                {typingUsers.map((t) => t.username).join(', ')} está digitando…
              </span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {showJump && (
          <button
            type="button"
            onClick={() => {
              shouldAutoScroll.current = true;
              setNovasFora(0);
              messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            }}
            aria-label="Ir para a última mensagem"
            className="absolute bottom-4 right-4 flex h-11 items-center gap-1.5 rounded-full bg-white px-3 text-sm font-medium text-gray-700 shadow-lg ring-1 ring-gray-200 transition hover:bg-gray-50"
          >
            {novasFora > 0 && (
              <span className="rounded-full bg-green-600 px-1.5 text-xs font-semibold text-white">
                {novasFora}
              </span>
            )}
            <ArrowDown size={18} aria-hidden="true" />
          </button>
        )}
      </div>

      {/* Message input */}
      <MessageInput
        key={`${conversation.id}-${tituloAnuncio ?? ''}`}
        conversationId={conversation.id}
        onSend={handleSend}
        initialText={
          tituloAnuncio ? `Oi! Tenho interesse em “${tituloAnuncio}”. Ainda está disponível?` : ''
        }
        suggestions={
          initialLoaded ? (messages.length === 0 ? SUGESTOES_INICIO : SUGESTOES_CONVERSA) : []
        }
      />
    </div>
  );
}

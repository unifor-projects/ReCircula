'use client';

import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { MessageCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useChatStore } from '@/store/chatStore';
import { getSocket } from '@/services/socket';
import api from '@/services/api';
import ConversationList from '@/components/chat/ConversationList';
import ChatWindow from '@/components/chat/ChatWindow';
import NewConversationModal from '@/components/chat/NewConversationModal';
import type { ChatConversation } from '@/types/chat';

export default function ChatPageClient() {
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const convParam = searchParams?.get('conv') ?? null;
  const anuncioParam = Number(searchParams?.get('anuncio')) || null;
  const {
    conversations,
    setConversations,
    activeConversationId,
    setActiveConversation,
    setTotalUnread,
  } = useChatStore();
  const [showNewConv, setShowNewConv] = useState(false);
  const [mobileShowChat, setMobileShowChat] = useState(false);

  useEffect(() => {
    api
      .get<ChatConversation[]>('/api/chat/conversations')
      .then((res) => {
        setConversations(res.data);
        const total = res.data.reduce((sum, c) => sum + c.unread_count, 0);
        setTotalUnread(total);
      })
      .catch(() => {});
  }, [setConversations, setTotalUnread]);

  useEffect(() => {
    if (!convParam || conversations.length === 0) return;
    const targetId = Number(convParam);
    if (!Number.isNaN(targetId) && targetId > 0) {
      handleSelectConversation(targetId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [convParam, conversations.length]);

  // Ao sair de /chat, esquecer a conversa ativa. Ela é o que o useSocket usa
  // para re-entrar na sala a cada reconexão — mantê-la faria o cliente voltar
  // para a sala mesmo com o chat fechado, suprimindo as notificações.
  useEffect(() => {
    return () => {
      useChatStore.getState().setActiveConversation(null);
    };
  }, []);

  const handleSelectConversation = useCallback(
    (id: number) => {
      const socket = getSocket();
      if (activeConversationId && socket) {
        socket.emit('leave_room', { conversation_id: activeConversationId });
      }
      setActiveConversation(id);
      setMobileShowChat(true);
      if (socket) {
        socket.emit('join_room', { conversation_id: id });
      }
    },
    [activeConversationId, setActiveConversation],
  );

  const handleBack = useCallback(() => {
    const socket = getSocket();
    if (activeConversationId && socket) {
      socket.emit('leave_room', { conversation_id: activeConversationId });
    }
    setActiveConversation(null);
    setMobileShowChat(false);
  }, [activeConversationId, setActiveConversation]);

  const handleConversationCreated = useCallback(
    (conv: ChatConversation) => {
      setConversations([conv, ...conversations.filter((c) => c.id !== conv.id)]);
      handleSelectConversation(conv.id);
      setShowNewConv(false);
    },
    [conversations, setConversations, handleSelectConversation],
  );

  const activeConversation = conversations.find((c) => c.id === activeConversationId) ?? null;

  return (
    <div className="mx-auto flex h-[calc(100dvh-4rem)] max-w-6xl overflow-hidden bg-white md:my-4 md:h-[calc(100dvh-6rem)] md:rounded-2xl md:border md:border-gray-200 md:shadow-sm">
      {/* Sidebar — hidden on mobile when chat is open */}
      <div
        className={`w-full flex-shrink-0 border-r border-gray-200 md:w-80 ${
          mobileShowChat ? 'hidden md:block' : 'block'
        }`}
      >
        <ConversationList
          conversations={conversations}
          activeId={activeConversationId}
          currentUserId={user?.id ?? 0}
          onSelect={handleSelectConversation}
          onNewConversation={() => setShowNewConv(true)}
        />
      </div>

      {/* Chat area */}
      <div className={`min-w-0 flex-1 ${!mobileShowChat ? 'hidden md:flex' : 'flex'} flex-col`}>
        {activeConversation ? (
          <ChatWindow
            conversation={activeConversation}
            currentUserId={user?.id ?? 0}
            onBack={handleBack}
            // O anúncio só vale para a conversa aberta pelo botão do anúncio
            anuncioId={String(activeConversation.id) === convParam ? anuncioParam : null}
          />
        ) : (
          <div className="flex flex-1 flex-col items-center justify-center bg-gray-50 px-6 text-center">
            <span className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-green-700">
              <MessageCircle size={28} aria-hidden="true" />
            </span>
            <p className="mt-4 font-semibold text-gray-900">Suas conversas</p>
            <p className="mt-1 max-w-xs text-sm text-gray-500">
              Escolha uma conversa ao lado para combinar a entrega de um item.
            </p>
          </div>
        )}
      </div>

      {showNewConv && (
        <NewConversationModal
          onClose={() => setShowNewConv(false)}
          onCreated={handleConversationCreated}
        />
      )}
    </div>
  );
}

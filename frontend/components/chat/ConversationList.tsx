'use client';

import { useMemo, useState } from 'react';
import { MessageSquarePlus, Search } from 'lucide-react';
import { useChatStore } from '@/store/chatStore';
import type { ChatConversation } from '@/types/chat';

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return 'U';
  return parts
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase() ?? '')
    .join('');
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / 86400000);

  if (diffDays === 0) {
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  }
  if (diffDays === 1) return 'Ontem';
  if (diffDays < 7) {
    return date.toLocaleDateString('pt-BR', { weekday: 'short' });
  }
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
}

interface Props {
  conversations: ChatConversation[];
  activeId: number | null;
  currentUserId: number;
  onSelect: (id: number) => void;
  onNewConversation: () => void;
}

export default function ConversationList({
  conversations,
  activeId,
  currentUserId,
  onSelect,
  onNewConversation,
}: Props) {
  const [search, setSearch] = useState('');
  const onlineUsers = useChatStore((s) => s.onlineUsers);

  const filtered = useMemo(() => {
    if (!search.trim()) return conversations;
    const q = search.toLowerCase();
    return conversations.filter((c) => {
      const other = c.participants.find((p) => p.user_id !== currentUserId);
      return other?.user.nome.toLowerCase().includes(q);
    });
  }, [conversations, search, currentUserId]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-gray-800">Conversas</h2>
        <button
          type="button"
          onClick={onNewConversation}
          className="rounded-lg p-2 text-green-600 transition-colors hover:bg-green-50"
          title="Nova conversa"
        >
          <MessageSquarePlus size={20} />
        </button>
      </div>

      <div className="px-3 py-2">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar conversa..."
            className="w-full rounded-lg border border-gray-200 bg-gray-50 py-2 pl-9 pr-3 text-sm text-gray-900 placeholder-gray-400 outline-none transition-colors focus:border-green-300 focus:bg-white"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {filtered.length === 0 ? (
          <p className="px-4 py-8 text-center text-sm text-gray-400">Nenhuma conversa encontrada</p>
        ) : (
          filtered.map((conv) => {
            const other = conv.participants.find((p) => p.user_id !== currentUserId);
            const name = other?.user.nome ?? 'Usuário';
            const isOnline = other ? onlineUsers.has(other.user_id) : false;
            const isActive = conv.id === activeId;

            return (
              <button
                key={conv.id}
                type="button"
                onClick={() => onSelect(conv.id)}
                className={`flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-gray-50 ${
                  isActive ? 'bg-green-50' : ''
                }`}
              >
                <div className="relative flex-shrink-0">
                  {other?.user.foto_url ? (
                    <img
                      src={other.user.foto_url}
                      alt={name}
                      className="h-10 w-10 rounded-full object-cover"
                    />
                  ) : (
                    <span className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100 text-sm font-semibold text-green-700">
                      {getInitials(name)}
                    </span>
                  )}
                  {isOnline && (
                    <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white bg-green-500" />
                  )}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <span className="truncate text-sm font-medium text-gray-800">{name}</span>
                    {conv.last_message && (
                      <span className="flex-shrink-0 text-xs text-gray-400">
                        {formatTime(conv.last_message.created_at)}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="truncate text-xs text-gray-500">
                      {conv.last_message
                        ? conv.last_message.content.slice(0, 50)
                        : 'Nenhuma mensagem'}
                    </p>
                    {conv.unread_count > 0 && (
                      <span className="ml-2 flex h-5 min-w-5 flex-shrink-0 items-center justify-center rounded-full bg-green-500 px-1.5 text-xs font-medium text-white">
                        {conv.unread_count > 99 ? '99+' : conv.unread_count}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}

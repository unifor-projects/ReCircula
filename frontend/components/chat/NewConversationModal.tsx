'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { Search, X } from 'lucide-react';
import api from '@/services/api';
import type { ChatConversation, UserSearchResult } from '@/types/chat';

interface Props {
  onClose: () => void;
  onCreated: (conversation: ChatConversation) => void;
}

export default function NewConversationModal({ onClose, onCreated }: Props) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<UserSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (!query.trim()) {
      setResults([]);
      return;
    }

    debounceRef.current = setTimeout(() => {
      setLoading(true);
      api
        .get<UserSearchResult[]>('/api/chat/users/search', { params: { q: query } })
        .then((res) => setResults(res.data))
        .catch(() => setResults([]))
        .finally(() => setLoading(false));
    }, 300);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  const handleSelect = useCallback(
    async (userId: number) => {
      if (creating) return;
      setCreating(true);
      try {
        const res = await api.post<ChatConversation>('/api/chat/conversations', {
          user_id: userId,
        });
        onCreated(res.data);
      } catch {
        // conversation might already exist — the backend returns it
      } finally {
        setCreating(false);
      }
    },
    [creating, onCreated],
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
          <h3 className="text-lg font-semibold text-gray-800">Nova Conversa</h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-4">
          <div className="relative">
            <Search
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
            />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar por nome ou email..."
              className="w-full rounded-lg border border-gray-200 bg-gray-50 py-2.5 pl-9 pr-3 text-sm text-gray-900 placeholder-gray-400 outline-none transition-colors focus:border-green-300 focus:bg-white"
            />
          </div>
        </div>

        <div className="max-h-64 overflow-y-auto px-2 pb-4">
          {loading ? (
            <p className="py-4 text-center text-sm text-gray-400">Buscando...</p>
          ) : results.length === 0 && query.trim() ? (
            <p className="py-4 text-center text-sm text-gray-400">Nenhum usuário encontrado</p>
          ) : (
            results.map((user) => (
              <button
                key={user.id}
                type="button"
                disabled={creating}
                onClick={() => void handleSelect(user.id)}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left transition-colors hover:bg-gray-50 disabled:opacity-50"
              >
                {user.foto_url ? (
                  <img
                    src={user.foto_url}
                    alt={user.nome}
                    className="h-9 w-9 rounded-full object-cover"
                  />
                ) : (
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-green-100 text-xs font-semibold text-green-700">
                    {user.nome
                      .split(/\s+/)
                      .slice(0, 2)
                      .map((w) => w[0]?.toUpperCase())
                      .join('')}
                  </span>
                )}
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-gray-800">{user.nome}</p>
                  {user.localizacao && (
                    <p className="truncate text-xs text-gray-400">{user.localizacao}</p>
                  )}
                </div>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

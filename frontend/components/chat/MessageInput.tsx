'use client';

import { useCallback, useLayoutEffect, useRef, useState } from 'react';
import { Send } from 'lucide-react';
import { getSocket } from '@/services/socket';

interface Props {
  conversationId: number;
  onSend: (content: string) => void;
  /** Texto já preenchido (ex.: primeira mensagem sobre um anúncio) */
  initialText?: string;
  /** Respostas rápidas: um toque envia */
  suggestions?: string[];
}

const TYPING_DEBOUNCE_MS = 2000;

export default function MessageInput({ conversationId, onSend, initialText = '', suggestions = [] }: Props) {
  const [text, setText] = useState(initialText);
  const typingTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Ajusta a altura ao conteúdo (inclusive texto já preenchido e depois de enviar)
  useLayoutEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 128)}px`;
    el.style.overflow = el.scrollHeight > 128 ? 'auto' : 'hidden';
  }, [text]);
  const isTypingRef = useRef(false);

  const emitTypingStart = useCallback(() => {
    if (isTypingRef.current) return;
    isTypingRef.current = true;
    const socket = getSocket();
    socket?.emit('typing_start', { conversation_id: conversationId });
  }, [conversationId]);

  const emitTypingStop = useCallback(() => {
    if (!isTypingRef.current) return;
    isTypingRef.current = false;
    const socket = getSocket();
    socket?.emit('typing_stop', { conversation_id: conversationId });
  }, [conversationId]);

  const handleChange = useCallback(
    (value: string) => {
      setText(value);

      if (value.trim()) {
        emitTypingStart();
        if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
        typingTimerRef.current = setTimeout(emitTypingStop, TYPING_DEBOUNCE_MS);
      } else {
        emitTypingStop();
      }
    },
    [emitTypingStart, emitTypingStop],
  );

  const handleSend = useCallback(() => {
    const content = text.trim();
    if (!content) return;
    onSend(content);
    setText('');
    emitTypingStop();
    if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
  }, [text, onSend, emitTypingStop]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend],
  );

  return (
    <div className="border-t border-gray-200 bg-white px-3 py-3 sm:px-4">
      {suggestions.length > 0 && (
        <div className="-mx-1 mb-2 flex gap-2 overflow-x-auto px-1 pb-1">
          {suggestions.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => onSend(s)}
              className="shrink-0 rounded-full border border-green-200 bg-green-50 px-3 py-1.5 text-xs font-medium text-green-800 transition hover:border-green-300 hover:bg-green-100 active:scale-95"
            >
              {s}
            </button>
          ))}
        </div>
      )}
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => handleChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escreva uma mensagem…"
          aria-label="Mensagem"
          rows={1}
          className="max-h-32 min-h-[44px] flex-1 resize-none rounded-3xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-900 placeholder-gray-500 outline-none transition-colors focus:border-green-500 focus:bg-white focus:ring-4 focus:ring-green-100"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={!text.trim()}
          aria-label="Enviar mensagem"
          className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-full bg-green-600 text-white shadow-sm transition hover:bg-green-700 active:scale-95 disabled:bg-gray-200 disabled:text-gray-400 disabled:shadow-none"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}

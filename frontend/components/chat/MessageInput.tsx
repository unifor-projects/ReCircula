'use client';

import { useCallback, useRef, useState } from 'react';
import { Send } from 'lucide-react';
import { getSocket } from '@/services/socket';

interface Props {
  conversationId: number;
  onSend: (content: string) => void;
}

const TYPING_DEBOUNCE_MS = 2000;

export default function MessageInput({ conversationId, onSend }: Props) {
  const [text, setText] = useState('');
  const typingTimerRef = useRef<ReturnType<typeof setTimeout>>();
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
    <div className="border-t border-gray-200 px-4 py-3">
      <div className="flex items-end gap-2">
        <textarea
          value={text}
          onChange={(e) => handleChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Digite uma mensagem..."
          rows={1}
          className="max-h-32 min-h-[40px] flex-1 resize-none rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-900 placeholder-gray-400 outline-none transition-colors focus:border-green-300 focus:bg-white"
          style={{ height: 'auto', overflow: 'hidden' }}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = 'auto';
            target.style.height = `${Math.min(target.scrollHeight, 128)}px`;
            target.style.overflow = target.scrollHeight > 128 ? 'auto' : 'hidden';
          }}
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={!text.trim()}
          className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-green-500 text-white transition-colors hover:bg-green-600 disabled:bg-gray-200 disabled:text-gray-400"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}

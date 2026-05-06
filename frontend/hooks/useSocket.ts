'use client';

import { useEffect, useRef } from 'react';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { connectSocket, disconnectSocket, getSocket } from '@/services/socket';
import { useChatStore } from '@/store/chatStore';
import type { ChatMessage } from '@/types/chat';

let notificationAudio: HTMLAudioElement | null = null;

function playNotificationSound() {
  const { soundEnabled } = useChatStore.getState();
  if (!soundEnabled) return;
  if (!notificationAudio) {
    notificationAudio = new Audio('/sounds/notification.wav');
    notificationAudio.volume = 0.5;
  }
  notificationAudio.currentTime = 0;
  notificationAudio.play().catch(() => {});
}

export function useSocket() {
  const { token, isAuthenticated } = useAuth();
  const initialized = useRef(false);

  useEffect(() => {
    if (!isAuthenticated || !token) {
      disconnectSocket();
      initialized.current = false;
      return;
    }

    if (initialized.current && getSocket()?.connected) return;
    initialized.current = true;

    const socket = connectSocket(token);
    const store = useChatStore.getState;

    socket.on('new_message', (data: ChatMessage) => {
      const state = store();
      state.addMessage(data);
      state.updateConversationLastMessage(data);

      if (data.conversation_id !== state.activeConversationId) {
        state.incrementUnread(data.conversation_id);
      }
    });

    socket.on(
      'notification',
      (data: {
        type: string;
        conversation_id: number;
        message_preview: string;
        sender: { nome: string };
      }) => {
        playNotificationSound();
        toast(data.sender.nome, {
          description: data.message_preview,
          duration: 4000,
        });
      },
    );

    socket.on(
      'user_typing',
      (data: { conversation_id: number; user_id: number; username: string }) => {
        const state = store();
        state.addTypingUser({
          conversation_id: data.conversation_id,
          user_id: data.user_id,
          username: data.username,
        });

        setTimeout(() => {
          store().removeTypingUser(data.conversation_id, data.user_id);
        }, 3000);
      },
    );

    socket.on('user_stop_typing', (data: { conversation_id: number; user_id: number }) => {
      store().removeTypingUser(data.conversation_id, data.user_id);
    });

    socket.on(
      'messages_read',
      (_data: { conversation_id: number; user_id: number; read_until: string }) => {},
    );

    socket.on('user_online', (data: { user_id: number }) => {
      store().setUserOnline(data.user_id);
    });

    socket.on('user_offline', (data: { user_id: number }) => {
      store().setUserOffline(data.user_id);
    });

    socket.on('error', (data: { message: string }) => {
      toast.error(data.message);
    });

    return () => {
      socket.off('new_message');
      socket.off('notification');
      socket.off('user_typing');
      socket.off('user_stop_typing');
      socket.off('messages_read');
      socket.off('user_online');
      socket.off('user_offline');
      socket.off('error');
    };
  }, [isAuthenticated, token]);
}

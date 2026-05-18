'use client';

import { useEffect } from 'react';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { connectSocket, disconnectSocket } from '@/services/socket';
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

  useEffect(() => {
    if (!isAuthenticated || !token) {
      disconnectSocket();
      return;
    }

    const socket = connectSocket(token);
    const store = useChatStore.getState;

    // Re-join the active room whenever the socket connects or reconnects.
    // The server creates a fresh session on each connection, so rooms must
    // be re-joined explicitly.
    function handleConnect() {
      const { activeConversationId } = store();
      if (activeConversationId) {
        socket.emit('join_room', { conversation_id: activeConversationId });
      }
    }

    function handleNewMessage(data: ChatMessage) {
      const state = store();
      state.addMessage(data);
      state.updateConversationLastMessage(data);
      if (data.conversation_id !== state.activeConversationId) {
        state.incrementUnread(data.conversation_id);
      }
    }

    function handleNotification(data: {
      type: string;
      conversation_id: number;
      message_preview: string;
      sender: { nome: string };
    }) {
      playNotificationSound();
      toast(data.sender.nome, {
        description: data.message_preview,
        duration: 4000,
      });
    }

    function handleUserTyping(data: {
      conversation_id: number;
      user_id: number;
      username: string;
    }) {
      store().addTypingUser({
        conversation_id: data.conversation_id,
        user_id: data.user_id,
        username: data.username,
      });
      setTimeout(() => {
        store().removeTypingUser(data.conversation_id, data.user_id);
      }, 3000);
    }

    function handleUserStopTyping(data: { conversation_id: number; user_id: number }) {
      store().removeTypingUser(data.conversation_id, data.user_id);
    }

    function handleUserOnline(data: { user_id: number }) {
      store().setUserOnline(data.user_id);
    }

    function handleUserOffline(data: { user_id: number }) {
      store().setUserOffline(data.user_id);
    }

    function handleError(data: { message: string }) {
      toast.error(data.message);
    }

    socket.on('connect', handleConnect);
    socket.on('new_message', handleNewMessage);
    socket.on('notification', handleNotification);
    socket.on('user_typing', handleUserTyping);
    socket.on('user_stop_typing', handleUserStopTyping);
    socket.on('user_online', handleUserOnline);
    socket.on('user_offline', handleUserOffline);
    socket.on('error', handleError);

    // If already connected when this effect runs, join the active room immediately.
    if (socket.connected) {
      handleConnect();
    }

    return () => {
      socket.off('connect', handleConnect);
      socket.off('new_message', handleNewMessage);
      socket.off('notification', handleNotification);
      socket.off('user_typing', handleUserTyping);
      socket.off('user_stop_typing', handleUserStopTyping);
      socket.off('user_online', handleUserOnline);
      socket.off('user_offline', handleUserOffline);
      socket.off('error', handleError);
    };
  }, [isAuthenticated, token]);
}

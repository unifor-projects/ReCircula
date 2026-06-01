'use client';

import { useSocket } from '@/hooks/useSocket';

export default function SocketProvider() {
  useSocket();
  return null;
}

'use client';

import type { ReactNode } from 'react';
import { Toaster } from 'sonner';
import { AuthProvider } from '@/contexts/AuthContext';
import Navbar from '@/components/Navbar';
import SocketProvider from '@/components/chat/SocketProvider';

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <SocketProvider />
      <Navbar />
      {children}
      <Toaster position="bottom-right" richColors />
    </AuthProvider>
  );
}

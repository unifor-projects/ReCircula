import { Suspense } from 'react';
import ChatPageClient from './ChatPageClient';

export default function ChatPage() {
  return (
    <Suspense fallback={null}>
      <ChatPageClient />
    </Suspense>
  );
}

// app/chat/page.tsx
'use client';

import { Suspense } from 'react';
import ChatTestPage from './ChatTestpage';

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="p-4">로딩 중...</div>}>
      <ChatTestPage />
    </Suspense>
  );
}

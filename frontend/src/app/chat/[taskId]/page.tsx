// app/chat/test-task/page.tsx
import { Suspense } from 'react';
import ChatTaskPage from './ChatTaskPage';

export default function ChatPageWrapper() {
  return (
    <Suspense fallback={<div className="p-6 text-gray-500">로딩 중입니다...</div>}>
      <ChatTaskPage />
    </Suspense>
  );
}

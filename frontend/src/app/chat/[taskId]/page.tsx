// src/app/chat/[taskId]/page.tsx
'use client';

import { useParams } from 'next/navigation';
import ChatTaskPage from '@/components/ChatTaskPage';

export default function TaskDetailPage() {
  const { taskId } = useParams();

  return <ChatTaskPage taskId={String(taskId)} />;
}

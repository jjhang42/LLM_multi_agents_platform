'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import ChatWindow from '@/components/chatwindow/ChatWindow';
import ChatInputBar from '@/components/ChatInputBar/ChatInputBar';
import type { MessageBubbleProps } from '@/types/MessageBubbleProps';
import { formatMessages } from '@/lib/formatMessages';
import type { ChatResponse } from '@/types/ChatInputBarProps';

export default function ChatTaskPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const searchParams = useSearchParams();
  const initialMessage = searchParams?.get('msg');

  const [messages, setMessages] = useState<MessageBubbleProps[]>([]);

  // ✅ taskId 변경 시 초기화
  useEffect(() => {
    setMessages([
      {
        role: 'agent',
        content: `Task "${taskId}"를 시작합니다.`,
        timestamp: new Date().toLocaleTimeString(),
        username: 'Agent',
        profileImage: '/agent-avatar.png',
      },
    ]);
  }, [taskId]);

  // ✅ URL로 전달된 초기 메시지 등록
  useEffect(() => {
    if (initialMessage) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'user',
          content: initialMessage,
          timestamp: new Date().toLocaleTimeString(),
          username: 'You',
          profileImage: '/user-avatar.png',
        },
      ]);
    }
  }, [initialMessage]);

  return (
    <div className="relative min-h-screen pb-32 px-6 space-y-8">
      <h1 className="text-2xl font-bold pt-6 text-center">Task ID: {taskId}</h1>

      {/* ✅ 메시지 시각화 */}
      <ChatWindow messages={messages} />

      {/* ✅ 입력창 및 응답 처리 */}
      <ChatInputBar
        taskId={taskId}
        className="fixed bottom-6 left-1/2 transform -translate-x-1/2 w-full max-w-2xl z-50"
        onSuccess={(res: ChatResponse) => {
          console.log('✅ onSuccess - ChatResponse:', res);

          const { messages: formattedMessages } = formatMessages(res);
          console.log('✅ Formatted messages:', formattedMessages);

          setMessages((prev) => [...prev, ...formattedMessages]);
        }}
      />
    </div>
  );
}

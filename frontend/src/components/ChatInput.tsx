'use client';

import { useEffect, useRef } from 'react';

interface ChatMessage {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
}

interface ChatViewProps {
  messages: ChatMessage[];
}

export default function ChatView({ messages }: ChatViewProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col gap-2 p-4 max-h-screen overflow-y-auto">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`rounded-xl px-4 py-2 max-w-lg ${
            msg.role === 'user' ? 'bg-blue-100 self-end' : 'bg-gray-100 self-start'
          }`}
        >
          <p className="text-sm text-gray-800 whitespace-pre-line">{msg.content}</p>
          <p className="text-xs text-gray-400 mt-1 text-right">{msg.timestamp}</p>
        </div>
      ))}
      <div ref={scrollRef} />
    </div>
  );
}

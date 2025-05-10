'use client';

import React from 'react';
import { MessageBubble } from '@/components/messagebubble/MessageBubble';
import type { MessageBubbleProps } from '@/types/MessageBubbleProps';

interface ChatWindowProps {
  messages: MessageBubbleProps[];
}

export default function ChatWindow({ messages }: ChatWindowProps) {
  console.log('✅ ChatWindow - Rendering messages:', messages);
  
  return (
    <div className="p-4 rounded-md overflow-y-auto dark:bg-mac-bg">
      {messages.map((msg, i) => (
        <MessageBubble 
          key={`${msg.role}-${msg.timestamp}-${i}`} 
          {...msg} 
        />
      ))}
    </div>
  );
}

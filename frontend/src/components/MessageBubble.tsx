'use client';

import React from 'react';

export interface MessageBubbleProps {
  role: 'user' | 'agent';
  content: string;
  timestamp?: string;
}

export function MessageBubble({ role, content, timestamp }: MessageBubbleProps) {
  const isUser = role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-2`}>
      <div
        className={`rounded-xl p-3 max-w-sm whitespace-pre-wrap ${
          isUser ? 'bg-blue-100 text-right' : 'bg-gray-100 text-left'
        }`}
      >
        <div>{content}</div>
        {timestamp && <div className="text-xs text-gray-400 mt-1">{timestamp}</div>}
      </div>
    </div>
  );
}

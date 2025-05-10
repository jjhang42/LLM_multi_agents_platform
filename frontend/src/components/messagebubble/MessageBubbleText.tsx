import React from 'react';
import type { MessageBubbleUIProps } from '@/types/MessageBubbleProps';

export function MessageBubbleText({
  isUser,
  content,
  timestamp,
}: Pick<MessageBubbleUIProps, 'isUser' | 'content' | 'timestamp'>) {
  return (
    <div
      className={`flex items-end gap-2 mb-2 ${
        isUser ? 'flex-row-reverse justify-end' : 'flex-row justify-start'
      }`}
    >
      {/* 말풍선 */}
      <div
        className={`px-4 py-2 rounded-xl break-words whitespace-pre-wrap ${
          isUser ? 'bg-yellow-300 text-black' : 'bg-gray-800 text-white'
        }`}
        style={{
          maxWidth: '600px',
          wordBreak: 'break-word',
        }}
      >
        <p>{content}</p>
      </div>

      {/* 타임스탬프 */}
      {timestamp && (
        <div className="text-[10px] text-gray-400 mb-1 whitespace-nowrap">
          {timestamp}
        </div>
      )}
    </div>
  );
}

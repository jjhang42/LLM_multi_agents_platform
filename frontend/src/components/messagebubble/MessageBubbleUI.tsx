// src/components/messagebubble/MessageBubbleUI.tsx

import React from 'react';
import Image from 'next/image';
import { MessageBubbleText } from './MessageBubbleText';
import { MessageBubbleGraph } from './MessageBubbleGraph';
import type { MessageBubbleUIProps } from '@/types/MessageBubbleProps';

export function MessageBubbleUI({
  isUser,
  username,
  profileImage,
  content,
  timestamp,
  parts,
  graphData,
}: MessageBubbleUIProps) {
  const isAgent = !isUser;

  return (
    <div className={`flex items-start ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      {/* 🟦 프로필 이미지 (agent 전용) */}
      {isAgent && profileImage && (
        <div className="mr-2 self-start bg-sky-100 p-1 rounded-full">
          <Image
            src={profileImage}
            alt="profile"
            width={36}
            height={36}
            className="w-9 h-9 rounded-full object-cover"
          />
        </div>
      )}

      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} w-full max-w-full`}>
        {/* 🟩 유저 이름 (agent만 표시) */}
        {isAgent && username && (
          <div className="text-sm text-white mb-1 ml-1">{username}</div>
        )}

        {/* 🟨 말풍선 내용 분기 */}
        {(graphData || parts) ? (
          <MessageBubbleGraph
            isUser={isUser}
            content={content}
            timestamp={timestamp}
            parts={parts}
            graphData={graphData}
          />
        ) : (
          <MessageBubbleText
            isUser={isUser}
            content={content}
            timestamp={timestamp}
          />
        )}
      </div>
    </div>
  );
}

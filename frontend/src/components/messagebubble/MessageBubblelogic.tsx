// src/components/messagebubble/MessageBubblelogic.tsx
import React from 'react';
import { MessageBubbleUI } from './MessageBubbleUI';
import type { MessageBubbleProps } from '@/types/MessageBubbleProps';
import type { Part } from './RenderParts';

export function MessageBubbleLogic({
  role,
  content,
  timestamp,
  profileImage,
  username,
  parts,
  graphData,
}: MessageBubbleProps) {
  const isUser = role === 'user';

  let parsedParts: Part[] | undefined = parts;

  // fallback: content가 JSON 형태의 parts 포함 문자열일 경우 파싱
  if (!parsedParts && typeof content === 'string') {
    try {
      const parsed = JSON.parse(content);
      if (Array.isArray(parsed.parts)) {
        parsedParts = parsed.parts;
      }
    } catch {
      // parsing 실패 시 무시
    }
  }

  return (
    <MessageBubbleUI
      isUser={isUser}
      username={username}
      profileImage={profileImage}
      content={content}
      timestamp={timestamp}
      parts={parsedParts}
      graphData={graphData}
    />
  );
}

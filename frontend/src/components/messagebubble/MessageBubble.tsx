// src/components/messagebubble/MessageBubble.tsx
'use client';

import React from 'react';
import { MessageBubbleLogic } from './MessageBubblelogic';
import type { MessageBubbleProps } from '@/types/MessageBubbleProps';

export function MessageBubble(props: MessageBubbleProps) {
  return <MessageBubbleLogic {...props} />;
}

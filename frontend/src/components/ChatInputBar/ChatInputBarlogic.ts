'use client';

import { useState } from 'react';
import { sendTaskRequest } from '@/lib/sendTaskRequest';
import { composeParts } from '@/lib/composeParts';
import type { UploadedFile } from './useUploadModal';
import type { ChatResponse } from '@/types/ChatInputBarProps';

export function useChatInputLogic(
  taskId: string,
  uploadedFiles: UploadedFile[],
  onSuccess?: (res: ChatResponse) => void
) {
  const [input, setInput] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() && uploadedFiles.length === 0) return;

    const parts = composeParts(input, uploadedFiles);
    console.log('🔼 Sending parts:', parts);

    try {
      const res = await sendTaskRequest(taskId, parts);

      const response: ChatResponse = {
        type: res.type ?? 'chat',
        originalInput: input,
        message: res.message ?? {
          role: 'assistant',
          parts: [
            {
              type: 'text',
              text: res.reply ?? '[응답 없음]',
            },
          ],
        },
        tasks: res.tasks,
        graph: res.graph,
        context_id: res.context_id,
        ...res, // 추가 확장 필드도 포함
      };

      onSuccess?.(response);
    } catch (err) {
      console.error('❌ 전송 실패:', err);
    }

    setInput('');
  };

  return { input, setInput, handleSubmit };
}

'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { MessageBubble } from '@/components/MessageBubble';
import { ModalUploader } from '@/components/ModalUploader';
import { TaskGraph } from '@/components/TaskGraph';
import type { MessageBubbleProps } from '@/components/MessageBubble';

export default function ChatTaskPage() {
  const { taskId } = useParams<{ taskId: string }>();

  const [messages] = useState<MessageBubbleProps[]>([
    { role: 'user', content: '작업을 시작해 주세요', timestamp: '09:00' },
    { role: 'agent', content: '작업을 분석 중입니다', timestamp: '09:01' },
  ]);
  

  const [uploadedFiles, setUploadedFiles] = useState<
    { name: string; dataUrl: string }[]
  >([]);

  const handleUpload = (files: { name: string; dataUrl: string }[]) => {
    setUploadedFiles(files);
    // 이후 파일 업로드 처리 로직 작성 가능
  };

  const taskGraphMock = {
    nodes: [
      { id: '1', label: 'Parse', position: { x: 0, y: 0 } },
      { id: '2', label: 'Plan', position: { x: 150, y: 100 } },
      { id: '3', label: 'Execute', position: { x: 300, y: 0 } },
    ],
    edges: [
      { id: 'e1-2', source: '1', target: '2' },
      { id: 'e2-3', source: '2', target: '3' },
    ],
  };

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-bold">Task ID: {taskId}</h1>

      <div className="border p-4 rounded-md h-72 overflow-y-auto bg-white">
        {messages.map((msg, i) => (
          <MessageBubble key={i} {...msg} />
        ))}
      </div>

      <ModalUploader onUpload={handleUpload} />
      {uploadedFiles.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mt-4">Uploaded Files:</h2>
          <ul className="list-disc ml-5">
            {uploadedFiles.map((file, i) => (
              <li key={i}>{file.name}</li>
            ))}
          </ul>
        </div>
      )}

      <TaskGraph nodes={taskGraphMock.nodes} edges={taskGraphMock.edges} />
    </div>
  );
}

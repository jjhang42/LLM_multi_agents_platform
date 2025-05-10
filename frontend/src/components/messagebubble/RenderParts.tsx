// src/components/messagebubble/RenderParts.tsx
import React from 'react';
import Image from 'next/image';

export interface Part {
  type: string;
  text?: string;
  url?: string;
  metadata?: Record<string, unknown>;
}

interface RenderPartsProps {
  parts: Part[];
}

export function RenderParts({ parts }: RenderPartsProps) {
  return (
    <div className="space-y-3">
      {parts.map((part, idx) => {
        switch (part.type) {
          case 'text':
            return (
              <p key={idx} className="whitespace-pre-wrap text-sm text-gray-900 dark:text-gray-100">
                {part.text}
              </p>
            );
          case 'image':
            return (
              <Image
                key={idx}
                src={part.url ?? ''}
                alt="응답 이미지"
                width={500}
                height={300}
                className="rounded-lg object-contain border border-gray-300"
              />
            );
          case 'code':
            return (
              <pre
                key={idx}
                className="bg-gray-100 dark:bg-gray-800 text-sm p-3 rounded-md overflow-auto"
              >
                <code>{part.text}</code>
              </pre>
            );
          default:
            return (
              <p key={idx} className="text-sm text-red-500">
                [지원되지 않는 형식: {part.type}]
              </p>
            );
        }
      })}
    </div>
  );
}

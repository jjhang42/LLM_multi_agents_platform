// src/components/messagebubble/MessageBubbleGraph.tsx
import React from 'react';
import TaskGraphViewer from '@/components/taskgraph/TaskGraphViewer';
import type { FlowNode, FlowEdge, Part } from '@/types/MessageBubbleProps';

export interface MessageBubbleGraphProps {
  isUser: boolean;
  content: string;
  timestamp?: string;
  parts?: Part[];
  graphData?: {
    nodes: FlowNode[];
    edges: FlowEdge[];
  };
}

export function MessageBubbleGraph({
  isUser,
  graphData,
  timestamp,
}: MessageBubbleGraphProps) {
  if (!graphData) return null;

  return (
    <div
      className={`relative px-4 py-2 rounded-xl w-full max-w-[600px] break-words whitespace-pre-wrap ${
        isUser ? 'bg-yellow-300 text-black' : 'bg-gray-800 text-white'
      }`}
      style={{ overflow: 'hidden' }}
    >
      <div className="mb-2">
        <TaskGraphViewer nodes={graphData.nodes} edges={graphData.edges} />
      </div>

      {timestamp && (
        <div className="text-[10px] text-gray-400 mt-1 text-right">
          {timestamp}
        </div>
      )}
    </div>
  );
}

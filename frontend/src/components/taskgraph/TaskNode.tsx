// src/components/taskgraph/TaskNode.tsx
import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export default function TaskNode({ data }: NodeProps) {
  return (
    <div className="bg-white text-black rounded-md shadow-md p-3 text-sm min-w-[180px]">
      <div className="font-semibold text-gray-700 mb-1">{data.label}</div>
      <div className="text-xs text-gray-600 mb-1">{data.instruction}</div>
      <div className="text-xs text-gray-400">{data.action}</div>
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

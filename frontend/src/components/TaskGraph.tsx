'use client';

import React from 'react';
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';

interface TaskNode {
  id: string;
  label: string;
  position: { x: number; y: number };
}

interface TaskEdge {
  id: string;
  source: string;
  target: string;
}

interface TaskGraphProps {
  nodes: TaskNode[];
  edges: TaskEdge[];
}

export function TaskGraph({ nodes, edges }: TaskGraphProps) {
  const flowNodes = nodes.map((node) => ({
    id: node.id,
    data: { label: node.label },
    position: node.position,
  }));

  const flowEdges = edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
  }));

  return (
    <div style={{ width: '100%', height: 500 }}>
      <ReactFlow nodes={flowNodes} edges={flowEdges} fitView>
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
}

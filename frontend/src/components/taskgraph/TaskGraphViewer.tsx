import React from 'react';
import ReactFlow, {
  Background,
  Controls,
  Node,
  Edge,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import TaskNode from './TaskNode';

const nodeTypes = {
  task: TaskNode,
};

interface TaskGraphViewerProps {
  nodes: Node[];
  edges: Edge[];
}

export default function TaskGraphViewer({ nodes, edges }: TaskGraphViewerProps) {
  return (
    <div className="w-full h-[400px] border border-gray-300 rounded-md overflow-hidden">
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          proOptions={{ hideAttribution: true }}
        >
          <Background />
          <Controls />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}

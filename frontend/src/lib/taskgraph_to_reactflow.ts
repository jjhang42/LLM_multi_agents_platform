// src/lib/taskgraph_to_reactflow.ts
import type { FlowNode, FlowEdge } from '@/types/MessageBubbleProps';
import type { Task } from '@/types/Task';
import type { GraphStructure } from '@/types/Task'; 

export function taskgraph_to_reactflow(
  graph: GraphStructure,
  tasks: Record<string, Task>
): { nodes: FlowNode[]; edges: FlowEdge[] } {
  const nodes: FlowNode[] = [];
  const edges: FlowEdge[] = [];

  const x_step = 200;
  const y_step = 120;

  Object.entries(graph.dependencies).forEach(([taskId], i) => {
    const task = tasks[taskId];
    const meta = task.metadata as { action?: string; target?: string } | undefined;

    const label = `${meta?.action ?? 'N/A'}\n${meta?.target ?? 'N/A'}`;
    const x = 100 + (i % 4) * x_step;
    const y = 100 + Math.floor(i / 4) * y_step;

    nodes.push({
      id: taskId,
	  type: 'default',
      data: { label },
      position: { x, y },
    });
  });

  for (const [target, sources] of Object.entries(graph.dependencies)) {
    for (const source of sources) {
      edges.push({
        id: `e_${source}_${target}`,
        source,
        target,
      });
    }
  }

  return { nodes, edges };
}

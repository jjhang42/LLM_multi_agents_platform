import type {
  MessageBubbleProps,
  FlowNode,
  FlowEdge,
} from '@/types/MessageBubbleProps';
import type { ChatResponse } from '@/types/ChatInputBarProps';

type GraphData = { nodes: FlowNode[]; edges: FlowEdge[] };

export function formatMessages(res: ChatResponse): {
  messages: MessageBubbleProps[];
  graphData?: GraphData;
} {
  const now = new Date().toLocaleTimeString();

  const userMessage: MessageBubbleProps = {
    role: 'user',
    content: res.originalInput ?? '[No input]',
    timestamp: now,
    username: 'You',
    profileImage: '/user-avatar.png',
  };

  switch (res.type) {
    case 'chat': {
      const text =
        typeof res.message === 'object' &&
        Array.isArray(res.message.parts) &&
        typeof res.message.parts[0]?.text === 'string'
          ? res.message.parts[0].text
          : '[response error]';

      const agentMessage: MessageBubbleProps = {
        role: 'agent',
        content: text,
        timestamp: now,
        username: 'Agent',
        profileImage: '/agent-avatar.png',
      };

      return { messages: [userMessage, agentMessage] };
    }

    case 'task_graph': {
      const flow = res.flow;

      if (
        flow &&
        typeof flow === 'object' &&
        Array.isArray((flow as GraphData).nodes) &&
        Array.isArray((flow as GraphData).edges)
      ) {
        const graphData = flow as GraphData;

        const agentMessage: MessageBubbleProps = {
          role: 'agent',
          content: '[Task Graph 응답 수신됨]',
          timestamp: now,
          username: 'Agent',
          profileImage: '/agent-avatar.png',
          graphData,
        };

        return {
          messages: [userMessage, agentMessage],
          graphData,
        };
      }

      const errorMessage: MessageBubbleProps = {
        role: 'agent',
        content: '[task_graph 응답 오류: 유효한 flow 구조 없음]',
        timestamp: now,
        username: 'Agent',
        profileImage: '/agent-avatar.png',
      };

      return {
        messages: [userMessage, errorMessage],
      };
    }

    case 'tasks': {
      const agentMessage: MessageBubbleProps = {
        role: 'agent',
        content: JSON.stringify({ tasks: res.tasks, graph: res.graph }, null, 2),
        timestamp: now,
        username: 'Agent',
        profileImage: '/agent-avatar.png',
      };

      return { messages: [userMessage, agentMessage] };
    }

    default: {
      const agentMessage: MessageBubbleProps = {
        role: 'agent',
        content: '[지원되지 않는 응답 유형]',
        timestamp: now,
        username: 'Agent',
        profileImage: '/agent-avatar.png',
      };

      return { messages: [userMessage, agentMessage] };
    }
  }
}

// src/types/MessageBubbleProps.ts

// 멀티모달 메시지 파트를 표현
export interface Part {
  type: string;
  text?: string;
  url?: string;
  metadata?: Record<string, unknown>;
}

// React Flow용 노드 및 엣지 타입
export interface FlowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    metadata?: Record<string, unknown>;
  };
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  animated?: boolean;
}

// 말풍선 1개 (텍스트 메시지, 멀티모달 파트, 그래프 포함 가능)
export interface MessageBubbleProps {
  role: 'user' | 'agent';
  content: string;
  timestamp?: string;
  profileImage?: string;
  username?: string;
  parts?: Part[];
  graphData?: {
    nodes: FlowNode[];
    edges: FlowEdge[];
  };
}

// 내부 UI 컴포넌트에서 사용하는 구조 (로직 처리 후 전달되는 UI단 props)
export interface MessageBubbleUIProps {
  isUser: boolean;
  username?: string;
  profileImage?: string;
  content: string;
  timestamp?: string;
  parts?: Part[];
  graphData?: {
    nodes: FlowNode[];
    edges: FlowEdge[];
  };
}

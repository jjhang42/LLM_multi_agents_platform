export interface MessagePart {
  type: 'text' | 'image' | 'code' | string;
  text?: string;
  url?: string;
  metadata?: Record<string, unknown>;
}

export interface ChatMessage {
  role: 'assistant' | 'user' | string;
  parts: MessagePart[];
  metadata?: Record<string, unknown>;
}

export interface ChatResponse {
  type: 'chat' | 'task_graph' | 'tasks' | string;
  originalInput: string;
  message?: ChatMessage;
  tasks?: Record<string, unknown>;
  graph?: unknown;
  context_id?: string;
  [key: string]: unknown;
}

export interface ChatInputBarProps {
  taskId: string;
  className?: string;
  onSuccess?: (res: ChatResponse) => void;
}

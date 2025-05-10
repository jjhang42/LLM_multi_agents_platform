// src/types/Task.ts
export interface GraphStructure {
  dependencies: Record<string, string[]>;
}

export type TaskState =
  | 'submitted'
  | 'working'
  | 'input-required'
  | 'completed'
  | 'canceled'
  | 'failed'
  | 'unknown';

export interface MessagePart {
  type: string;
  text?: string;
  url?: string;
  metadata?: Record<string, unknown>;
}

export interface Message {
  role: string;
  parts: MessagePart[];
  metadata?: Record<string, unknown>;
  timestamp?: string;
}

export interface Artifact {
  id: string;
  type: string;
  url?: string;
  metadata?: Record<string, unknown>;
}

export interface TaskStatus {
  state: TaskState;
  message?: Message;
  timestamp: string;
}

export interface Task {
  id: string;
  session_id: string;
  status: TaskStatus;
  history?: Message[];
  artifacts?: Artifact[];
  metadata?: Record<string, unknown>;
}

export interface TaskSendParams {
  id: string;
  session_id?: string;
  message: Message;
  history_length?: number;
  push_notification?: PushNotificationConfig;
  metadata?: Record<string, unknown>;
}

export interface PushNotificationConfig {
  type: string;
  target: string;
  metadata?: Record<string, unknown>;
}

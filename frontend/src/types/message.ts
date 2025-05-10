// root/frontend/src/types/message.ts
export type Message = {
	role: 'user' | 'agent';
	content: string;
	timestamp: string;
	username: string;
	profileImage?: string;
  };
  
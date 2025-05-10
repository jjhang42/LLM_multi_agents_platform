// src/lib/sendTaskRequest.ts
import axios from 'axios';
import type { Part } from '@/types/Part';

export async function sendTaskRequest(taskId: string, parts: Part[]) {
  const apiBase = process.env.NEXT_PUBLIC_API_GATEWAY;
  const res = await axios.post(`${apiBase}/task`, {
    task_id: taskId,
    parts,
  });
  return res.data;
}

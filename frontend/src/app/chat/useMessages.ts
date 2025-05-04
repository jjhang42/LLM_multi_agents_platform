"use client";

import useSWR from "swr";
import axios from "axios";

const fetcher = (url: string) => axios.get(url).then(res => res.data);

export function useMessages(taskId: string) {
  const { data, error, mutate, isLoading } = useSWR(
    `${process.env.NEXT_PUBLIC_API_GATEWAY}/messages/${taskId}`,
    fetcher
  );

  const sendMessage = async (message: { role: string; content: string }) => {
    const newMessage = await axios.post(
      `${process.env.NEXT_PUBLIC_API_GATEWAY}/messages`,
      { task_id: taskId, ...message }
    );
    mutate(); // 🔄 최신 메시지 다시 불러오기
    return newMessage.data;
  };

  return {
    messages: data || [],
    error,
    isLoading,
    sendMessage,
  };
}

import { ImageIcon, Send } from 'lucide-react';
import React, { FormEvent } from 'react';

interface ChatInputBarUIProps {
  input: string;
  setInput: (val: string) => void;
  handleSubmit: (e: FormEvent) => void;
  className?: string;
  openUploadModal: () => void;
}

export function ChatInputBarUI({
  input,
  setInput,
  handleSubmit,
  className = '',
  openUploadModal,
}: ChatInputBarUIProps) {
  return (
    <form
      onSubmit={handleSubmit}
      className={`flex items-center gap-3 bg-gray-50 border border-gray-300 rounded-full px-4 py-2 w-full max-w-2xl shadow ${className}`}
    >
      {/* 입력창 */}
      <input
        type="text"
        placeholder="메시지를 입력하세요..."
        className="flex-1 min-w-0 px-4 py-2 bg-white text-black rounded-full placeholder:text-gray-400 focus:outline-none"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      {/* 파일 업로드 */}
      <button
        type="button"
        title="파일 업로드"
        onClick={openUploadModal}
        className="p-2 hover:bg-gray-100 rounded-full transition-colors"
      >
        <ImageIcon className="w-5 h-5 text-gray-500 hover:text-black" />
      </button>

      {/* 전송 버튼 */}
      <button
        type="submit"
        title="전송"
        className="p-2 hover:bg-gray-100 rounded-full transition-colors"
      >
        <Send className="w-5 h-5 text-gray-500 hover:text-black" />
      </button>
    </form>
  );
}

import { ImageIcon, Send } from 'lucide-react';
import React, { FormEvent } from 'react';

interface ChatSearchBarUIProps {
  input: string;
  setInput: (val: string) => void;
  handleSubmit: (e: FormEvent) => void;
  className?: string;
  openUploadModal: () => void;
}

export function ChatSearchBarUI({
  input,
  setInput,
  handleSubmit,
  className = '',
  openUploadModal,
}: ChatSearchBarUIProps) {
  const formStyle = `mx-auto w-full max-w-[600px] flex items-center gap-3 
    bg-white border border-gray-300 rounded-full px-6 py-2 shadow-md ${className}`;
  const inputStyle = `flex-1 min-w-0 px-4 py-3 text-lg bg-white text-black 
    rounded-full placeholder:text-gray-400 focus:outline-none`;
  const buttonStyle = `p-2 bg-white rounded-full`;
  const iconStyle = `w-6 h-6 text-black`;

  return (
    <form onSubmit={handleSubmit} className={formStyle}>
      <input
        type="text"
        placeholder="무엇이든 물어보세요..."
        className={inputStyle}
        value={input ?? ''}
        onChange={(e) => setInput(e.target.value)}
      />

      <button
        type="button"
        title="파일 업로드"
        onClick={openUploadModal}
        className={buttonStyle}
      >
        <ImageIcon className={iconStyle} />
      </button>

      <button
        type="submit"
        title="전송"
        className={buttonStyle}
      >
        <Send className={iconStyle} />
      </button>
    </form>
  );
}

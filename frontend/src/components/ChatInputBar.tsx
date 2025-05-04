'use client';

import { useState } from 'react';
import { Paperclip, Send, ImageIcon } from 'lucide-react';

export default function ChatInputBar({
  onSend,
  className = '',
}: {
  onSend: (message: string) => void;
  className?: string; // 위치 조정을 위한 외부 클래스
}) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input);
    setInput('');
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={`flex items-center gap-3 bg-background border border-border rounded-full px-4 py-2 w-full max-w-2xl ${className}`}
    >
      <input
        type="text"
        placeholder="메시지를 입력하세요..."
        className="flex-grow px-3 py-2 bg-muted rounded-full text-foreground placeholder:text-muted-foreground focus:outline-none"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <button type="button" title="멀티모달 업로드">
        <ImageIcon className="w-5 h-5 text-muted-foreground hover:text-foreground" />
      </button>

      <button type="button" title="기타 기능">
        <Paperclip className="w-5 h-5 text-muted-foreground hover:text-foreground" />
      </button>

      <button type="submit" title="전송">
        <Send className="w-5 h-5 text-primary hover:text-primary-foreground" />
      </button>
    </form>
  );
}

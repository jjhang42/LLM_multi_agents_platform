'use client';

import { useRouter } from 'next/navigation';
import { useChatInputLogic } from '../ChatInputBar/ChatInputBarlogic';
import { ChatSearchBarUI } from './ChatSearchBarUI';
import { useUploadModal } from '../ChatInputBar/useUploadModal';
import { UploadModal } from '../ChatInputBar/UploadModal';

export default function ChatSearchBar({ className = '' }: { className?: string }) {
  const router = useRouter();
  const taskId = `task_${Date.now()}`;

  const {
    isModalOpen,
    uploadedFiles,
    openModal,
    closeModal,
    handleUpload,
  } = useUploadModal();

  const handleSuccess = () => {
    router.push(`/chat/${taskId}?msg=${encodeURIComponent(input)}`);
  };

  const { input, setInput, handleSubmit } = useChatInputLogic(taskId, uploadedFiles, handleSuccess);

  return (
    <>
      <ChatSearchBarUI
        input={input}
        setInput={setInput}
        handleSubmit={handleSubmit}
        openUploadModal={openModal}
        className={className}
      />
      <UploadModal
        isOpen={isModalOpen}
        onClose={closeModal}
        onUpload={handleUpload}
        uploadedFiles={uploadedFiles}
      />
    </>
  );
}

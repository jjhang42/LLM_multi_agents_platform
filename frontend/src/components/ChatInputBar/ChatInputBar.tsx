'use client';

import { useChatInputLogic } from './ChatInputBarlogic';
import { ChatInputBarUI } from './ChatInputBarUI';
import { useUploadModal } from './useUploadModal';
import { UploadModal } from './UploadModal';
import type { ChatInputBarProps } from '@/types/ChatInputBarProps';

export default function ChatInputBar({ taskId, className = '', onSuccess }: ChatInputBarProps) {
  const {
    isModalOpen,
    uploadedFiles,
    openModal,
    closeModal,
    handleUpload,
  } = useUploadModal();

  const { input, setInput, handleSubmit } = useChatInputLogic(taskId, uploadedFiles, onSuccess);

  return (
    <>
      <ChatInputBarUI
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

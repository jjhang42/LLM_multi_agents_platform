'use client';

import { useState } from 'react';

export interface UploadedFile {
  name: string;
  dataUrl: string;
}

export function useUploadModal() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  const handleUpload = (files: FileList | null) => {
    if (!files) return;

    const readers = Array.from(files).map(
      (file) =>
        new Promise<UploadedFile>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () =>
            resolve({
              name: file.name,
              dataUrl: reader.result as string,
            });
          reader.onerror = reject;
          reader.readAsDataURL(file);
        })
    );

    Promise.all(readers)
      .then((results) => {
        setUploadedFiles((prev) => [...prev, ...results]);
        closeModal();
      })
      .catch(console.error);
  };

  return {
    isModalOpen,
    uploadedFiles,
    openModal,
    closeModal,
    handleUpload,
  };
}

'use client';

import React, { useState } from 'react';

interface ModalUploaderProps {
  onUpload: (files: { name: string; dataUrl: string }[]) => void;
}

export function ModalUploader({ onUpload }: ModalUploaderProps) {
  const [files, setFiles] = useState<File[]>([]);
  if (!files) return;
  const handleFiles = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = Array.from(e.target.files || []);
    const readAsDataUrl = (file: File) =>
      new Promise<{ name: string; dataUrl: string }>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve({ name: file.name, dataUrl: reader.result as string });
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

    const previews = await Promise.all(fileList.map(readAsDataUrl));
    setFiles(fileList);
    onUpload(previews);
  };

  return (
    <div className="p-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">Upload files</label>
      <input type="file" multiple onChange={handleFiles} />
    </div>
  );
}

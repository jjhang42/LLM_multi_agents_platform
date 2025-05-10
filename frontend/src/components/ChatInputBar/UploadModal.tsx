'use client';

import React from 'react';
import type { UploadedFile } from './useUploadModal';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (files: FileList | null) => void;
  uploadedFiles: UploadedFile[];
}

export function UploadModal({ isOpen, onClose, onUpload }: UploadModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white dark:bg-gray-900 p-4 rounded-xl max-w-sm w-full space-y-4">
        <h2 className="text-lg font-semibold text-center">파일 업로드</h2>
        <input
          type="file"
          multiple
          accept="image/*,application/pdf"
          onChange={(e) => onUpload(e.target.files)}
          className="block w-full text-sm text-gray-700"
        />
        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="text-sm text-gray-500 hover:underline">
            취소
          </button>
        </div>
      </div>
    </div>
  );
}

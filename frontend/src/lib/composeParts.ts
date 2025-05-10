// src/lib/composeParts.ts
import type { Part } from '@/types/Part';

export function composeParts(
  text: string,
  files: { name: string; dataUrl: string }[]
): Part[] {
  const parts: Part[] = [];

  if (text.trim()) {
    parts.push({ type: 'text', text });
  }

  for (const file of files) {
    if (!file.name) {
      console.warn('File name is missing, skipping file');
      continue;
    }
    parts.push({
      type: 'image',
      data_url: file.dataUrl,
      name: file.name
    });
  }

  return parts;
}

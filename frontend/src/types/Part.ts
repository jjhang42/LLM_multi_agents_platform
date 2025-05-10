// src/types/Part.ts
export type Part =
  | { type: 'text'; text: string }
  | { type: 'image'; data_url: string; name: string };

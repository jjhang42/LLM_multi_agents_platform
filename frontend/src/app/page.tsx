'use client';

import Image from 'next/image';
import ChatSearchBar from '@/components/ChatSearchBar/ChatSearchBar';

export default function Home() {
  return (
    <div className="min-h-screen w-full px-6 sm:px-20 font-sans bg-background">
      <main className="w-full flex justify-center mt-[15vh]">
        <div className="flex flex-col items-center gap-8 w-full max-w-2xl">
          <Image
            src="/favicon.ico"
            alt="App icon"
            width={64}
            height={64}
            priority
          />

          <ChatSearchBar />
        </div>
      </main>
    </div>
  );
}

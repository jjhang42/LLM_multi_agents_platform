'use client';

import Link from 'next/link';
import Image from 'next/image';

export default function Home() {
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-sans">
      <main className="flex flex-col gap-8 row-start-2 items-center">
        <Image
          src="/favicon.ico"
          alt="App icon"
          width={64}
          height={64}
          priority
        />


        <Link
          href="/chat/test-task"
          className="text-white no-underline hover:underline text-lg"
        >
          Start: AI Agent
        </Link>
      </main>
    </div>
  );
}

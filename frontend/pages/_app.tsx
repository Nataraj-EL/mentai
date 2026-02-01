import type { AppProps } from "next/app";
import Head from "next/head";
import { SessionProvider } from "next-auth/react";
import dynamic from 'next/dynamic';
import Footer from '../src/components/Footer';
import ChatInterface from '../src/components/ChatInterface';
import "../styles/globals.css";

const ThreeJSBackground = dynamic(() => import('../src/components/ThreeJSBackground'), { ssr: false });

export default function App({ Component, pageProps: { session, ...pageProps } }: AppProps) {
  return (
    <SessionProvider session={session}>
      <Head>
        <title>MentAI | Your AI Learning Buddy</title>
      </Head>
      <div className="min-h-screen bg-black text-white relative flex flex-col">
        <ThreeJSBackground />
        <div className="relative z-10 flex-grow flex flex-col">
          <main className="container mx-auto px-4 py-8 flex-grow">
            <Component {...pageProps} />
          </main>
          <Footer />
          <ChatInterface />
        </div>
      </div>
    </SessionProvider>
  );
}

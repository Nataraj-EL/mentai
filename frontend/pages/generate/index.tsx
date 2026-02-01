"use client"
import { useEffect } from "react";
import { useRouter } from "next/router";

export default function GeneratePage() {
  const router = useRouter();

  useEffect(() => {
    router.push('/');
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-lg text-gray-600">Redirecting to course builder...</p>
      </div>
    </div>
  );
}

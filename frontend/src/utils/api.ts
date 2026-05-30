import axios from 'axios';

export const API = axios.create();

API.interceptors.request.use((config) => {
  const isDev = process.env.NODE_ENV === 'development';
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const isLocalHost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.') || hostname.startsWith('10.') || hostname.endsWith('.local');
    if (isDev || isLocalHost) {
      config.baseURL = 'http://localhost:8000/api';
    } else {
      config.baseURL = process.env.NEXT_PUBLIC_API_URL || 'https://mentai-backend-gt5t.onrender.com/api';
    }
    console.log(`[Axios Interceptor Client] hostname=${hostname}, isDev=${isDev}, isLocalHost=${isLocalHost} -> baseURL=${config.baseURL}`);
  } else {
    config.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    console.log(`[Axios Interceptor Server] SSR -> baseURL=${config.baseURL}`);
  }
  return config;
});

export const generateCourse = async (topic: string, language: string = 'python') =>
  await API.post('/generate-course/', { topic, language });

export const getVideos = async (topic: string) =>
  await API.get(`/youtube-videos/?topic=${topic}`);

export const generateQuiz = async (topic: string, language: string = 'python') =>
  await API.post('/generate-quiz/', { topic, language });

export const markCompleted = async (courseId: number) =>
  await API.post('/progress/', { course: courseId });

export const askMentAI = async (query: string) =>
  await API.post('/v1/ask', { query });
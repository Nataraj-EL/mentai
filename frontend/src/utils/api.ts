import axios from 'axios';

export const API = axios.create();

API.interceptors.response.use(
  (response) => {
    const url = response.config.url || '';
    if (typeof window !== 'undefined' && url.includes('generate-course')) {
      const data = response.data as {
        title?: string;
        modules?: Array<{
          theory?: string;
          content?: string;
          mini_labs?: unknown[];
          quizzes?: unknown[];
          practice_problems?: unknown[];
        }>;
      };
      const first = data?.modules?.[0];
      const theoryLen = (first?.theory || first?.content || '').length;
      console.log('[MentAI API] generate-course response', {
        status: response.status,
        baseURL: response.config.baseURL,
        title: data?.title,
        moduleCount: data?.modules?.length ?? 0,
        module0_theoryLen: theoryLen,
        module0_miniLabs: first?.mini_labs?.length ?? 0,
        module0_quizzes: first?.quizzes?.length ?? 0,
        module0_practiceProblems: first?.practice_problems?.length ?? 0,
        raw: response.data,
      });
    }
    return response;
  },
  (error) => Promise.reject(error)
);

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
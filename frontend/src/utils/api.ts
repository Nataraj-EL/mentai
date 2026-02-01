import axios from 'axios';

const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
});

export const generateCourse = async (topic: string, language: string = 'python') =>
  await API.post('/generate-course/', { topic, language });

export const getVideos = async (topic: string) =>
  await API.get(`/youtube-videos/?topic=${topic}`);

export const generateQuiz = async (topic: string, language: string = 'python') =>
  await API.post('/generate-quiz/', { topic, language });

export const markCompleted = async (courseId: number) =>
  await API.post('/progress/', { course: courseId }); 

import React, { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import axios from 'axios';

interface CourseProgress {
    topic_slug: string;
    display_title: string;
    current_module: number;
    completed_count: number;
    percent_complete: number;
    last_visited: string;
}

const Dashboard = () => {
    const { data: session, status } = useSession();
    const [courses, setCourses] = useState<CourseProgress[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboard = async () => {
            if (session?.user?.email) {
                try {
                    const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/dashboard/?email=${session.user.email}`);
                    setCourses(res.data.courses || []);
                } catch (err) {
                    console.error("Dashboard fetch error:", err);
                } finally {
                    setLoading(false);
                }
            }
        };

        if (status === 'authenticated') {
            fetchDashboard();
        } else if (status === 'unauthenticated') {
            setLoading(false);
        }
    }, [session, status]);

    if (status === 'loading' || (status === 'authenticated' && loading)) {
        return <div className="flex justify-center items-center h-64 text-blue-400">Loading your progress...</div>;
    }

    if (status === 'unauthenticated') {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] text-center space-y-6">
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                    Track Your Learning Journey
                </h1>
                <p className="text-gray-400 max-w-md">
                    Sign in to save your progress, track completed modules, and earn achievements.
                </p>
                <p className="text-gray-400 max-w-md">
                    Guest Mode Active. Progress is stored temporarily.
                </p>
                {/* Sign In Button Hidden */}
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <header className="space-y-2">
                <h1 className="text-3xl font-bold text-white">My Learning Dashboard</h1>
                <p className="text-gray-400">Welcome back, {session?.user?.name || "Learner"}. logic.</p>
            </header>

            {courses.length === 0 ? (
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center space-y-4">
                    <p className="text-gray-400 text-lg">You haven&apos;t started any courses yet.</p>
                    <Link href="/" className="inline-block px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                        Browse Courses
                    </Link>
                </div>
            ) : (
                <div className="grid gap-6">
                    {courses.map((course) => (
                        <div key={course.topic_slug} className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all flex flex-col md:flex-row justify-between items-center gap-6">
                            <div className="flex-1 space-y-3 w-full">
                                <div className="flex justify-between items-start">
                                    <h3 className="text-xl font-bold text-white">{course.display_title}</h3>
                                    <span className="text-xs text-gray-400 px-2 py-1 bg-gray-800 rounded-full">
                                        Module {course.current_module}/10
                                    </span>
                                </div>

                                {/* Progress Bar */}
                                <div className="w-full bg-gray-800 rounded-full h-2.5 overflow-hidden">
                                    <div
                                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2.5 rounded-full"
                                        style={{ width: `${course.percent_complete}%` }}
                                    ></div>
                                </div>

                                <p className="text-sm text-gray-500">
                                    {course.percent_complete}% Complete &bull; Last visited {new Date(course.last_visited).toLocaleDateString()}
                                </p>
                            </div>

                            <Link
                                href={`/quiz/${course.current_module}?topic=${course.topic_slug}`}
                                className="w-full md:w-auto px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition text-center shadow-lg hover:shadow-blue-600/20 whitespace-nowrap"
                            >
                                Continue Learning
                            </Link>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Dashboard;

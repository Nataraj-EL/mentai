
import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import GithubProvider from "next-auth/providers/github";
import axios from "axios";
import { API } from "../../../src/utils/api";

import CredentialsProvider from "next-auth/providers/credentials";

export default NextAuth({
    providers: [
        CredentialsProvider({
            name: "Demo Account",
            credentials: {
                username: { label: "Username", type: "text", placeholder: "demo" },
                password: { label: "Password", type: "password" }
            },
            async authorize() {
                // Add logic here to look up the user from the credentials supplied
                const user = { id: "1", name: "Demo User", email: "demo@mentai.com" }
                if (user) {
                    return user
                } else {
                    return null
                }
            }
        }),
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID || "",
            clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
        }),
        GithubProvider({
            clientId: process.env.GITHUB_ID || "",
            clientSecret: process.env.GITHUB_SECRET || "",
        }),
    ],
    callbacks: {
        async signIn({ user, account }) {
            // Sync user with Django Backend
            try {
                await API.post(`/auth/sync/`, {
                    email: user.email,
                    name: user.name,
                    provider: account?.provider,
                    provider_id: account?.providerAccountId
                });
                return true;
            } catch (error) {
                console.error("Backend Sync Failed:", error);
                return true; // Allow login even if sync fails temporarily
            }
        },
        async session({ session }) {
            return session;
        }
    },
    secret: process.env.NEXTAUTH_SECRET,
});

if (process.env.NODE_ENV === 'production' && !process.env.NEXTAUTH_SECRET) {
    throw new Error("NEXTAUTH_SECRET is required in production");
}

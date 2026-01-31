"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export interface Session {
    id: string;
    title: string;
    date: string;
    thumbnail?: string;
}

interface SessionContextType {
    sessions: Session[];
    addSession: (title: string) => void;
    removeSession: (id: string, e: React.MouseEvent) => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: React.ReactNode }) {
    const [sessions, setSessions] = useState<Session[]>([]);

    // Load from local storage on mount
    useEffect(() => {
        const saved = localStorage.getItem("ragebait_sessions");
        if (saved) {
            setSessions(JSON.parse(saved));
        } else {
            // Default Mock Data
            setSessions([
                { id: "1", title: "Golf Swing - Iron 7", date: "2 mins ago" },
                { id: "2", title: "Basketball Free Throw", date: "1 hour ago" },
            ]);
        }
    }, []);

    const addSession = (title: string) => {
        const newSession: Session = {
            id: Date.now().toString(),
            title,
            date: "Just now",
        };
        const updated = [newSession, ...sessions];
        setSessions(updated);
        localStorage.setItem("ragebait_sessions", JSON.stringify(updated));
    };

    const removeSession = (id: string, e: React.MouseEvent) => {
        e.preventDefault(); // Prevent navigation
        e.stopPropagation();
        const updated = sessions.filter(s => s.id !== id);
        setSessions(updated);
        localStorage.setItem("ragebait_sessions", JSON.stringify(updated));
    };

    return (
        <SessionContext.Provider value={{ sessions, addSession, removeSession }}>
            {children}
        </SessionContext.Provider>
    );
}

export function useSessions() {
    const context = useContext(SessionContext);
    if (context === undefined) {
        throw new Error("useSessions must be used within a SessionProvider");
    }
    return context;
}

"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
    History,
    PlusCircle,
    Settings,
    User,
    Trophy,
    Menu,
    Sparkles,
    Search,
    Trash2
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet";

import { useSessions } from "@/lib/session-context";

export function Sidebar({ className }: { className?: string }) {
    const pathname = usePathname();
    const { sessions, removeSession } = useSessions();

    return (
        <div className={cn("pb-12 h-screen border-r border-sidebar-border bg-sidebar text-sidebar-foreground flex flex-col backdrop-blur-xl bg-opacity-90", className)}>
            <div className="space-y-4 py-4">
                <div className="px-4 py-2">
                    <Link href="/" className="flex items-center gap-2 mb-8">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                            <Sparkles className="h-5 w-5 text-white fill-white" />
                        </div>
                        <span className="text-xl font-semibold tracking-tight">rageb<span className="text-primary">AI</span>t</span>
                    </Link>
                    <div className="grid gap-2">
                        <Link href="/">
                            <Button variant={pathname === "/" ? "secondary" : "ghost"} className="w-full justify-start gap-2">
                                <PlusCircle className="h-4 w-4" />
                                New Analysis
                            </Button>
                        </Link>
                        <Link href="/browser">
                            <Button variant={pathname === "/browser" ? "secondary" : "ghost"} className="w-full justify-start gap-2">
                                <Search className="h-4 w-4" />
                                Browser Search
                            </Button>
                        </Link>
                    </div>
                </div>
                <div className="px-4 py-2">
                    <h2 className="mb-2 px-2 text-xs font-semibold tracking-tight text-white/40 uppercase">
                        History
                    </h2>
                    <ScrollArea className="h-[300px] px-2">
                        <div className="space-y-1">
                            {sessions.map((item) => (
                                <div key={item.id} className="relative group">
                                    <Link href={`/result/${item.id}`}>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className={cn(
                                                "w-full justify-start text-sm font-normal text-white/70 hover:text-white hover:bg-white/5 pr-8",
                                                pathname === `/result/${item.id}` ? "bg-white/10 text-white" : ""
                                            )}
                                        >
                                            <History className="mr-2 h-4 w-4 opacity-70" />
                                            <span className="truncate max-w-[140px]">{item.title}</span>
                                        </Button>
                                    </Link>
                                    <button
                                        onClick={(e) => removeSession(item.id, e)}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 rounded-md transition-all text-white/40 hover:text-red-500"
                                    >
                                        <Trash2 className="w-3 h-3" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </ScrollArea>
                </div>
            </div>

            <div className="mt-auto px-4 py-4 border-t border-white/5 bg-black/20">
                <div className="space-y-1">
                    <Button variant="ghost" className="w-full justify-start gap-2 text-white/60 hover:text-white hover:bg-white/5">
                        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-[10px] text-white font-bold">
                            V
                        </div>
                        Vatsala Jha
                    </Button>
                </div>
            </div>
        </div>
    );
}

export function MobileNav() {
    return (
        <Sheet>
            <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden fixed top-4 left-4 z-50 text-white">
                    <Menu className="h-6 w-6" />
                </Button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 bg-sidebar border-sidebar-border w-72">
                <SheetTitle className="sr-only">Navigation Menu</SheetTitle>
                <Sidebar />
            </SheetContent>
        </Sheet>
    )
}

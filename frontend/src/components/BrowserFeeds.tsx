"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Twitter, Newspaper, ArrowUpRight } from "lucide-react";

// Mock Data representing what "Browser Use" would fetch
const LIVE_FEED = [
    {
        id: 1,
        source: "twitter",
        user: "@NBAMemes",
        content: "LeBron just missed a dunk at age 40. Father Time is undefeated. 💀 #NBA #Lakers",
        time: "2m ago",
        sentiment: "negative"
    },
    {
        id: 2,
        source: "news",
        user: "ESPN",
        content: "BREAKING: Chiefs quarterback Patrick Mahomes seen practicing left-handed throws ahead of Super Bowl.",
        time: "10m ago",
        sentiment: "neutral"
    },
    {
        id: 3,
        source: "twitter",
        user: "@GolfDigest",
        content: "You won't believe this swing from the Am-Am tour. Looks like he's chopping wood! 🪓",
        time: "15m ago",
        sentiment: "negative"
    }
];

export function BrowserFeeds() {
    const [feeds, setFeeds] = useState(LIVE_FEED);

    return (
        <Card className="bg-white/5 border-white/10 backdrop-blur-md p-6 h-full flex flex-col">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                    <div className="relative">
                        <div className="w-3 h-3 bg-red-500 rounded-full animate-ping absolute" />
                        <div className="w-3 h-3 bg-red-500 rounded-full relative" />
                    </div>
                    <h3 className="font-bold text-white tracking-wide font-oswald">LIVE BROWSER AGENT</h3>
                </div>
                <Badge variant="outline" className="text-xs font-mono text-white/50 border-white/10">
                    SCANNING X.COM...
                </Badge>
            </div>

            <ScrollArea className="flex-1 -mr-4 pr-4">
                <div className="space-y-4">
                    {feeds.map((item) => (
                        <div key={item.id} className="p-4 rounded-xl bg-black/20 border border-white/5 hover:border-primary/30 transition-colors group">
                            <div className="flex justify-between items-start mb-2">
                                <div className="flex items-center gap-2">
                                    {item.source === "twitter" ? (
                                        <Twitter className="w-4 h-4 text-blue-400" />
                                    ) : (
                                        <Newspaper className="w-4 h-4 text-purple-400" />
                                    )}
                                    <span className="text-xs font-bold text-white/70">{item.user}</span>
                                </div>
                                <span className="text-[10px] text-white/30 font-mono">{item.time}</span>
                            </div>
                            <p className="text-sm text-white/90 leading-relaxed mb-3">
                                {item.content}
                            </p>
                            <div className="flex justify-end">
                                <Button size="sm" variant="ghost" className="h-6 text-[10px] text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                                    GENERATE REACT <ArrowUpRight className="ml-1 w-3 h-3" />
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            </ScrollArea>
        </Card>
    );
}

"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, Youtube, Twitter, Instagram, Globe } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function BrowserSearchPage() {
    const [query, setQuery] = useState("");
    const [platform, setPlatform] = useState("youtube");
    const [isSearching, setIsSearching] = useState(false);
    const [results, setResults] = useState<any[]>([]);

    const handleSearch = () => {
        setIsSearching(true);
        // Mock Search Results
        setTimeout(() => {
            setResults([
                { id: 1, title: "Top 10 Golf Fails 2024", thumbnail: "https://placehold.co/300x200/png?text=Golf+Fail", source: "YouTube", url: "#" },
                { id: 2, title: "Charles Barkley Swing Roast", thumbnail: "https://placehold.co/300x200/png?text=Barkley", source: "YouTube", url: "#" },
                { id: 3, title: "Shannon Sharpe on Lebron", thumbnail: "https://placehold.co/300x200/png?text=Shannon", source: "YouTube", url: "#" },
            ]);
            setIsSearching(false);
        }, 1500);
    };

    return (
        <div className="min-h-screen bg-background p-8 max-w-6xl mx-auto space-y-8">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
                <h1 className="text-4xl font-bold tracking-tight font-oswald text-white flex items-center gap-3">
                    <Globe className="w-10 h-10 text-primary" />
                    BROWSER AGENT SEARCH
                </h1>
                <p className="text-xl text-muted-foreground max-w-2xl">
                    Deploy our autonomous agent to scour the web for content to roast.
                </p>
            </div>

            {/* Search Bar */}
            <Card className="p-6 bg-white/5 border-white/10 backdrop-blur-md">
                <div className="flex flex-col md:flex-row gap-4">
                    <Select value={platform} onValueChange={setPlatform}>
                        <SelectTrigger className="w-[180px] h-12 bg-black/50 border-white/10">
                            <SelectValue placeholder="Platform" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="youtube">
                                <div className="flex items-center"><Youtube className="w-4 h-4 mr-2 text-red-500" /> YouTube</div>
                            </SelectItem>
                            <SelectItem value="twitter">
                                <div className="flex items-center"><Twitter className="w-4 h-4 mr-2 text-blue-400" /> Twitter / X</div>
                            </SelectItem>
                            <SelectItem value="instagram">
                                <div className="flex items-center"><Instagram className="w-4 h-4 mr-2 text-pink-500" /> Instagram</div>
                            </SelectItem>
                            <SelectItem value="reddit">
                                <div className="flex items-center"><span className="w-4 h-4 mr-2 text-orange-500 font-bold">R</span> Reddit</div>
                            </SelectItem>
                        </SelectContent>
                    </Select>
                    <div className="flex-1 relative">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                        <Input
                            placeholder="Search query (e.g., 'Basketball airballs', 'Golf slice corrections')..."
                            className="pl-12 h-12 bg-black/50 border-white/10 text-lg"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                        />
                    </div>
                    <Button size="lg" className="h-12 px-8 text-lg font-bold bg-primary hover:bg-primary/90" onClick={handleSearch} disabled={isSearching}>
                        {isSearching ? "DEPLOYING AGENT..." : "SEARCH"}
                    </Button>
                </div>
            </Card>

            {/* Results Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.map((result) => (
                    <Card key={result.id} className="overflow-hidden bg-black/40 border-white/10 group cursor-pointer hover:border-primary/50 transition-colors">
                        <div className="relative aspect-video">
                            <img src={result.thumbnail} alt={result.title} className="w-full h-full object-cover" />
                            <Badge className="absolute top-2 right-2 bg-red-600">Video</Badge>
                        </div>
                        <div className="p-4 space-y-2">
                            <div className="flex items-center justify-between text-xs text-muted-foreground">
                                <span className="flex items-center gap-1"><Youtube className="w-3 h-3" /> {result.source}</span>
                                <span>2 hours ago</span>
                            </div>
                            <h3 className="font-bold text-white group-hover:text-primary transition-colors line-clamp-2">{result.title}</h3>
                            <Button variant="secondary" className="w-full mt-2">Analyze This Clip</Button>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
}

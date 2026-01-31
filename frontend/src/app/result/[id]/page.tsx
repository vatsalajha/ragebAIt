"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ArrowLeft, Download, RefreshCw, Share2, UploadCloud, Image, Copy, Check } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

import { api, RoastResult } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function ResultPage() {
    const params = useParams();
    const id = params.id as string;

    const [status, setStatus] = useState<"processing" | "completed" | "failed">("processing");
    const [result, setResult] = useState<RoastResult | null>(null);
    const [isRegeneratingMeme, setIsRegeneratingMeme] = useState(false);
    const [copied, setCopied] = useState(false);

    // Polling Logic
    useEffect(() => {
        let interval: NodeJS.Timeout;
        let attempts = 0;
        const maxAttempts = 200; // ~10 minutes with 3s interval

        const checkStatus = async () => {
            attempts++;
            const data = await api.getRoastStatus(id);
            setResult(data);
            setStatus(data.status);

            if (data.status === "completed" || data.status === "failed" || attempts >= maxAttempts) {
                clearInterval(interval);
                if (attempts >= maxAttempts && data.status === "processing") {
                    setStatus("failed");
                    toast.error("Generation timed out. Please try again.");
                }
            }
        };

        // Initial check
        checkStatus();
        // Poll every 3 seconds
        interval = setInterval(checkStatus, 3000);

        return () => clearInterval(interval);
    }, [id]);

    const handleDownload = () => {
        if (result?.video_url) {
            const a = document.createElement('a');
            a.href = result.video_url;
            a.download = `ragebait-${id}.mp4`;
            a.target = '_blank';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            toast.success("Download started!");
        }
    };

    const handleRegenerateMeme = async () => {
        if (!result?.job_id) return;
        
        setIsRegeneratingMeme(true);
        try {
            const memeResult = await api.generateMeme(result.job_id);
            setResult(prev => prev ? {
                ...prev,
                meme_url: memeResult.meme_url,
                caption: memeResult.caption,
            } : null);
            toast.success("New meme generated!");
        } catch (error) {
            toast.error("Failed to regenerate meme");
        } finally {
            setIsRegeneratingMeme(false);
        }
    };

    const handleCopyCaption = () => {
        if (result?.caption) {
            navigator.clipboard.writeText(result.caption);
            setCopied(true);
            toast.success("Caption copied!");
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const handleShareToTwitter = () => {
        const text = result?.caption || "Check out this AI-generated sports roast! 🔥";
        const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
        window.open(url, '_blank');
    };

    return (
        <div className="h-full flex flex-col p-6 max-w-[1800px] mx-auto space-y-6">

            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/">
                        <Button variant="ghost" className="text-white hover:text-primary hover:bg-white/5">
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Back
                        </Button>
                    </Link>
                    <h1 className="text-2xl font-bold font-oswald text-white tracking-wide">
                        {status === "completed" ? "🔥 RAGEBAIT READY" : status === "failed" ? "❌ GENERATION FAILED" : "⏳ COOKING..."}
                    </h1>
                </div>
                <div className="flex gap-2">
                    <Button 
                        className="bg-[#1DA1F2] hover:bg-[#1DA1F2]/90 text-white border-0"
                        onClick={handleShareToTwitter}
                        disabled={status !== "completed"}
                    >
                        <Share2 className="w-4 h-4 mr-2" />
                        Share to X
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">

                {/* Left: Final Video */}
                <div className="lg:col-span-7 flex flex-col space-y-4">
                    <Card className="flex-1 bg-black border-white/10 relative overflow-hidden group shadow-2xl rounded-2xl min-h-[400px]">
                        <Badge className={cn(
                            "absolute top-4 left-4 z-10 transition-colors duration-500",
                            status === "completed" ? "bg-green-600" : 
                            status === "failed" ? "bg-red-600" : 
                            "bg-yellow-600 animate-pulse"
                        )}>
                            {status === "completed" ? "✅ READY TO DOWNLOAD" : 
                             status === "failed" ? "FAILED" : 
                             "🔥 GENERATING RAGEBAIT..."}
                        </Badge>

                        {result?.video_url ? (
                            <video
                                id="main-video"
                                src={result.video_url}
                                key={result.video_url}
                                className="w-full h-full object-contain"
                                controls
                                autoPlay
                            />
                        ) : status === "failed" ? (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-red-400 gap-4 p-6">
                                <div className="text-6xl">😢</div>
                                <div className="text-center">
                                    <p className="text-lg font-semibold">Generation Failed</p>
                                    <p className="text-sm text-white/50 mt-2">
                                        {result?.error || "Something went wrong. Please try again."}
                                    </p>
                                    <Link href="/">
                                        <Button className="mt-4">Try Again</Button>
                                    </Link>
                                </div>
                            </div>
                        ) : (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-white/30 gap-4">
                                <UploadCloud className="w-16 h-16 animate-bounce" />
                                <div className="text-center">
                                    <p className="text-lg font-semibold">Processing your video...</p>
                                    <p className="text-sm text-white/50">Finding the funniest scene & adding commentary</p>
                                    <p className="text-xs text-white/30 mt-2">This usually takes 2-5 minutes</p>
                                </div>
                            </div>
                        )}
                    </Card>
                    
                    <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                        <div>
                            <div className="text-sm font-medium text-white">
                                {status === "completed" ? `Complete Scene Extracted (${result?.duration?.toFixed(1)}s)` : 
                                 status === "failed" ? "Generation Failed" :
                                 "AI Processing..."}
                            </div>
                            <div className="text-xs text-white/50">
                                {result?.lens ? `Lens: ${result.lens}` : "Gemini 3 Flash + fal.ai TTS"}
                            </div>
                        </div>
                        <Button
                            variant="outline"
                            className="border-white/10 hover:bg-white/10"
                            onClick={handleDownload}
                            disabled={status !== "completed"}
                        >
                            <Download className="w-4 h-4 mr-2" />
                            {status === "completed" ? "Download Video" : "Processing..."}
                        </Button>
                    </div>
                </div>

                {/* Right: Meme & Commentary Log */}
                <div className="lg:col-span-5 flex flex-col space-y-6">

                    {/* Generated Meme Section */}
                    <div className="flex-1 min-h-[300px]">
                        <Card className="h-full bg-white/5 border-white/10 p-4 flex flex-col">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-bold font-oswald text-white tracking-wide flex items-center gap-2">
                                    <Image className="w-5 h-5 text-yellow-500" />
                                    GENERATED MEME
                                </h3>
                                <Badge variant="outline" className="border-yellow-500/50 text-yellow-500">
                                    Nano Banana AI
                                </Badge>
                            </div>
                            <div className="flex-1 bg-black/40 rounded-lg overflow-hidden relative group flex items-center justify-center">
                                {result?.meme_url ? (
                                    <div className="relative w-full h-full">
                                        <img 
                                            src={result.meme_url} 
                                            alt="Generated Meme" 
                                            className="w-full h-full object-contain" 
                                        />
                                        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                                            <Button 
                                                variant="secondary" 
                                                onClick={handleRegenerateMeme}
                                                disabled={isRegeneratingMeme}
                                            >
                                                <RefreshCw className={cn("w-4 h-4 mr-2", isRegeneratingMeme && "animate-spin")} />
                                                Regenerate
                                            </Button>
                                            <Button asChild>
                                                <a href={result.meme_url} download target="_blank">
                                                    <Download className="w-4 h-4 mr-2" />
                                                    Save
                                                </a>
                                            </Button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-center p-6 space-y-2">
                                        <Image className="w-8 h-8 text-white/20 mx-auto animate-pulse" />
                                        <p className="text-sm text-white/40">
                                            {status === "completed" ? "Meme generation in progress..." : "Waiting for video..."}
                                        </p>
                                    </div>
                                )}
                            </div>

                            {/* Caption */}
                            {result?.caption && (
                                <div className="mt-4 p-3 bg-black/30 rounded-lg border border-white/10">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs text-white/50 uppercase tracking-wider">Social Caption</span>
                                        <Button 
                                            variant="ghost" 
                                            size="sm" 
                                            className="h-6 px-2"
                                            onClick={handleCopyCaption}
                                        >
                                            {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                        </Button>
                                    </div>
                                    <p className="text-sm text-white/80">{result.caption}</p>
                                </div>
                            )}
                        </Card>
                    </div>

                    {/* Roast Log (Transcript) */}
                    <div className="h-[250px]">
                        <Card className="h-full flex flex-col bg-white/5 border-white/10">
                            <div className="p-3 border-b border-white/10 flex justify-between items-center">
                                <h3 className="text-sm font-semibold text-white/70">🎙️ Commentary Transcript</h3>
                                {status === "processing" && (
                                    <span className="text-xs text-primary animate-pulse">Generating...</span>
                                )}
                            </div>
                            <ScrollArea className="flex-1 p-4">
                                <div className="space-y-3 text-sm">
                                    {result?.transcript && result.transcript.length > 0 ? (
                                        result.transcript.map((line, i) => (
                                            <p key={i} className="text-white/90">
                                                <span className="text-primary font-mono mr-2 text-xs">[{line.timestamp}]</span>
                                                {line.text}
                                            </p>
                                        ))
                                    ) : (
                                        <div className="space-y-3 opacity-30">
                                            <div className="h-4 w-3/4 bg-white/20 rounded animate-pulse" />
                                            <div className="h-4 w-1/2 bg-white/20 rounded animate-pulse delay-75" />
                                            <div className="h-4 w-5/6 bg-white/20 rounded animate-pulse delay-150" />
                                        </div>
                                    )}
                                </div>
                            </ScrollArea>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}

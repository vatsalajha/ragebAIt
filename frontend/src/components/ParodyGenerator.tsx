"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
    Video,
    Sparkles,
    Loader2,
    Play,
    Zap,
    Camera,
    Tv
} from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface ParodyGeneratorProps {
    videoId: string;
    memeUrl?: string;
    onParodyGenerated?: (videoUrl: string) => void;
}

const MOTION_DIRECTIVES = [
    {
        id: "shake",
        label: "Camera Shake",
        directive: "subtle handheld broadcast camera shake",
        icon: <Camera className="w-4 h-4" />,
        description: "Handheld broadcast feel"
    },
    {
        id: "zoom",
        label: "Stadium Flicker",
        directive: "slow zoom-in, stadium lights flicker slightly",
        icon: <Sparkles className="w-4 h-4" />,
        description: "Dramatic zoom with lighting"
    },
    {
        id: "stutter",
        label: "Replay Stutter",
        directive: "quick 0.5s replay stutter then smooth",
        icon: <Zap className="w-4 h-4" />,
        description: "Classic sports replay glitch"
    },
    {
        id: "fixed",
        label: "TV Graphics",
        directive: "overlay remains fixed, like TV graphics",
        icon: <Tv className="w-4 h-4" />,
        description: "Clean broadcast overlay look"
    }
];

export function ParodyGenerator({ videoId, memeUrl, onParodyGenerated }: ParodyGeneratorProps) {
    const [isGenerating, setIsGenerating] = useState(false);
    const [selectedDirective, setSelectedDirective] = useState(MOTION_DIRECTIVES[0].id);
    const [parodyUrl, setParodyUrl] = useState<string | null>(null);

    const handleGenerate = async () => {
        setIsGenerating(true);
        const directive = MOTION_DIRECTIVES.find(d => d.id === selectedDirective)?.directive || "";

        try {
            const result = await api.generateParody(videoId, directive, memeUrl);
            setParodyUrl(result.video_url);
            toast.success("Parody video generated!");
            if (onParodyGenerated) onParodyGenerated(result.video_url);
        } catch (error) {
            console.error("Parody generation failed:", error);
            toast.error("Failed to generate parody video");
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <Card className="bg-white/5 border-white/10 p-4 space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="font-bold font-oswald text-white tracking-wide flex items-center gap-2">
                    <Video className="w-5 h-5 text-primary" />
                    CREATE PARODY
                </h3>
                <div className="flex items-center gap-1">
                    <span className="text-[10px] text-white/30 uppercase font-bold px-1.5 py-0.5 rounded border border-white/5 bg-white/5">fal.ai Image to Video</span>
                </div>
            </div>

            <p className="text-xs text-white/50">
                Transform this moment into a viral parody clip.
            </p>

            <div className="grid grid-cols-2 gap-2">
                {MOTION_DIRECTIVES.map((d) => (
                    <button
                        key={d.id}
                        onClick={() => setSelectedDirective(d.id)}
                        className={cn(
                            "flex flex-col items-start p-3 rounded-lg border text-left transition-all",
                            selectedDirective === d.id
                                ? "bg-primary/20 border-primary text-white"
                                : "bg-white/5 border-white/10 text-white/60 hover:bg-white/10"
                        )}
                    >
                        <div className="flex items-center gap-2 mb-1">
                            {d.icon}
                            <span className="text-xs font-bold uppercase tracking-tight">{d.label}</span>
                        </div>
                        <span className="text-[10px] opacity-70 leading-tight">{d.description}</span>
                    </button>
                ))}
            </div>

            {!parodyUrl ? (
                <Button
                    className="w-full bg-primary hover:bg-primary/90 text-black font-bold h-12"
                    onClick={handleGenerate}
                    disabled={isGenerating}
                >
                    {isGenerating ? (
                        <>
                            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                            GENERATING PARODY...
                        </>
                    ) : (
                        <>
                            <Sparkles className="w-5 h-5 mr-2" />
                            GENERATE PARODY VIDEO
                        </>
                    )}
                </Button>
            ) : (
                <div className="space-y-4">
                    <div className="aspect-video w-full bg-black rounded-lg overflow-hidden border border-white/10 relative group">
                        <video
                            src={parodyUrl}
                            className="w-full h-full object-contain"
                            controls
                        />
                        <div className="absolute top-2 right-2">
                            <Button size="sm" variant="secondary" onClick={() => setParodyUrl(null)}>
                                New Parody
                            </Button>
                        </div>
                    </div>
                    <Button variant="outline" className="w-full border-white/10 hover:bg-white/10" asChild>
                        <a href={parodyUrl} download target="_blank">
                            Save Parody to Disk
                        </a>
                    </Button>
                </div>
            )}
        </Card>
    );
}

export default ParodyGenerator;

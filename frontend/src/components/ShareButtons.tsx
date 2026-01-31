"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Share2, Twitter, Facebook, Link as LinkIcon } from "lucide-react";

interface ShareButtonsProps {
    videoId: string;
    title: string;
}

export function ShareButtons({ videoId, title }: ShareButtonsProps) {
    const shareUrl = typeof window !== 'undefined' ? `${window.location.origin}/result/${videoId}` : '';
    const shareText = `Check out this roast! ${title} #ragebAIt`;

    const handleCopyLink = () => {
        navigator.clipboard.writeText(shareUrl);
        alert("Link copied to clipboard!");
    };

    const handleTwitterShare = () => {
        window.open(
            `https://twitter.com/intent/tweet?text=${encodeURIComponent(
                shareText
            )}&url=${encodeURIComponent(shareUrl)}`,
            "_blank"
        );
    };

    return (
        <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleCopyLink}>
                <LinkIcon className="w-4 h-4 mr-2" />
                Copy Link
            </Button>
            <Button variant="outline" size="sm" onClick={handleTwitterShare}>
                <Twitter className="w-4 h-4 mr-2" />
                Twitter
            </Button>
            <Button variant="outline" size="sm" disabled>
                <Facebook className="w-4 h-4 mr-2" />
                Facebook
            </Button>
        </div>
    );
}

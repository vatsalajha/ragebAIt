"use client";

import React, { useState } from "react";
import { VideoUploader } from "@/components/VideoUploader";
import { LensSelector } from "@/components/LensSelector";
import { BrowserFeeds } from "@/components/BrowserFeeds";
import { Button } from "@/components/ui/button";
import { Loader2, Zap, AlertCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

import { useSessions } from "@/lib/session-context";
import { api } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const { addSession } = useSessions();
  const [file, setFile] = useState<File | null>(null);
  const [selectedLens, setSelectedLens] = useState<string>("nature_documentary");
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState<string>("");

  const handleGenerate = async () => {
    if (!file) {
      toast.error("Please upload a video first");
      return;
    }

    setIsGenerating(true);
    setProgress("Uploading video...");

    try {
      // Start the generation job
      toast.info("Starting video analysis... This may take 2-5 minutes.");
      setProgress("🔍 Finding funny scenes in video...");

      const { job_id } = await api.startRoast(file, selectedLens);

      // Create session entry
      const title = `${file.name} - ${selectedLens}`;
      addSession(title);

      // Navigate to result page
      setProgress("Redirecting to results...");
      router.push(`/result/${job_id}`);
      
    } catch (error) {
      console.error("Generation failed:", error);
      toast.error(error instanceof Error ? error.message : "Generation failed");
      setIsGenerating(false);
      setProgress("");
    }
  };

  return (
    <div className="h-full flex flex-col p-6 max-w-[1600px] mx-auto">
      <header className="mb-12 text-center md:text-left">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-5xl font-bold tracking-tight text-white mb-2 bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent"
        >
          ragebAIt <span className="text-primary font-normal">🔥</span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-xl text-white/60 font-light"
        >
          AI Sports Ragebait Generator - Turn clips into viral content
        </motion.p>
      </header>

      <div className="grid lg:grid-cols-12 gap-8 flex-1">
        {/* Left Column: Input (Video/URL) */}
        <div className="lg:col-span-4 space-y-8">
          <section className="bg-white/5 border border-white/10 rounded-2xl p-1 backdrop-blur-md h-full flex flex-col">
            <Tabs defaultValue="upload" className="w-full flex-1 flex flex-col">
              <TabsList className="w-full bg-transparent border-b border-white/5 justify-start h-14 p-0">
                <TabsTrigger value="upload" className="h-full px-8 data-[state=active]:bg-white/5 data-[state=active]:text-white data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none">
                  Upload
                </TabsTrigger>
                <TabsTrigger value="url" className="h-full px-8 data-[state=active]:bg-white/5 data-[state=active]:text-white data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none">
                  Paste URL
                </TabsTrigger>
              </TabsList>
              <div className="p-6 flex-1">
                <TabsContent value="upload" className="mt-0 h-full">
                  <VideoUploader onFileSelect={setFile} />
                </TabsContent>
                <TabsContent value="url" className="mt-0 space-y-4">
                  <div className="p-8 border-2 border-dashed border-white/10 rounded-xl bg-white/5 flex flex-col items-center justify-center text-center gap-4 min-h-[300px]">
                    <p className="text-white/60 max-w-sm">
                      Paste a link from Twitter, YouTube, or TikTok. Our Browser Agent will fetch it for you.
                    </p>
                    <div className="flex w-full max-w-md gap-2">
                      <Input placeholder="https://x.com/user/status/123..." className="bg-black/50 border-white/10" />
                      <Button variant="secondary">Fetch</Button>
                    </div>
                  </div>
                </TabsContent>
              </div>
            </Tabs>
          </section>
        </div>

        {/* Middle Column: Selection & Summary */}
        <div className="lg:col-span-5 space-y-8">
          <LensSelector
            selectedLens={selectedLens}
            onSelectLens={setSelectedLens}
          />

          <div className="bg-gradient-to-br from-primary/20 to-purple-900/20 border border-primary/20 rounded-2xl p-6 backdrop-blur-md">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium text-white">
                {isGenerating ? "Processing..." : "Ready to Generate"}
              </h3>
              <div className="flex items-center gap-2 text-xs text-primary font-mono uppercase">
                <Zap className="w-4 h-4 fill-primary" />
                Gemini-3-Flash + fal.ai
              </div>
            </div>

            {isGenerating && progress && (
              <div className="mb-4 p-3 bg-black/30 rounded-lg border border-white/10">
                <p className="text-sm text-white/80 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  {progress}
                </p>
              </div>
            )}

            <Button
              size="lg"
              className="w-full text-lg h-14 rounded-xl bg-gradient-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90 shadow-[0_0_30px_rgba(var(--primary),0.3)] transition-all hover:scale-[1.02]"
              disabled={!file || isGenerating}
              onClick={handleGenerate}
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Generating Ragebait...
                </>
              ) : (
                "🔥 Generate Viral Clip"
              )}
            </Button>

            {!file && (
              <p className="text-xs text-white/40 text-center mt-3 flex items-center justify-center gap-1">
                <AlertCircle className="w-3 h-3" />
                Upload a video to get started
              </p>
            )}
          </div>
        </div>

        {/* Right Column: Live Browser Feeds */}
        <div className="lg:col-span-3">
          <BrowserFeeds />
        </div>
      </div>
    </div>
  );
}

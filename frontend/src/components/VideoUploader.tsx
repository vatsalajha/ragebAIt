"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileVideo, X, Zap, Image as ImageIcon } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface VideoUploaderProps {
    onFileSelect: (file: File) => void;
}

export function VideoUploader({ onFileSelect }: VideoUploaderProps) {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        const selectedFile = acceptedFiles[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            onFileSelect(selectedFile);
        }
    }, [onFileSelect]);

    const removeFile = () => {
        setFile(null);
        if (preview) URL.revokeObjectURL(preview);
        setPreview(null);
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            "video/*": [".mp4", ".mov", ".avi", ".webm"],
            "image/*": [".png", ".jpg", ".jpeg", ".webp"],
        },
        maxFiles: 1,
        maxSize: 50 * 1024 * 1024, // 50MB
    });

    return (
        <div className="w-full h-full">
            <AnimatePresence mode="wait">
                {file ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        key="preview"
                        className="h-full"
                    >
                        <Card className="relative overflow-hidden bg-black/40 border-primary/20 p-0 group h-full flex flex-col">
                            {/* Glossy Overlay */}
                            <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 to-transparent pointer-events-none" />

                            <Button
                                variant="destructive"
                                size="icon"
                                className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity"
                                onClick={removeFile}
                            >
                                <X className="w-4 h-4" />
                            </Button>

                            <div className="relative flex-1 bg-black/80 flex items-center justify-center overflow-hidden">
                                {file.type.startsWith("video") ? (
                                    <video
                                        src={preview || ""}
                                        className="w-full h-full object-contain"
                                        controls
                                    />
                                ) : (
                                    <img
                                        src={preview || ""}
                                        alt="Preview"
                                        className="w-full h-full object-contain"
                                    />
                                )}
                            </div>

                            <div className="p-4 flex items-center justify-between border-t border-white/5 bg-white/5 shrink-0">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-primary/20 rounded-md text-primary">
                                        {file.type.startsWith("video") ? <FileVideo className="w-5 h-5" /> : <ImageIcon className="w-5 h-5" />}
                                    </div>
                                    <div>
                                        <div className="text-sm font-medium text-white">{file.name}</div>
                                        <div className="text-xs text-white/50">{(file.size / (1024 * 1024)).toFixed(2)} MB</div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 text-primary text-xs font-mono uppercase tracking-wider">
                                    <Zap className="w-3 h-3" />
                                    Ready to Roast
                                </div>
                            </div>
                        </Card>
                    </motion.div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        key="dropzone"
                        className="h-full"
                    >
                        <div
                            {...getRootProps()}
                            className={cn(
                                "relative group cursor-pointer overflow-hidden rounded-xl border-2 border-dashed transition-all duration-300 h-full min-h-[300px] flex items-center justify-center",
                                isDragActive
                                    ? "border-primary bg-primary/10 scale-[1.01]"
                                    : "border-white/10 hover:border-primary/50 hover:bg-white/5"
                            )}
                        >
                            <input {...getInputProps()} />

                            {/* Scanning Effect */}
                            <div className="absolute inset-0 bg-[linear-gradient(to_bottom,transparent,rgba(var(--primary),0.1),transparent)] translate-y-[-100%] group-hover:translate-y-[100%] transition-transform duration-1000 ease-in-out" />

                            <div className="relative z-10 flex flex-col items-center gap-6 text-center p-8">
                                <div className={cn(
                                    "w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300",
                                    isDragActive ? "bg-primary text-white" : "bg-white/5 text-white/50 group-hover:text-primary group-hover:bg-primary/10"
                                )}>
                                    <Upload className="w-10 h-10" />
                                </div>

                                <div className="space-y-2">
                                    <h3 className="text-2xl font-bold font-oswald tracking-wide text-white">
                                        UPLOAD FOOTAGE
                                    </h3>
                                    <p className="text-white/60 max-w-xs mx-auto">
                                        Drag & drop your sports fail (video) or bad form (image) here.
                                    </p>
                                </div>

                                <div className="flex items-center gap-4 text-xs font-mono text-white/40 uppercase tracking-widest">
                                    <span>MP4</span>
                                    <span>JPG</span>
                                    <span>PNG</span>
                                    <span>Max 50MB</span>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

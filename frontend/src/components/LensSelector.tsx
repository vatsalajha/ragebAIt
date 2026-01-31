"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { Check, Skull, BookOpen, Clapperboard, ChefHat, Theater, Briefcase, Radio } from "lucide-react";

// Match backend lens IDs from backend/prompts/lenses.py
export const LENSES = [
    { id: "nature_documentary", name: "Nature Doc", icon: BookOpen, description: "David Attenborough narrates the wild." },
    { id: "heist_movie", name: "Heist Movie", icon: Clapperboard, description: "High stakes thriller narration." },
    { id: "alien_anthropologist", name: "Alien Study", icon: Skull, description: "Confused alien observing humans." },
    { id: "cooking_show", name: "Cooking Show", icon: ChefHat, description: "Chef's kiss! Magnifico!" },
    { id: "shakespearean", name: "Shakespeare", icon: Theater, description: "Dramatic tragedy of sports." },
    { id: "corporate_meeting", name: "Corporate", icon: Briefcase, description: "Let's circle back on that play." },
    { id: "true_crime", name: "True Crime", icon: Radio, description: "Suspenseful podcast style." },
];

interface LensSelectorProps {
    selectedLens: string;
    onSelectLens: (lensId: string) => void;
}

export function LensSelector({ selectedLens, onSelectLens }: LensSelectorProps) {
    return (
        <div className="w-full space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold font-oswald tracking-wide flex items-center gap-2 text-white">
                    <span className="w-1 h-6 bg-primary rounded-full" />
                    SELECT COMMENTARY STYLE
                </h2>
                <span className="text-xs text-white/40 font-mono">STEP 02</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-3">
                {LENSES.map((lens) => {
                    const isSelected = selectedLens === lens.id;
                    const Icon = lens.icon;

                    return (
                        <motion.div
                            key={lens.id}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => onSelectLens(lens.id)}
                            className={cn(
                                "relative cursor-pointer overflow-hidden rounded-xl border-2 transition-all duration-300 h-full",
                                isSelected
                                    ? "border-primary bg-primary/10 shadow-[0_0_20px_rgba(var(--primary),0.3)]"
                                    : "border-white/10 bg-white/5 hover:border-white/30 hover:bg-white/10"
                            )}
                        >
                            {isSelected && (
                                <div className="absolute top-2 right-2 p-1 bg-primary rounded-full z-10">
                                    <Check className="w-3 h-3 text-white" />
                                </div>
                            )}

                            <div className="p-3 flex flex-col items-center text-center gap-2 h-full">
                                <Icon className={cn("w-8 h-8 transition-colors", isSelected ? "text-primary" : "text-white")} />
                                <div>
                                    <div className="font-bold text-xs text-white">{lens.name}</div>
                                    <div className="text-[9px] text-white/50 leading-tight mt-1 line-clamp-2">
                                        {lens.description}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}

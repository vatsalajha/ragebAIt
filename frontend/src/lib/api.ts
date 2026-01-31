// API TYPES
export interface CommentarySegment {
  start_time: number;
  end_time: number;
  text: string;
  emotion: string;
}

export interface GenerateResult {
  video_id: string;
  video_url: string;
  thumbnail_url?: string;
  commentary_segments: CommentarySegment[];
  lens: string;
  duration: number;
}

export interface MemeResult {
  meme_id: string;
  meme_url: string;
  caption: string;
  style: string;
  image_prompt: string;
}

export interface RoastResult {
  job_id: string;
  status: "processing" | "completed" | "failed";
  video_url?: string;
  thumbnail_url?: string;
  meme_url?: string;
  caption?: string;
  transcript?: { timestamp: string; text: string }[];
  duration?: number;
  lens?: string;
  error?: string;
}

// Always use direct backend URL to avoid proxy timeouts on long requests
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Store results in memory (for the session)
const resultCache: Record<string, RoastResult> = {};

// Map frontend job IDs to backend video IDs
const jobToVideoId: Record<string, string> = {};

export const api = {
  /**
   * Generate ragebait video with commentary
   * NOTE: This is a long-running request (2-5 minutes)
   * Uses AbortController with 10 minute timeout
   */
  generateVideo: async (file: File, lensId: string): Promise<GenerateResult> => {
    const formData = new FormData();
    formData.append("video", file);
    formData.append("lens", lensId);

    // 10 minute timeout for long video processing
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10 * 60 * 1000);

    try {
      const response = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Generation failed: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === "AbortError") {
        throw new Error("Request timed out after 10 minutes");
      }
      throw error;
    }
  },

  /**
   * Start video generation and store result
   * Returns job_id immediately, stores result in cache when done
   */
  startRoast: async (file: File, lensId: string): Promise<{ job_id: string }> => {
    // Generate a temporary job ID
    const jobId = `job_${Date.now()}`;
    
    // Store initial processing state
    resultCache[jobId] = {
      job_id: jobId,
      status: "processing",
    };

    console.log(`[API] Starting generation job: ${jobId}`);

    // Start the long-running request in background
    api.generateVideo(file, lensId)
      .then(async (data) => {
        console.log(`[API] Generation completed! Video ID: ${data.video_id}`);
        
        // Map job ID to video ID for future lookups
        jobToVideoId[jobId] = data.video_id;

        // Try to generate meme automatically
        let memeResult: MemeResult | null = null;
        try {
          console.log(`[API] Generating meme for video: ${data.video_id}`);
          memeResult = await api.generateMeme(data.video_id);
          console.log(`[API] Meme generated: ${memeResult.meme_url}`);
        } catch (e) {
          console.warn("[API] Meme generation failed:", e);
        }

        // Update cache with completed result
        resultCache[jobId] = {
          job_id: data.video_id,
          status: "completed",
          video_url: data.video_url,
          thumbnail_url: data.thumbnail_url,
          meme_url: memeResult?.meme_url,
          caption: memeResult?.caption,
          duration: data.duration,
          lens: data.lens,
          transcript: data.commentary_segments.map((s) => ({
            timestamp: `${s.start_time.toFixed(1)}s`,
            text: s.text,
          })),
        };

        console.log(`[API] Job ${jobId} completed successfully`);
      })
      .catch((error) => {
        console.error(`[API] Generation failed for job ${jobId}:`, error);
        resultCache[jobId] = {
          job_id: jobId,
          status: "failed",
          error: error instanceof Error ? error.message : "Unknown error",
        };
      });

    return { job_id: jobId };
  },

  /**
   * Get the status/result of a roast job
   */
  getRoastStatus: async (jobId: string): Promise<RoastResult> => {
    // Check cache first
    if (resultCache[jobId]) {
      return resultCache[jobId];
    }

    // Check if this job ID maps to a video ID we know about
    const videoId = jobToVideoId[jobId];
    if (videoId) {
      try {
        const response = await fetch(`${API_BASE}/api/video/${videoId}`);
        if (response.ok) {
          const data = await response.json();
          return {
            job_id: data.video_id,
            status: "completed",
            video_url: data.video_url,
            duration: data.duration,
            lens: data.lens,
            transcript: data.segments?.map((s: CommentarySegment) => ({
              timestamp: `${s.start_time.toFixed(1)}s`,
              text: s.text,
            })) || [],
          };
        }
      } catch {
        // Fall through to processing state
      }
    }

    // Try to fetch directly from backend (if jobId is actually a video_id)
    try {
      const response = await fetch(`${API_BASE}/api/video/${jobId}`);
      
      if (!response.ok) {
        return { job_id: jobId, status: "processing" };
      }

      const data = await response.json();
      
      return {
        job_id: data.video_id,
        status: "completed",
        video_url: data.video_url,
        duration: data.duration,
        lens: data.lens,
        transcript: data.segments?.map((s: CommentarySegment) => ({
          timestamp: `${s.start_time.toFixed(1)}s`,
          text: s.text,
        })) || [],
      };
    } catch {
      return { job_id: jobId, status: "processing" };
    }
  },

  /**
   * Generate a meme from a video frame using Nano Banana
   */
  generateMeme: async (videoId: string, frameIndex?: number): Promise<MemeResult> => {
    const response = await fetch(`${API_BASE}/api/meme/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        video_id: videoId,
        frame_index: frameIndex 
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Meme generation failed: ${errorText}`);
    }

    return await response.json();
  },

  /**
   * Get available lenses from the backend
   */
  getLenses: async () => {
    const response = await fetch(`${API_BASE}/api/lenses`);
    return await response.json();
  },

  /**
   * Health check
   */
  healthCheck: async () => {
    const response = await fetch(`${API_BASE}/api/health`);
    return await response.json();
  },

  /**
   * Get saved sessions from localStorage
   */
  getSessions: async () => {
    if (typeof window === "undefined") return [];
    const saved = localStorage.getItem("ragebait_sessions");
    return saved ? JSON.parse(saved) : [];
  },
};

// Legacy export for compatibility
export async function generateMeme(videoId: string) {
  return api.generateMeme(videoId);
}

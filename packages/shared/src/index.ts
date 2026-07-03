export type Provenance =
  | "ai_generated"
  | "uploaded"
  | "remix"
  | "cover"
  | "repaint"
  | "stems"
  | "vocal_to_bgm";

export type JobStatus = "queued" | "processing" | "completed" | "failed";

export interface Track {
  id: string;
  title: string;
  prompt: string;
  lyrics?: string | null;
  tags: string[];
  duration: number;
  bpm?: number | null;
  musical_key?: string | null;
  created_at: string;
  provenance: Provenance;
  source_type: string;
  parent_track_id?: string | null;
  favorite: boolean;
  has_audio: boolean;
  version: number;
}

export interface Job {
  id: string;
  kind: string;
  status: JobStatus;
  progress: number;
  message: string;
  track_id?: string | null;
  error?: string | null;
}

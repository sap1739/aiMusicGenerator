"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { CaretDown, Clock, DotsThreeVertical, MagicWand, Pause, Play, Plus, SlidersHorizontal, Sparkle, Waveform as WaveIcon } from "@phosphor-icons/react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { z } from "zod";
import { api } from "@/lib/api";
import { usePlayer, useToasts } from "@/lib/store";
import { AudioWaveform } from "./waveform";

const schema = z.object({
  prompt: z.string().min(8, "Give Auralis a little more to dream with.").max(1200),
  lyrics: z.string().max(12000).optional(),
  duration: z.number().min(10).max(600),
  bpm: z.number().min(40).max(240).optional(),
  instrumental: z.boolean(),
});
type FormValues = z.infer<typeof schema>;
const genres = ["Electronic", "Synthwave", "Future bass", "Ambient", "Indie pop"];
const moods = ["Melancholic", "Dreamy", "Euphoric", "Cinematic", "Nostalgic"];

export function Studio() {
  const queryClient = useQueryClient();
  const push = useToasts((state) => state.push);
  const setTrack = usePlayer((state) => state.setTrack);
  const [genre, setGenre] = useState("Electronic");
  const [mood, setMood] = useState("Melancholic");
  const [custom, setCustom] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const {register, handleSubmit, formState: {errors}, control} = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {prompt: "A midnight drive through rain, luminous synths and a weightless chorus", duration: 204, instrumental: false, lyrics: ""},
  });
  const prompt = useWatch({control, name: "prompt"});
  const {data: tracks = []} = useQuery({queryKey: ["tracks"], queryFn: () => api.tracks()});
  const {data: job} = useQuery({
    queryKey: ["job", jobId], queryFn: () => api.job(jobId!), enabled: Boolean(jobId),
    refetchInterval: (query) => ["completed", "failed"].includes(query.state.data?.status ?? "") ? false : 650,
  });
  useEffect(() => {
    if (job?.status === "completed") { queryClient.invalidateQueries({queryKey: ["tracks"]}); push("Glass Horizon is ready to play."); }
    if (job?.status === "failed") { push(job.error ?? "Generation failed.", "error"); }
  }, [job?.status, job?.error, push, queryClient]);
  const generate = useMutation({mutationFn: api.generate, onSuccess: (nextJob) => { setJobId(nextJob.id); push("Two versions entered the generation queue."); }, onError: (error) => push(error.message, "error")});
  const onSubmit = (values: FormValues) => generate.mutate({...values, title: "Glass Horizon", genre: [genre], mood: [mood], instruments: ["Analogue synth", "Soft drums"], musical_key: "F minor"});
  const featured = tracks[0];
  const working = job && ["queued", "processing"].includes(job.status);

  return <div className="studio-grid">
    <section className="studio-workspace">
      <div className="eyebrow"><Sparkle weight="fill" /> Create a song with <b>AI</b></div>
      <form onSubmit={handleSubmit(onSubmit)} className="composer">
        <div className="prompt-box"><textarea aria-label="Song prompt" defaultValue="A midnight drive through rain, luminous synths and a weightless chorus" {...register("prompt")} /><span>{prompt.length} / 1200</span></div>
        {errors.prompt && <p className="field-error">{errors.prompt.message}</p>}
        <div className="control-row"><label>Genre</label><div className="chip-row">{genres.map((item) => <button type="button" key={item} className={genre === item ? "selected" : ""} onClick={() => setGenre(item)}>{item}</button>)}<button type="button" aria-label="Add genre"><Plus /></button></div></div>
        <div className="control-row"><label>Mood</label><div className="chip-row">{moods.map((item) => <button type="button" key={item} className={mood === item ? "selected" : ""} onClick={() => setMood(item)}>{item}</button>)}<button type="button" aria-label="Add mood"><Plus /></button></div></div>
        <AnimatePresence>{custom && <motion.div className="lyrics-panel" initial={{height: 0, opacity: 0}} animate={{height: "auto", opacity: 1}} exit={{height: 0, opacity: 0}}><div><label>Custom lyrics</label><button type="button"><MagicWand /> Draft lyrics</button></div><textarea placeholder="[Verse]\nCity lights dissolve into the tide…" {...register("lyrics")} /></motion.div>}</AnimatePresence>
        <div className="composer-footer">
          <label className="switch-line"><input type="checkbox" {...register("instrumental")} /><i /><span>Instrumental</span></label>
          <button className="text-action" type="button" onClick={() => setCustom((value) => !value)}>{custom ? "Hide lyrics" : "Add custom lyrics"}<CaretDown className={custom ? "up" : ""} /></button>
          <label className="duration"><Clock /><select aria-label="Duration" defaultValue="204" {...register("duration", {valueAsNumber: true})}><option value="120">2:00</option><option value="204">3:24</option><option value="240">4:00</option></select></label>
          <button className="generate-button" disabled={generate.isPending || Boolean(working)}><Sparkle weight="fill" />{working ? "Generating…" : "Generate"}<WaveIcon /></button>
        </div>
      </form>
      {working ? <GenerationProgress progress={job.progress} message={job.message} track={featured} /> : <NowPlaying track={featured} onPlay={() => featured && setTrack(featured)} />}
    </section>
    <aside className="queue-panel"><div className="queue-heading"><span><SlidersHorizontal /> Generation queue</span><b>{working ? 4 : 3}</b></div>{working && <QueueItem title="Glass Horizon" meta={`${job.progress}% · ${job.message}`} active />}{(tracks.length ? tracks.slice(0, 3) : null)?.map((track, index) => <QueueItem key={track.id} title={track.title} meta={`${track.musical_key ?? "—"} · ${track.bpm ?? "—"} BPM`} active={!working && index === 0} />) ?? <><QueueItem title="Neon Tides" meta="A minor · 122 BPM" active /><QueueItem title="Echoes in Motion" meta="D minor · 110 BPM" /><QueueItem title="Beyond the Skyline" meta="G minor · 126 BPM" /></>}<button className="clear-queue">Clear completed</button></aside>
  </div>;
}

function QueueItem({title, meta, active = false}: {title: string; meta: string; active?: boolean}) { return <div className={`queue-item ${active ? "active" : ""}`}><button aria-label={`Play ${title}`}>{active ? <Pause weight="fill" /> : <Play weight="fill" />}</button><div><strong>{title}</strong><span>{meta}</span><div className="micro-wave">{Array.from({length: 16}, (_, index) => <i key={index} style={{height: `${25 + (index * 23) % 70}%`}} />)}</div></div><DotsThreeVertical /></div>; }

function GenerationProgress({progress, message, track}: {progress: number; message: string; track?: import("@auralis/shared").Track}) { return <motion.section className="now-playing generating-track" initial={{opacity: 0, y: 10}} animate={{opacity: 1, y: 0}}><div className="now-heading"><div><span><Sparkle weight="fill" /> Now generating · {progress}%</span><h2>Glass Horizon</h2></div><div className="track-facts"><div><b>F minor</b><span>Key</span></div><div><b>118</b><span>BPM</span></div><button><SlidersHorizontal /> Edit track</button></div></div><AudioWaveform url={track?.has_audio ? api.audio(track.id) : undefined} active /><div className="render-status"><i style={{width: `${progress}%`}} /><span>{message}</span></div></motion.section>; }

function NowPlaying({track, onPlay}: {track?: import("@auralis/shared").Track; onPlay: () => void}) { return <section className="now-playing"><div className="now-heading"><div><span><Sparkle weight="fill" /> Now playing</span><h2>{track?.title ?? "Glass Horizon"}</h2></div><div className="track-facts"><div><b>{track?.musical_key ?? "F minor"}</b><span>Key</span></div><div><b>{track?.bpm ?? 118}</b><span>BPM</span></div><button><SlidersHorizontal /> Edit track</button></div></div><button className="wave-play" onClick={onPlay} aria-label="Play featured track"><Play weight="fill" /></button><AudioWaveform url={track?.has_audio ? api.audio(track.id) : undefined} active /></section>; }

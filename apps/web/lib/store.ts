import type { Track } from "@auralis/shared";
import { create } from "zustand";
type PlayerStore = {current: Track | null; playing: boolean; setTrack: (track: Track) => void; toggle: () => void; stop: () => void};
export const usePlayer = create<PlayerStore>((set) => ({current: null, playing: false, setTrack: (current) => set({current, playing: true}), toggle: () => set((state) => ({playing: !state.playing})), stop: () => set({playing: false})}));
type Toast = {id: number; message: string; tone: "success" | "error"};
type ToastStore = {items: Toast[]; push: (message: string, tone?: Toast["tone"]) => void; remove: (id: number) => void};
export const useToasts = create<ToastStore>((set) => ({items: [], push: (message, tone = "success") => { const id = Date.now(); set((state) => ({items: [...state.items, {id, message, tone}]})); window.setTimeout(() => set((state) => ({items: state.items.filter((item) => item.id !== id)})), 3600); }, remove: (id) => set((state) => ({items: state.items.filter((item) => item.id !== id)}))}));

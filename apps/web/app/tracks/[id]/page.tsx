import { AppShell } from "@/components/app-shell";
import { TrackDetail } from "@/components/track-detail";
export default async function TrackPage({params}: {params: Promise<{id: string}>}) { const {id} = await params; return <AppShell title="Track detail"><TrackDetail id={id} /></AppShell>; }

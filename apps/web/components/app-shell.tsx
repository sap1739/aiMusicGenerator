"use client";
import { GearSix, Info, MusicNotes, SlidersHorizontal, Sparkle, Waveform } from "@phosphor-icons/react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Brand } from "./brand";
import { MiniPlayer } from "./mini-player";
const links = [{href: "/create", label: "Create", icon: Sparkle}, {href: "/remix", label: "Remix", icon: Waveform}, {href: "/library", label: "Library", icon: MusicNotes}];
export function AppShell({children, title}: {children: React.ReactNode; title?: string}) { const path = usePathname(); return <div className="app-shell"><aside className="sidebar"><Brand /><nav>{links.map(({href, label, icon: Icon}) => <Link key={href} href={href} className={path.startsWith(href) ? "active" : ""}><Icon weight={path.startsWith(href) ? "fill" : "regular"} /><span>{label}</span></Link>)}</nav><div className="sidebar-bottom"><Link href="/settings" className={path === "/settings" ? "active" : ""}><GearSix /><span>Settings</span></Link><Link href="/legal" className={path === "/legal" ? "active" : ""}><Info /><span>Rights & safety</span></Link><div className="profile"><div className="avatar">AV</div><div><strong>Ava Reed</strong><span>Creator plan</span></div><SlidersHorizontal /></div></div></aside><main className="main-panel">{title && <header className="mobile-header"><Brand /><strong>{title}</strong></header>}{children}</main><MiniPlayer /></div>; }

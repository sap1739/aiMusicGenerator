import type { Metadata } from "next";
import { Manrope } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
const manrope = Manrope({subsets: ["latin"], variable: "--font-manrope"});
export const metadata: Metadata = {title: "Auralis — Make music from imagination", description: "An original AI music creation studio powered by independent, open inference."};
export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) { return <html lang="en"><body className={manrope.variable}><Providers>{children}</Providers></body></html>; }

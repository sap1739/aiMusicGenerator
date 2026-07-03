"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { ToastViewport } from "./toast";
export function Providers({children}: {children: React.ReactNode}) { const [client] = useState(() => new QueryClient({defaultOptions: {queries: {staleTime: 4_000, retry: 1}}})); return <QueryClientProvider client={client}>{children}<ToastViewport /></QueryClientProvider>; }

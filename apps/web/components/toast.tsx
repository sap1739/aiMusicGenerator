"use client";
import { CheckCircle, WarningCircle, X } from "@phosphor-icons/react";
import { AnimatePresence, motion } from "framer-motion";
import { useToasts } from "@/lib/store";
export function ToastViewport() { const {items, remove} = useToasts(); return <div className="toast-viewport"><AnimatePresence>{items.map((item) => <motion.div className={`toast ${item.tone}`} key={item.id} initial={{opacity: 0, y: 12}} animate={{opacity: 1, y: 0}} exit={{opacity: 0, x: 12}}>{item.tone === "success" ? <CheckCircle weight="fill" /> : <WarningCircle weight="fill" />}<span>{item.message}</span><button onClick={() => remove(item.id)} aria-label="Dismiss"><X /></button></motion.div>)}</AnimatePresence></div>; }

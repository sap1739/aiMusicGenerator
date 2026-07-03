import Image from "next/image";
export function Brand({compact = false}: {compact?: boolean}) { return <div className="brand"><Image src="/logo.svg" width={26} height={26} alt="" /><span className={compact ? "sr-only" : ""}>Auralis</span></div>; }

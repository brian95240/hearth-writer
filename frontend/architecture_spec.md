// state/signals.ts
import { signal } from "@preact/signals-react";

// The "Hot" Stream - Updates ~50ms
export const tokenStream = signal<string>(""); 

// The "Warm" State - Updates on sentence completion
export const confirmedText = signal<string>("");

// System State - Triggers UI animations (e.g., "The Hearth Glow")
export const systemTemperature = signal<"COLD" | "WARM" | "HOT">("COLD");
"use client";

import { useEffect, useRef, useState } from "react";

/** Animates a number to `target` over `durationMs`, respecting prefers-reduced-motion
 * (BUILD_PROMPT §5: "the changed number counts to its new value over 400ms"). */
export function useCountUp(target: number, durationMs = 400): number {
  const [value, setValue] = useState(target);
  const fromRef = useRef(target);

  useEffect(() => {
    const from = fromRef.current;
    fromRef.current = target;

    if (from === target) return;

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      // matchMedia is a browser-only read with no server-side equivalent to derive
      // this from during render.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setValue(target);
      return;
    }

    let frame: number;
    const start = performance.now();

    const tick = (now: number) => {
      const progress = Math.min(1, (now - start) / durationMs);
      setValue(from + (target - from) * progress);
      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      }
    };
    frame = requestAnimationFrame(tick);

    return () => cancelAnimationFrame(frame);
  }, [target, durationMs]);

  return value;
}

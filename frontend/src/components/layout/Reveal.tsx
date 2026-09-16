"use client";

import { useEffect, useRef, useState } from "react";

/** Scroll-into-view wrapper around the site's existing .reveal animation (globals.css) —
 * reuses the same settle-in motion already used for calculator results, just triggered
 * by IntersectionObserver instead of mount. No-JS and pre-hydration renders show full
 * content (the hidden state is only ever applied via an inline style set client-side
 * after mount), so this can never leave content stuck invisible. */
export default function Reveal({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [hasMounted, setHasMounted] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Client-only mount flag — there's no pre-mount value to read, so this can't be
    // derived during render; the one extra render is the hydration-safety tradeoff.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setHasMounted(true);
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(el);
        }
      },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      style={hasMounted && !isVisible ? { opacity: 0 } : undefined}
      className={isVisible ? `reveal ${className}` : className}
    >
      {children}
    </div>
  );
}

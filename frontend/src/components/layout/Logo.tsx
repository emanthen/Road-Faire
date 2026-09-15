/** A mountain range with a dashed road climbing through it — the two things Roadfare
 * is actually about (national parks, the drive between them) rendered in the same two
 * colors used everywhere else (pine, sodium), not a new brand color. */
export default function Logo({ className = "h-7 w-7" }: { className?: string }) {
  return (
    <svg viewBox="0 0 48 48" fill="none" className={className} aria-hidden>
      <path
        d="M4 38 L17 14 L24 26 L31 12 L44 38 Z"
        fill="currentColor"
        className="text-pine"
      />
      <path
        d="M11 38 Q19 27 22 21 Q26 13 31 6"
        stroke="currentColor"
        strokeWidth="2.25"
        strokeLinecap="round"
        strokeDasharray="1 5"
        className="text-sodium"
      />
    </svg>
  );
}

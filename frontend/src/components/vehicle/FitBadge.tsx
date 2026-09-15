export default function FitBadge({ status }: { status: "fits" | "warning" | "blocked" }) {
  const styles = {
    fits: "border-pine text-pine",
    // sodium text on a light background is ~1.9:1 contrast, under WCAG AA's 4.5:1
    // minimum — the accent lives in the border/fill here, text stays ink for contrast.
    warning: "border-sodium bg-sodium/10 text-ink",
    blocked: "border-signal text-signal",
  };
  const labels = { fits: "Fits", warning: "Check limits", blocked: "Won't fit" };

  return (
    <span className={`rounded border px-2 py-1 text-xs font-medium ${styles[status]}`}>
      {labels[status]}
    </span>
  );
}

/** "Fees verified 14 Aug 2026" — freshness as a UI feature, not metadata (BUILD_PROMPT §6). */
export default function VerifiedAt({ date }: { date: string | null }) {
  if (!date) {
    return <p className="text-sm text-signal">Not yet verified.</p>;
  }
  const formatted = new Date(date).toLocaleDateString("en-US", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
  return <p className="text-sm text-asphalt">Verified {formatted}</p>;
}

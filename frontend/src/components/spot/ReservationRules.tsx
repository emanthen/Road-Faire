import VerifiedAt from "@/components/spot/VerifiedAt";
import type { ReservationRule } from "@/types/api";

const KIND_LABELS: Record<ReservationRule["kind"], string> = {
  timed_entry: "Timed entry",
  vehicle: "Vehicle reservation",
  permit: "Permit",
  shuttle: "Shuttle ticket",
  lottery: "Lottery",
};

export default function ReservationRules({ rules }: { rules: ReservationRule[] }) {
  if (rules.length === 0) {
    return <p className="text-asphalt">No reservation rules on file for this spot yet.</p>;
  }

  return (
    <ul className="flex flex-col gap-4">
      {rules.map((rule, i) => (
        <li key={i} className="border-b border-asphalt/20 pb-4">
          <p className="font-medium text-ink">{KIND_LABELS[rule.kind]}</p>
          {rule.season_start && rule.season_end && (
            <p className="text-sm text-asphalt">
              {rule.season_start} through {rule.season_end}
            </p>
          )}
          {rule.window_start && rule.window_end && (
            <p className="text-sm text-asphalt">
              {rule.window_start}–{rule.window_end}
            </p>
          )}
          {rule.notes && <p className="mt-1 text-sm text-ink">{rule.notes}</p>}
          {rule.booking_url && (
            <a href={rule.booking_url} className="text-sm text-pine underline">
              Book this reservation
            </a>
          )}
          <div className="mt-1">
            <VerifiedAt date={rule.verified_at} />
          </div>
        </li>
      ))}
    </ul>
  );
}

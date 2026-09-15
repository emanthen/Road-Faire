import CostLine from "@/components/cost/CostLine";
import type { SpotCost } from "@/types/api";

function toCents(decimalString: string | null): number {
  if (!decimalString) return 0;
  return Math.round(parseFloat(decimalString) * 100);
}

export default function AtAGlance({
  cost,
  contactPhone,
}: {
  cost: SpotCost | null;
  contactPhone?: string;
}) {
  return (
    <div>
      {!cost && (
        <p className="text-asphalt">Cost data hasn&apos;t been added for this spot yet.</p>
      )}
      {cost?.entry_vehicle && (
        <CostLine label="Entrance (per vehicle)" amountCents={toCents(cost.entry_vehicle)} />
      )}
      {cost?.entry_person && (
        <CostLine label="Entrance (per person)" amountCents={toCents(cost.entry_person)} />
      )}
      {cost?.campsite_low && (
        <CostLine label="Campsite (from)" amountCents={toCents(cost.campsite_low)} />
      )}
      {contactPhone && (
        <p className="mt-2 text-sm text-asphalt">
          Official number: <span className="figure">{contactPhone}</span>
        </p>
      )}
    </div>
  );
}

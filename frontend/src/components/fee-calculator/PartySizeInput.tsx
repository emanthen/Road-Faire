"use client";

function NumberField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
      {label}
      <input
        type="number"
        min={0}
        value={value}
        onChange={(e) => onChange(Math.max(0, Number(e.target.value)))}
        className="min-h-11 w-24 rounded border border-asphalt/30 px-3 py-2 text-ink figure hover:border-pine/60"
      />
    </label>
  );
}

export default function PartySizeInput({
  adults,
  childrenCount,
  onAdultsChange,
  onChildrenChange,
}: {
  adults: number;
  childrenCount: number;
  onAdultsChange: (value: number) => void;
  onChildrenChange: (value: number) => void;
}) {
  return (
    <div className="flex gap-4">
      <NumberField label="Adults (16+)" value={adults} onChange={onAdultsChange} />
      <NumberField
        label="Children (under 16)"
        value={childrenCount}
        onChange={onChildrenChange}
      />
    </div>
  );
}

"use client";

import RadioToggleGroup from "@/components/ui/RadioToggleGroup";

export default function ResidencyToggle({
  isUsResident,
  onChange,
}: {
  isUsResident: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <RadioToggleGroup
      legend="Are you a US resident?"
      value={isUsResident}
      onChange={onChange}
      options={[
        { label: "US resident", value: true },
        { label: "Non-resident", value: false },
      ]}
    />
  );
}

"use client";

import { useRef } from "react";

interface RadioOption<T> {
  label: string;
  value: T;
}

/** A `role="radiogroup"` of toggle buttons with real roving-tabindex keyboard support
 * (arrow keys move focus and selection between options, Tab reaches the group as a
 * single stop) — the interaction model screen reader users actually expect from
 * role="radio", not just individually-tabbable buttons that happen to look like one. */
export default function RadioToggleGroup<T extends string | boolean>({
  legend,
  options,
  value,
  onChange,
  optionClassName = "",
}: {
  legend: string;
  options: RadioOption<T>[];
  value: T;
  onChange: (value: T) => void;
  optionClassName?: string;
}) {
  const buttonRefs = useRef<(HTMLButtonElement | null)[]>([]);

  function handleKeyDown(event: React.KeyboardEvent, index: number) {
    const forward = event.key === "ArrowRight" || event.key === "ArrowDown";
    const backward = event.key === "ArrowLeft" || event.key === "ArrowUp";
    if (!forward && !backward) return;

    event.preventDefault();
    const nextIndex = (index + (forward ? 1 : -1) + options.length) % options.length;
    onChange(options[nextIndex].value);
    buttonRefs.current[nextIndex]?.focus();
  }

  return (
    <fieldset>
      <legend className="mb-2 text-sm font-medium text-ink">{legend}</legend>
      <div className="flex gap-2" role="radiogroup" aria-label={legend}>
        {options.map((option, index) => {
          const isChecked = option.value === value;
          return (
            <button
              key={String(option.value)}
              ref={(el) => {
                buttonRefs.current[index] = el;
              }}
              type="button"
              role="radio"
              aria-checked={isChecked}
              tabIndex={isChecked ? 0 : -1}
              onClick={() => onChange(option.value)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              className={`min-h-11 rounded border px-4 py-2 text-sm font-medium active:scale-[0.98] ${
                isChecked
                  ? "border-pine bg-pine text-snow"
                  : "border-asphalt/30 text-ink hover:border-pine hover:bg-pine/5"
              } ${optionClassName}`}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}

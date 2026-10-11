"use client";

import { useState } from "react";

interface ChipMultiSelectProps {
  label: string;
  options: string[];
  selected: string[];
  onToggle: (value: string) => void;
  allowCustom?: boolean;
  customPlaceholder?: string;
}

export function ChipMultiSelect({
  label,
  options,
  selected,
  onToggle,
  allowCustom = false,
  customPlaceholder = "Agregar otro...",
}: ChipMultiSelectProps) {
  const [customValue, setCustomValue] = useState("");

  function addCustom() {
    const trimmed = customValue.trim();
    if (trimmed) {
      onToggle(trimmed);
    }
    setCustomValue("");
  }

  const extras = selected.filter((value) => !options.includes(value));

  return (
    <div>
      <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">
        {label}
      </label>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            type="button"
            key={option}
            onClick={() => onToggle(option)}
            className={
              selected.includes(option)
                ? "rounded-full bg-brand-600 px-3 py-1.5 text-sm font-medium text-white"
                : "rounded-full border border-slate-300 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            }
          >
            {option}
          </button>
        ))}
        {extras.map((value) => (
          <button
            type="button"
            key={value}
            onClick={() => onToggle(value)}
            className="rounded-full bg-brand-600 px-3 py-1.5 text-sm font-medium text-white"
          >
            {value} &times;
          </button>
        ))}
      </div>
      {allowCustom && (
        <div className="mt-2 flex gap-2">
          <input
            type="text"
            value={customValue}
            onChange={(e) => setCustomValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addCustom();
              }
            }}
            placeholder={customPlaceholder}
            className="flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-slate-700 dark:bg-slate-800"
          />
          <button
            type="button"
            onClick={addCustom}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Agregar
          </button>
        </div>
      )}
    </div>
  );
}

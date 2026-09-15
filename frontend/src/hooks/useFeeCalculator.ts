"use client";

import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import type { EntryFeeBreakdown, FeeCalculateRequest } from "@/lib/schemas";
import { entryFeeBreakdownSchema } from "@/lib/schemas";

export function useFeeCalculator() {
  return useMutation({
    mutationFn: async (request: FeeCalculateRequest): Promise<EntryFeeBreakdown> => {
      const data = await apiFetch<unknown>("/api/fees/calculate", {
        method: "POST",
        body: JSON.stringify(request),
      });
      return entryFeeBreakdownSchema.parse(data);
    },
  });
}

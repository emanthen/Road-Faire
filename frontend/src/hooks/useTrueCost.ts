"use client";

import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import type { TrueCostRequest, VanCostBreakdown } from "@/lib/schemas";
import { vanCostBreakdownSchema } from "@/lib/schemas";

export function useTrueCost() {
  return useMutation({
    mutationFn: async (request: TrueCostRequest): Promise<VanCostBreakdown> => {
      const data = await apiFetch<unknown>("/api/vehicles/true-cost", {
        method: "POST",
        body: JSON.stringify(request),
      });
      return vanCostBreakdownSchema.parse(data);
    },
  });
}

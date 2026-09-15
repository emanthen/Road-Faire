"use client";

import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import type { FitResult, SizeCheckRequest } from "@/lib/schemas";
import { fitResultSchema } from "@/lib/schemas";

export function useSizeCheck() {
  return useMutation({
    mutationFn: async (request: SizeCheckRequest): Promise<FitResult> => {
      const data = await apiFetch<unknown>("/api/vehicles/size-check", {
        method: "POST",
        body: JSON.stringify(request),
      });
      return fitResultSchema.parse(data);
    },
  });
}

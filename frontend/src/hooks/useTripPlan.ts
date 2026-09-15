"use client";

import { useMutation } from "@tanstack/react-query";
import { createPlan, type PlanResponse } from "@/lib/api";
import type { TripRequest } from "@/types/planner";

/** Drives the planner flow against POST /api/plan. */
export function useTripPlan() {
  return useMutation<PlanResponse, Error, TripRequest>({
    mutationFn: createPlan,
  });
}

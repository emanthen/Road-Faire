"use client";

import { useParams } from "next/navigation";
import PhotosSubTable from "@/components/dashboard/spots/PhotosSubTable";
import ReservationRulesSubTable from "@/components/dashboard/spots/ReservationRulesSubTable";
import SpotCostSection from "@/components/dashboard/spots/SpotCostSection";
import SpotForm from "@/components/dashboard/spots/SpotForm";
import VehicleLimitsSubTable from "@/components/dashboard/spots/VehicleLimitsSubTable";
import { spotsAdminHooks } from "@/hooks/admin";

export default function EditSpotPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: spot, isLoading } = spotsAdminHooks.useDetail(slug);

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-semibold">Edit spot</h1>
      <div className="mt-6 space-y-8">
        {isLoading ? (
          <p className="text-muted-foreground">Loading…</p>
        ) : spot ? (
          <>
            <SpotForm spot={spot} />
            <SpotCostSection spotId={spot.id} />
            <ReservationRulesSubTable spotId={spot.id} />
            <VehicleLimitsSubTable spotId={spot.id} />
            <PhotosSubTable spotId={spot.id} />
          </>
        ) : (
          <p className="text-muted-foreground">Spot not found.</p>
        )}
      </div>
    </div>
  );
}

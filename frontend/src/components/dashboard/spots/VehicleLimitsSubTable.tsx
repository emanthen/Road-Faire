"use client";

import { useState } from "react";
import { toast } from "sonner";
import ConfirmDeleteDialog from "@/components/dashboard/ConfirmDeleteDialog";
import DataTable, { type DataTableColumn } from "@/components/dashboard/DataTable";
import { Button } from "@/components/ui/button";
import { vehicleLimitsAdminHooks } from "@/hooks/admin";
import type { VehicleLimitAdmin } from "@/types/admin";
import VehicleLimitFormDialog from "./VehicleLimitFormDialog";

export default function VehicleLimitsSubTable({ spotId }: { spotId: number }) {
  const { data, isLoading } = vehicleLimitsAdminHooks.useList({ spot: spotId });
  const deleteMutation = vehicleLimitsAdminHooks.useDelete();
  const [editingLimit, setEditingLimit] = useState<VehicleLimitAdmin | undefined>(undefined);
  const [dialogOpen, setDialogOpen] = useState(false);

  const columns: DataTableColumn<VehicleLimitAdmin>[] = [
    {
      header: "Max length",
      cell: (row) => (
        <button className="text-left font-medium text-pine hover:underline" onClick={() => { setEditingLimit(row); setDialogOpen(true); }}>
          {row.max_length_ft ? `${row.max_length_ft} ft` : "—"}
        </button>
      ),
    },
    { header: "Max height", cell: (row) => (row.max_height_ft ? `${row.max_height_ft} ft` : "—") },
    { header: "Max weight", cell: (row) => (row.max_weight_lb ? `${row.max_weight_lb} lb` : "—") },
    { header: "Roads", cell: (row) => <span className="text-muted-foreground">{row.applies_to_roads.join(", ")}</span> },
    {
      header: "", className: "text-right",
      cell: (row) => (
        <ConfirmDeleteDialog
          trigger={<Button variant="ghost" size="sm">Delete</Button>}
          title="Delete this vehicle limit?"
          onConfirm={() => deleteMutation.mutate(row.id, {
            onSuccess: () => toast.success("Vehicle limit deleted."),
            onError: () => toast.error("Couldn't delete that limit."),
          })}
          isPending={deleteMutation.isPending}
        />
      ),
    },
  ];

  return (
    <div className="rounded-md border border-border p-4">
      <div className="flex items-center justify-between">
        <h2 className="font-medium">Vehicle limits</h2>
        <Button size="sm" onClick={() => { setEditingLimit(undefined); setDialogOpen(true); }}>New limit</Button>
      </div>
      <div className="mt-4">
        <DataTable columns={columns} rows={data?.results} isLoading={isLoading} keyFor={(row) => row.id} emptyMessage="No vehicle limits yet." />
      </div>
      <VehicleLimitFormDialog spotId={spotId} limit={editingLimit} open={dialogOpen} onOpenChange={setDialogOpen} />
    </div>
  );
}

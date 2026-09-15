"use client";

import { useState } from "react";
import { toast } from "sonner";
import ConfirmDeleteDialog from "@/components/dashboard/ConfirmDeleteDialog";
import DataTable, { type DataTableColumn } from "@/components/dashboard/DataTable";
import { Button } from "@/components/ui/button";
import { reservationRulesAdminHooks } from "@/hooks/admin";
import type { ReservationRuleAdmin } from "@/types/admin";
import ReservationRuleFormDialog from "./ReservationRuleFormDialog";

export default function ReservationRulesSubTable({ spotId }: { spotId: number }) {
  const { data, isLoading } = reservationRulesAdminHooks.useList({ spot: spotId });
  const deleteMutation = reservationRulesAdminHooks.useDelete();
  const [editingRule, setEditingRule] = useState<ReservationRuleAdmin | undefined>(undefined);
  const [dialogOpen, setDialogOpen] = useState(false);

  const columns: DataTableColumn<ReservationRuleAdmin>[] = [
    {
      header: "Kind",
      cell: (row) => (
        <button className="text-left font-medium text-pine hover:underline" onClick={() => { setEditingRule(row); setDialogOpen(true); }}>
          {row.kind.replace("_", " ")}
        </button>
      ),
    },
    { header: "Season", cell: (row) => [row.season_start, row.season_end].filter(Boolean).join(" – ") || "—" },
    { header: "Booking URL", cell: (row) => <span className="text-muted-foreground">{row.booking_url}</span> },
    {
      header: "", className: "text-right",
      cell: (row) => (
        <ConfirmDeleteDialog
          trigger={<Button variant="ghost" size="sm">Delete</Button>}
          title="Delete this reservation rule?"
          onConfirm={() => deleteMutation.mutate(row.id, {
            onSuccess: () => toast.success("Reservation rule deleted."),
            onError: () => toast.error("Couldn't delete that rule."),
          })}
          isPending={deleteMutation.isPending}
        />
      ),
    },
  ];

  return (
    <div className="rounded-md border border-border p-4">
      <div className="flex items-center justify-between">
        <h2 className="font-medium">Reservation rules</h2>
        <Button size="sm" onClick={() => { setEditingRule(undefined); setDialogOpen(true); }}>New rule</Button>
      </div>
      <div className="mt-4">
        <DataTable columns={columns} rows={data?.results} isLoading={isLoading} keyFor={(row) => row.id} emptyMessage="No reservation rules yet." />
      </div>
      <ReservationRuleFormDialog spotId={spotId} rule={editingRule} open={dialogOpen} onOpenChange={setDialogOpen} />
    </div>
  );
}

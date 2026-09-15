"use client";

import { useState } from "react";
import { toast } from "sonner";
import ConfirmDeleteDialog from "@/components/dashboard/ConfirmDeleteDialog";
import DataTable, { type DataTableColumn } from "@/components/dashboard/DataTable";
import { Button } from "@/components/ui/button";
import { offersAdminHooks } from "@/hooks/admin";
import type { OfferAdmin } from "@/types/admin";
import OfferFormDialog from "./OfferFormDialog";

export default function OffersSubTable({ partnerId }: { partnerId: number }) {
  const { data, isLoading } = offersAdminHooks.useList({ partner: partnerId });
  const deleteMutation = offersAdminHooks.useDelete();
  const [editingOffer, setEditingOffer] = useState<OfferAdmin | undefined>(undefined);
  const [dialogOpen, setDialogOpen] = useState(false);

  const columns: DataTableColumn<OfferAdmin>[] = [
    {
      header: "Category",
      cell: (row) => (
        <button
          className="text-left font-medium text-pine hover:underline"
          onClick={() => {
            setEditingOffer(row);
            setDialogOpen(true);
          }}
        >
          {row.category}
        </button>
      ),
    },
    { header: "Description", cell: (row) => row.description },
    { header: "Price note", cell: (row) => row.price_note },
    {
      header: "",
      className: "text-right",
      cell: (row) => (
        <ConfirmDeleteDialog
          trigger={<Button variant="ghost" size="sm">Delete</Button>}
          title="Delete this offer?"
          onConfirm={() => {
            deleteMutation.mutate(row.id, {
              onSuccess: () => toast.success("Offer deleted."),
              onError: () => toast.error("Couldn't delete that offer."),
            });
          }}
          isPending={deleteMutation.isPending}
        />
      ),
    },
  ];

  return (
    <div className="rounded-md border border-border p-4">
      <div className="flex items-center justify-between">
        <h2 className="font-medium">Offers</h2>
        <Button
          size="sm"
          onClick={() => {
            setEditingOffer(undefined);
            setDialogOpen(true);
          }}
        >
          New offer
        </Button>
      </div>
      <div className="mt-4">
        <DataTable
          columns={columns}
          rows={data?.results}
          isLoading={isLoading}
          keyFor={(row) => row.id}
          emptyMessage="No offers yet."
        />
      </div>
      <OfferFormDialog
        partnerId={partnerId}
        offer={editingOffer}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />
    </div>
  );
}

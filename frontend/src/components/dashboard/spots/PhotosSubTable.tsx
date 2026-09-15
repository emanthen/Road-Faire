"use client";

import { useState } from "react";
import { toast } from "sonner";
import ConfirmDeleteDialog from "@/components/dashboard/ConfirmDeleteDialog";
import DataTable, { type DataTableColumn } from "@/components/dashboard/DataTable";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { photosAdminHooks } from "@/hooks/admin";
import type { PhotoAdmin } from "@/types/admin";
import PhotoFormDialog from "./PhotoFormDialog";

export default function PhotosSubTable({ spotId }: { spotId: number }) {
  const { data, isLoading } = photosAdminHooks.useList({ spot: spotId });
  const deleteMutation = photosAdminHooks.useDelete();
  const [editingPhoto, setEditingPhoto] = useState<PhotoAdmin | undefined>(undefined);
  const [dialogOpen, setDialogOpen] = useState(false);

  const columns: DataTableColumn<PhotoAdmin>[] = [
    {
      header: "Image",
      cell: (row) => (
        <button className="text-left font-medium text-pine hover:underline" onClick={() => { setEditingPhoto(row); setDialogOpen(true); }}>
          {row.s3_key}
        </button>
      ),
    },
    { header: "Alt text", cell: (row) => <span className="text-muted-foreground">{row.alt_text}</span> },
    { header: "Primary", cell: (row) => (row.is_primary ? <Badge>Primary</Badge> : null) },
    {
      header: "", className: "text-right",
      cell: (row) => (
        <ConfirmDeleteDialog
          trigger={<Button variant="ghost" size="sm">Delete</Button>}
          title="Delete this photo?"
          onConfirm={() => deleteMutation.mutate(row.id, {
            onSuccess: () => toast.success("Photo deleted."),
            onError: () => toast.error("Couldn't delete that photo."),
          })}
          isPending={deleteMutation.isPending}
        />
      ),
    },
  ];

  return (
    <div className="rounded-md border border-border p-4">
      <div className="flex items-center justify-between">
        <h2 className="font-medium">Photos</h2>
        <Button size="sm" onClick={() => { setEditingPhoto(undefined); setDialogOpen(true); }}>New photo</Button>
      </div>
      <div className="mt-4">
        <DataTable columns={columns} rows={data?.results} isLoading={isLoading} keyFor={(row) => row.id} emptyMessage="No photos yet." />
      </div>
      <PhotoFormDialog spotId={spotId} photo={editingPhoto} open={dialogOpen} onOpenChange={setDialogOpen} />
    </div>
  );
}

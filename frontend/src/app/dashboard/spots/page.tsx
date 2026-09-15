"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import ConfirmDeleteDialog from "@/components/dashboard/ConfirmDeleteDialog";
import DataTable, { type DataTableColumn } from "@/components/dashboard/DataTable";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { spotsAdminHooks } from "@/hooks/admin";
import type { SpotAdmin } from "@/types/admin";

export default function SpotsListPage() {
  const [search, setSearch] = useState("");
  const { data, isLoading } = spotsAdminHooks.useList(search ? { search } : undefined);
  const deleteMutation = spotsAdminHooks.useDelete();

  const columns: DataTableColumn<SpotAdmin>[] = [
    {
      header: "Name",
      cell: (row) => (
        <Link href={`/dashboard/spots/${row.slug}`} className="font-medium text-pine hover:underline">
          {row.name}
        </Link>
      ),
    },
    { header: "Type", cell: (row) => <span className="text-muted-foreground">{row.type.replace("_", " ")}</span> },
    { header: "Min days", cell: (row) => row.min_days },
    {
      header: "", className: "text-right",
      cell: (row) => (
        <ConfirmDeleteDialog
          trigger={<Button variant="ghost" size="sm">Delete</Button>}
          title={`Delete "${row.name}"?`}
          onConfirm={() => {
            deleteMutation.mutate(row.slug, {
              onSuccess: () => toast.success("Spot deleted."),
              onError: () => toast.error("Couldn't delete that spot."),
            });
          }}
          isPending={deleteMutation.isPending}
        />
      ),
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Spots</h1>
        <Button asChild>
          <Link href="/dashboard/spots/new">New spot</Link>
        </Button>
      </div>
      <div className="mt-4">
        <Input
          placeholder="Search by name or slug…"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          className="max-w-sm"
        />
      </div>
      <div className="mt-6">
        <DataTable
          columns={columns}
          rows={data?.results}
          isLoading={isLoading}
          keyFor={(row) => row.id}
          emptyMessage="No spots yet."
        />
      </div>
    </div>
  );
}

"use client";

import Link from "next/link";
import { toast } from "sonner";
import ConfirmDeleteDialog from "@/components/dashboard/ConfirmDeleteDialog";
import DataTable, { type DataTableColumn } from "@/components/dashboard/DataTable";
import { Button } from "@/components/ui/button";
import { partnersAdminHooks } from "@/hooks/admin";
import type { PartnerAdmin } from "@/types/admin";

export default function VendorsListPage() {
  const { data, isLoading } = partnersAdminHooks.useList();
  const deleteMutation = partnersAdminHooks.useDelete();

  const columns: DataTableColumn<PartnerAdmin>[] = [
    {
      header: "Name",
      cell: (row) => (
        <Link href={`/dashboard/vendors/${row.slug}`} className="font-medium text-pine hover:underline">
          {row.name}
        </Link>
      ),
    },
    { header: "Service area", cell: (row) => <span className="text-muted-foreground">{row.service_area}</span> },
    { header: "Rating", cell: (row) => (row.rating ? `${row.rating} (${row.rating_count ?? 0})` : "—") },
    {
      header: "",
      className: "text-right",
      cell: (row) => (
        <ConfirmDeleteDialog
          trigger={<Button variant="ghost" size="sm">Delete</Button>}
          title={`Delete "${row.name}"?`}
          onConfirm={() => {
            deleteMutation.mutate(row.slug, {
              onSuccess: () => toast.success("Vendor deleted."),
              onError: () => toast.error("Couldn't delete that vendor."),
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
        <h1 className="text-2xl font-semibold">Vendors</h1>
        <Button asChild>
          <Link href="/dashboard/vendors/new">New vendor</Link>
        </Button>
      </div>
      <div className="mt-6">
        <DataTable
          columns={columns}
          rows={data?.results}
          isLoading={isLoading}
          keyFor={(row) => row.id}
          emptyMessage="No vendors yet."
        />
      </div>
    </div>
  );
}

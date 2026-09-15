"use client";

import { useState } from "react";
import { toast } from "sonner";
import ConfirmDeleteDialog from "@/components/dashboard/ConfirmDeleteDialog";
import DataTable, { type DataTableColumn } from "@/components/dashboard/DataTable";
import FAQFormDialog from "@/components/dashboard/faqs/FAQFormDialog";
import { Button } from "@/components/ui/button";
import { faqsAdminHooks } from "@/hooks/admin";
import type { FAQAdmin } from "@/types/admin";

export default function FAQsPage() {
  const { data, isLoading } = faqsAdminHooks.useList();
  const deleteMutation = faqsAdminHooks.useDelete();
  const [editingFaq, setEditingFaq] = useState<FAQAdmin | undefined>(undefined);
  const [dialogOpen, setDialogOpen] = useState(false);

  const rows = [...(data?.results ?? [])].sort((a, b) => a.order - b.order);

  const columns: DataTableColumn<FAQAdmin>[] = [
    { header: "Order", cell: (row) => row.order, className: "w-16" },
    {
      header: "Question",
      cell: (row) => (
        <button
          className="text-left font-medium text-pine hover:underline"
          onClick={() => {
            setEditingFaq(row);
            setDialogOpen(true);
          }}
        >
          {row.question}
        </button>
      ),
    },
    {
      header: "Answer",
      cell: (row) => <span className="line-clamp-1 text-muted-foreground">{row.answer}</span>,
    },
    {
      header: "",
      className: "text-right",
      cell: (row) => (
        <ConfirmDeleteDialog
          trigger={<Button variant="ghost" size="sm">Delete</Button>}
          title="Delete this FAQ?"
          onConfirm={() => {
            deleteMutation.mutate(row.id, {
              onSuccess: () => toast.success("FAQ deleted."),
              onError: () => toast.error("Couldn't delete that FAQ."),
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
        <h1 className="text-2xl font-semibold">FAQs</h1>
        <Button
          onClick={() => {
            setEditingFaq(undefined);
            setDialogOpen(true);
          }}
        >
          New FAQ
        </Button>
      </div>
      <div className="mt-6">
        <DataTable columns={columns} rows={rows} isLoading={isLoading} keyFor={(row) => row.id} emptyMessage="No FAQs yet." />
      </div>
      <FAQFormDialog faq={editingFaq} open={dialogOpen} onOpenChange={setDialogOpen} />
    </div>
  );
}

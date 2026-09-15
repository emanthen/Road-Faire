"use client";

import Link from "next/link";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import ConfirmDeleteDialog from "@/components/dashboard/ConfirmDeleteDialog";
import DataTable, { type DataTableColumn } from "@/components/dashboard/DataTable";
import { pagesAdminHooks } from "@/hooks/admin";
import type { PageAdmin } from "@/types/admin";

export default function ArticlesListPage() {
  const { data, isLoading } = pagesAdminHooks.useList();
  const deleteMutation = pagesAdminHooks.useDelete();

  const columns: DataTableColumn<PageAdmin>[] = [
    { header: "Title", cell: (row) => <Link href={`/dashboard/articles/${row.slug}`} className="font-medium text-pine hover:underline">{row.title}</Link> },
    { header: "Slug", cell: (row) => <span className="text-muted-foreground">{row.slug}</span> },
    {
      header: "Status",
      cell: (row) => (
        <Badge variant={row.published ? "default" : "secondary"}>
          {row.published ? "Published" : "Draft"}
        </Badge>
      ),
    },
    {
      header: "",
      className: "text-right",
      cell: (row) => (
        <ConfirmDeleteDialog
          trigger={<Button variant="ghost" size="sm">Delete</Button>}
          title={`Delete "${row.title}"?`}
          onConfirm={() => {
            deleteMutation.mutate(row.slug, {
              onSuccess: () => toast.success("Article deleted."),
              onError: () => toast.error("Couldn't delete that article."),
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
        <h1 className="text-2xl font-semibold">Articles</h1>
        <Button asChild>
          <Link href="/dashboard/articles/new">New article</Link>
        </Button>
      </div>
      <div className="mt-6">
        <DataTable
          columns={columns}
          rows={data?.results}
          isLoading={isLoading}
          keyFor={(row) => row.id}
          emptyMessage="No articles yet."
        />
      </div>
    </div>
  );
}

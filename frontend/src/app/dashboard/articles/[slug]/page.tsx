"use client";

import { useParams } from "next/navigation";
import ArticleForm from "@/components/dashboard/articles/ArticleForm";
import { pagesAdminHooks } from "@/hooks/admin";

export default function EditArticlePage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: article, isLoading } = pagesAdminHooks.useDetail(slug);

  return (
    <div>
      <h1 className="text-2xl font-semibold">Edit article</h1>
      <div className="mt-6">
        {isLoading ? (
          <p className="text-muted-foreground">Loading…</p>
        ) : article ? (
          <ArticleForm article={article} />
        ) : (
          <p className="text-muted-foreground">Article not found.</p>
        )}
      </div>
    </div>
  );
}

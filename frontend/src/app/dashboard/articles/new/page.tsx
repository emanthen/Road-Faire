import ArticleForm from "@/components/dashboard/articles/ArticleForm";

export default function NewArticlePage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold">New article</h1>
      <div className="mt-6">
        <ArticleForm />
      </div>
    </div>
  );
}

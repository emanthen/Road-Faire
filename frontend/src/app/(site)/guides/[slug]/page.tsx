import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ApiError, fetchPage } from "@/lib/api";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  try {
    const page = await fetchPage(slug);
    return { title: `${page.title} - Roadfare` };
  } catch {
    return {};
  }
}

export default async function GuidePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;

  let page;
  try {
    page = await fetchPage(slug);
  } catch (error) {
    if (error instanceof ApiError && error.statusCode === 404) notFound();
    throw error;
  }

  return (
    <article className="max-w-2xl px-6 py-16">
      <h1 className="text-3xl font-semibold text-pine sm:text-4xl">{page.title}</h1>
      <div className="mt-8 flex flex-col gap-4 whitespace-pre-line text-ink">{page.body}</div>
    </article>
  );
}

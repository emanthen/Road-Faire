/**
 * Webhook from Django (apps.core.revalidate.notify_revalidate) on data change ->
 * revalidates the affected pages. Guarded by a shared secret (REVALIDATE_SECRET, set
 * identically on both sides) so only the backend can trigger it.
 */
import { revalidatePath } from "next/cache";
import { NextRequest, NextResponse } from "next/server";
import { SPOT_SUB_PATHS } from "@/app/sitemap";

interface RevalidateBody {
  kind: "spot" | "content";
  slug: string;
}

export async function POST(request: NextRequest) {
  const secret = request.headers.get("x-revalidate-secret");
  if (!secret || secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ error: "Invalid secret" }, { status: 401 });
  }

  let body: RevalidateBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const paths = pathsFor(body);
  if (paths.length === 0) {
    return NextResponse.json(
      { error: `Unknown revalidation kind/slug: ${body.kind}/${body.slug}` },
      { status: 400 }
    );
  }

  for (const path of paths) revalidatePath(path);

  return NextResponse.json({ revalidated: paths });
}

function pathsFor({ kind, slug }: RevalidateBody): string[] {
  if (!slug) return [];
  switch (kind) {
    case "spot":
      return SPOT_SUB_PATHS.map((subPath) => `/spots/${slug}${subPath}`);
    case "content":
      return [`/guides/${slug}`];
    default:
      return [];
  }
}

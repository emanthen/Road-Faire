/**
 * Webhook from Django on data change -> revalidates the affected ISR pages.
 * Phase 4/6: needs a shared secret check and a path-revalidation map once
 * spot/content pages exist.
 */
import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json(
    { error: "Not implemented until Phase 4 (spot pages exist to revalidate)." },
    { status: 501 }
  );
}

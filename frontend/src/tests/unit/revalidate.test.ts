import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";

vi.mock("next/cache", () => ({ revalidatePath: vi.fn() }));

const ENDPOINT = "http://localhost:3000/api/revalidate";

function postRequest(body: unknown, secret?: string): NextRequest {
  return new NextRequest(ENDPOINT, {
    method: "POST",
    headers: secret ? { "x-revalidate-secret": secret } : {},
    body: JSON.stringify(body),
  });
}

describe("POST /api/revalidate", () => {
  const originalSecret = process.env.REVALIDATE_SECRET;

  beforeEach(() => {
    process.env.REVALIDATE_SECRET = "test-secret";
    vi.resetModules();
  });

  afterEach(() => {
    process.env.REVALIDATE_SECRET = originalSecret;
  });

  it("rejects a missing or wrong secret", async () => {
    const { POST } = await import("@/app/api/revalidate/route");

    const missing = await POST(postRequest({ kind: "spot", slug: "zion" }));
    expect(missing.status).toBe(401);

    const wrong = await POST(postRequest({ kind: "spot", slug: "zion" }, "nope"));
    expect(wrong.status).toBe(401);
  });

  it("revalidates every spot sub-path for a spot slug", async () => {
    const { revalidatePath } = await import("next/cache");
    const { POST } = await import("@/app/api/revalidate/route");

    const response = await POST(postRequest({ kind: "spot", slug: "zion" }, "test-secret"));
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.revalidated).toEqual([
      "/spots/zion",
      "/spots/zion/cost",
      "/spots/zion/best-time-to-visit",
      "/spots/zion/reservations",
      "/spots/zion/campervan",
    ]);
    expect(revalidatePath).toHaveBeenCalledTimes(5);
  });

  it("revalidates a single guide path for content", async () => {
    const { POST } = await import("@/app/api/revalidate/route");

    const response = await POST(
      postRequest({ kind: "content", slug: "best-time-to-visit-zion" }, "test-secret")
    );
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.revalidated).toEqual(["/guides/best-time-to-visit-zion"]);
  });

  it("rejects an unknown kind or missing slug", async () => {
    const { POST } = await import("@/app/api/revalidate/route");

    const response = await POST(postRequest({ kind: "spot", slug: "" }, "test-secret"));
    expect(response.status).toBe(400);
  });
});

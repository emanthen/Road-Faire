"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";

/** Client-side staff gate for everything under /dashboard — there's no server session
 * (the auth token lives in localStorage), so this is the only enforcement point. */
export default function DashboardGuard({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && (!user || !user.is_staff)) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  if (isLoading || !user || !user.is_staff) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        Loading…
      </div>
    );
  }

  return <>{children}</>;
}

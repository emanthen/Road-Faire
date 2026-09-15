"use client";

import SiteSettingsForm from "@/components/dashboard/settings/SiteSettingsForm";
import { siteSettingsAdminHooks } from "@/hooks/admin";

export default function SiteSettingsPage() {
  const { data, isLoading } = siteSettingsAdminHooks.useList();
  const existing = data?.results[0];

  return (
    <div>
      <h1 className="text-2xl font-semibold">Site settings</h1>
      <div className="mt-6">
        {isLoading ? (
          <p className="text-muted-foreground">Loading…</p>
        ) : (
          <SiteSettingsForm settings={existing} />
        )}
      </div>
    </div>
  );
}

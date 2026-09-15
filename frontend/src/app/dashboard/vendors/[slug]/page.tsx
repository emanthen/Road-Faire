"use client";

import { useParams } from "next/navigation";
import OffersSubTable from "@/components/dashboard/vendors/OffersSubTable";
import VendorForm from "@/components/dashboard/vendors/VendorForm";
import { partnersAdminHooks } from "@/hooks/admin";

export default function EditVendorPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: vendor, isLoading } = partnersAdminHooks.useDetail(slug);

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-semibold">Edit vendor</h1>
      <div className="mt-6 space-y-8">
        {isLoading ? (
          <p className="text-muted-foreground">Loading…</p>
        ) : vendor ? (
          <>
            <VendorForm vendor={vendor} />
            <OffersSubTable partnerId={vendor.id} />
          </>
        ) : (
          <p className="text-muted-foreground">Vendor not found.</p>
        )}
      </div>
    </div>
  );
}

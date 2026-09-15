import VendorForm from "@/components/dashboard/vendors/VendorForm";

export default function NewVendorPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold">New vendor</h1>
      <div className="mt-6">
        <VendorForm />
      </div>
    </div>
  );
}

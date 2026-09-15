import SpotForm from "@/components/dashboard/spots/SpotForm";

export default function NewSpotPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold">New spot</h1>
      <div className="mt-6">
        <SpotForm />
      </div>
    </div>
  );
}

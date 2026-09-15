import { planPdfUrl } from "@/lib/api";

export default function ExportPdfButton({ planId }: { planId: string }) {
  return (
    <a
      href={planPdfUrl(planId)}
      className="min-h-11 rounded border border-asphalt/30 px-4 py-2 text-sm font-medium text-ink hover:border-pine/60"
    >
      Export as PDF
    </a>
  );
}

import Image from "next/image";
import type { SpotPhoto } from "@/types/api";

export default function Gallery({ photos, spotName }: { photos: SpotPhoto[]; spotName: string }) {
  if (photos.length === 0) return null;

  const [primary, ...rest] = [...photos].sort((a, b) => Number(b.is_primary) - Number(a.is_primary));

  return (
    <div className="grid grid-cols-3 gap-2">
      <div className="relative col-span-2 aspect-[4/3] overflow-hidden bg-asphalt/10">
        <Image
          src={primary.url}
          alt={primary.alt_text || spotName}
          fill
          sizes="(min-width: 768px) 66vw, 100vw"
          className="object-cover"
          priority
        />
      </div>
      {rest.slice(0, 1).map((photo) => (
        <div key={photo.url} className="relative aspect-[4/3] overflow-hidden bg-asphalt/10">
          <Image
            src={photo.url}
            alt={photo.alt_text || spotName}
            fill
            sizes="33vw"
            className="object-cover"
          />
        </div>
      ))}
      {(primary.credit || rest[0]?.credit) && (
        <p className="col-span-3 text-xs text-asphalt">Photo: {primary.credit}</p>
      )}
    </div>
  );
}

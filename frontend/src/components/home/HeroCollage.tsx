import Image from "next/image";

/** Nine real NPS photos (public domain, see public/images/parks/SOURCES.txt) in a
 * tilted mosaic rather than one full-bleed background photo — more of the catalog
 * visible at once, and each tile's independent rotation is what actually reads as a
 * collage instead of a grid. */
const TILES = [
  { slug: "grca", name: "Grand Canyon", rotate: "-rotate-3" },
  { slug: "zion", name: "Zion", rotate: "rotate-2" },
  { slug: "yose", name: "Yosemite", rotate: "rotate-3" },
  { slug: "glac", name: "Glacier", rotate: "rotate-1" },
  { slug: "brca", name: "Bryce Canyon", rotate: "-rotate-2" },
  { slug: "yell", name: "Yellowstone", rotate: "-rotate-1" },
  { slug: "acad", name: "Acadia", rotate: "rotate-2" },
  { slug: "romo", name: "Rocky Mountain", rotate: "-rotate-3" },
  { slug: "seki", name: "Sequoia & Kings Canyon", rotate: "rotate-1" },
] as const;

export default function HeroCollage() {
  return (
    <div className="grid grid-cols-3 gap-3 sm:gap-4">
      {TILES.map((tile) => (
        <div
          key={tile.slug}
          className={`group relative aspect-square overflow-hidden rounded-2xl shadow-sm transition-transform duration-300 hover:z-10 hover:rotate-0 hover:scale-110 ${tile.rotate}`}
        >
          <Image
            src={`/images/parks/${tile.slug}.jpg`}
            alt={`NPS photo of ${tile.name}`}
            fill
            sizes="(min-width: 640px) 16vw, 30vw"
            className="object-cover"
          />
        </div>
      ))}
    </div>
  );
}

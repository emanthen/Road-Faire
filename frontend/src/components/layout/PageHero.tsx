import Image from "next/image";

/** Real NPS photos (public domain, see public/images/parks/SOURCES.txt), reused across
 * page heroes rather than tied 1:1 to page content — same source discipline as the
 * homepage hero, just not claiming each photo depicts that specific page's subject.
 * Same full-width pine-panel language as the homepage hero (scaled to one photo
 * instead of a nine-photo collage) — one consistent hero style across the site. */
export default function PageHero({
  title,
  description,
  imageSrc,
  imageAlt,
}: {
  title: string;
  description: string;
  imageSrc: string;
  imageAlt: string;
}) {
  return (
    <section className="mb-14 w-screen bg-pine" style={{ marginInline: "calc(50% - 50vw)" }}>
      <div className="mx-auto grid max-w-[1600px] gap-8 px-6 py-14 sm:grid-cols-2 sm:items-center sm:gap-16 sm:py-20">
        <div className="text-snow">
          <h1 className="text-3xl font-semibold sm:text-4xl">{title}</h1>
          <p className="mt-3 max-w-md text-snow/80">{description}</p>
        </div>
        <div className="relative aspect-[4/3] overflow-hidden rounded-2xl sm:aspect-[3/2]">
          <Image
            src={imageSrc}
            alt={imageAlt}
            fill
            sizes="(min-width: 640px) 50vw, 100vw"
            className="object-cover"
            priority
          />
        </div>
      </div>
    </section>
  );
}

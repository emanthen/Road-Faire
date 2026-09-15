import Image from "next/image";
import Link from "next/link";

/** One shared photo band + two distinct paths below it, rather than the same
 * image-plus-text block repeated twice — repeating an identical component reads as
 * a template, not a considered choice. */
export default function ClosingCtas() {
  return (
    <div>
      <div className="relative aspect-[21/9] overflow-hidden bg-asphalt/10">
        <Image
          src="/images/parks/grte.jpg"
          alt="The Teton Range at Grand Teton National Park"
          fill
          sizes="100vw"
          className="object-cover"
        />
      </div>

      <div className="grid divide-y divide-asphalt/20 border-b border-asphalt/20 sm:grid-cols-2 sm:divide-x sm:divide-y-0">
        <div className="flex flex-col gap-4 py-10 sm:pr-10">
          <h2 className="text-2xl font-semibold text-pine">Plan a full trip</h2>
          <p className="max-w-sm text-asphalt">
            Tell us where you&apos;re flying into and we&apos;ll build three fully
            costed road-trip options, day by day.
          </p>
          <Link
            href="/plan"
            className="mt-2 inline-block min-h-11 self-start rounded bg-pine px-6 py-2.5 font-medium text-snow hover:bg-ink active:scale-[0.98]"
          >
            Plan a trip
          </Link>
        </div>

        <div className="flex flex-col gap-4 py-10 sm:pl-10">
          <h2 className="text-2xl font-semibold text-pine">Read travel stories</h2>
          <p className="max-w-sm text-asphalt">
            Destination guides and trip write-ups, grounded in the same real fees
            and rules the planner uses.
          </p>
          <Link
            href="/guides"
            className="mt-2 inline-block min-h-11 self-start rounded border border-pine px-6 py-2.5 font-medium text-pine hover:bg-pine hover:text-snow active:scale-[0.98]"
          >
            Read stories
          </Link>
        </div>
      </div>
    </div>
  );
}

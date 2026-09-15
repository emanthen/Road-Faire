/** Always routes through /go/ — never a raw partner URL (BUILD_PROMPT §7).
 * rel="sponsored" tells search engines this is a paid/affiliate placement — only true
 * when Roadfare actually earns a commission. Informational-only listings (no commission
 * relationship) must pass sponsored={false} so we don't misrepresent them. */
export default function OfferLink({
  offerId,
  spotSlug,
  children,
  className,
  sponsored = true,
}: {
  offerId: string;
  spotSlug?: string;
  children: React.ReactNode;
  className?: string;
  sponsored?: boolean;
}) {
  const query = spotSlug ? `?spot=${encodeURIComponent(spotSlug)}` : "";
  return (
    <a
      href={`/go/${offerId}${query}`}
      className={className}
      rel={sponsored ? "sponsored nofollow" : "nofollow"}
    >
      {children}
    </a>
  );
}

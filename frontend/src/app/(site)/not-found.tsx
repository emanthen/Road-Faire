import Link from "next/link";

export default function NotFound() {
  return (
    <section className="px-6 py-16">
      <h1 className="text-3xl font-semibold text-pine">Page not found</h1>
      <p className="mt-2 text-asphalt">
        Try the <Link href="/spots">spot browser</Link> or head back{" "}
        <Link href="/">home</Link>.
      </p>
    </section>
  );
}

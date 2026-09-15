"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <section className="px-6 py-16">
      <h1 className="text-3xl font-semibold text-signal">Something broke</h1>
      <p className="mt-2 text-asphalt">Try again, or head back home if it keeps happening.</p>
      <button
        onClick={reset}
        className="mt-6 rounded bg-pine px-4 py-2 text-snow"
        type="button"
      >
        Try again
      </button>
    </section>
  );
}

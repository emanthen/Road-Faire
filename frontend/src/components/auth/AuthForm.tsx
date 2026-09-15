"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function AuthForm({ mode }: { mode: "login" | "register" }) {
  const { login, register } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      if (mode === "login") {
        await login(username, password);
      } else {
        await register(username, email, password);
      }
      router.push("/");
    } catch (err) {
      const detail = err instanceof ApiError ? err.detail : null;
      setError(typeof detail === "string" ? detail : "That didn't work. Check your details and try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex max-w-sm flex-col gap-6">
      <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
        Username
        <input
          type="text"
          required
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="min-h-11 rounded border border-asphalt/30 px-3 py-2 text-ink hover:border-pine/60"
        />
      </label>

      {mode === "register" && (
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="min-h-11 rounded border border-asphalt/30 px-3 py-2 text-ink hover:border-pine/60"
          />
        </label>
      )}

      <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
        Password
        <input
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="min-h-11 rounded border border-asphalt/30 px-3 py-2 text-ink hover:border-pine/60"
        />
      </label>

      <button
        type="submit"
        disabled={isSubmitting}
        className="min-h-11 self-start rounded bg-pine px-7 py-2.5 font-medium text-snow hover:bg-ink disabled:opacity-40"
      >
        {mode === "login" ? "Log in" : "Sign up"}
      </button>

      {error && <p className="text-signal">{error}</p>}
    </form>
  );
}

import type { Metadata } from "next";
import Link from "next/link";
import AuthForm from "@/components/auth/AuthForm";
import GoogleSignInButton from "@/components/auth/GoogleSignInButton";

export const metadata: Metadata = {
  title: "Log in - Roadfare",
  description: "Log in to your Roadfare account.",
};

export default function LoginPage() {
  return (
    <section className="px-6 py-16">
      <h1 className="text-3xl font-semibold text-pine">Log in</h1>
      <p className="mt-2 max-w-sm text-asphalt">
        No account yet?{" "}
        <Link href="/signup" className="text-pine underline">
          Sign up
        </Link>
        .
      </p>
      <div className="mt-8 flex flex-col gap-6">
        <GoogleSignInButton />
        <AuthForm mode="login" />
      </div>
    </section>
  );
}

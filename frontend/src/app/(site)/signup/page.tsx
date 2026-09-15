import type { Metadata } from "next";
import Link from "next/link";
import AuthForm from "@/components/auth/AuthForm";
import GoogleSignInButton from "@/components/auth/GoogleSignInButton";

export const metadata: Metadata = {
  title: "Sign up - Roadfare",
  description: "Create a Roadfare account.",
};

export default function SignupPage() {
  return (
    <section className="px-6 py-16">
      <h1 className="text-3xl font-semibold text-pine">Sign up</h1>
      <p className="mt-2 max-w-sm text-asphalt">
        Already have an account?{" "}
        <Link href="/login" className="text-pine underline">
          Log in
        </Link>
        .
      </p>
      <div className="mt-8 flex flex-col gap-6">
        <GoogleSignInButton />
        <AuthForm mode="register" />
      </div>
    </section>
  );
}

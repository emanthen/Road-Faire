"use client";

import Script from "next/script";
import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";
import { useAuth } from "@/lib/auth";

// Google's Identity Services library has no official TypeScript types — this covers
// only the two calls this component actually makes.
interface GoogleAccountsId {
  initialize: (config: {
    client_id: string;
    callback: (response: { credential: string }) => void;
  }) => void;
  renderButton: (parent: HTMLElement, options: { theme: string; size: string }) => void;
}

declare global {
  interface Window {
    google?: { accounts: { id: GoogleAccountsId } };
  }
}

const CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

/** Renders nothing if NEXT_PUBLIC_GOOGLE_CLIENT_ID isn't set — get a real client ID
 * from https://console.cloud.google.com/apis/credentials (OAuth client ID, "Web
 * application"), matching the backend's GOOGLE_OAUTH_CLIENT_ID. There is no working
 * default; without it, this is intentionally invisible rather than a broken button. */
export default function GoogleSignInButton() {
  const { loginWithGoogle } = useAuth();
  const router = useRouter();
  const buttonRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const clientId = CLIENT_ID;
    if (!clientId) return;

    function handleCredential(response: { credential: string }) {
      loginWithGoogle(response.credential)
        .then(() => router.push("/"))
        .catch(() => {});
    }

    function render(id: string) {
      if (!window.google || !buttonRef.current) return;
      window.google.accounts.id.initialize({ client_id: id, callback: handleCredential });
      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: "outline",
        size: "large",
      });
    }

    if (window.google) {
      render(clientId);
    } else {
      const interval = setInterval(() => {
        if (window.google) {
          clearInterval(interval);
          render(clientId);
        }
      }, 100);
      return () => clearInterval(interval);
    }
  }, [loginWithGoogle, router]);

  if (!CLIENT_ID) return null;

  return (
    <>
      <Script src="https://accounts.google.com/gsi/client" strategy="afterInteractive" />
      <div ref={buttonRef} />
    </>
  );
}

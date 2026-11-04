"use client";

import Script from "next/script";
import { useEffect, useRef } from "react";

const SITE_KEY = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;

// Cloudflare Turnstile CAPTCHA. Renders nothing when no site key is configured.
export default function Turnstile({ onToken }) {
  const box = useRef(null);
  const widgetId = useRef(null);

  useEffect(() => {
    if (!SITE_KEY) return undefined;
    let tries = 0;
    const timer = setInterval(() => {
      tries += 1;
      if (window.turnstile && box.current && widgetId.current === null) {
        widgetId.current = window.turnstile.render(box.current, {
          sitekey: SITE_KEY,
          callback: (token) => onToken(token),
          "expired-callback": () => onToken(""),
        });
        clearInterval(timer);
      }
      if (tries > 50) clearInterval(timer);
    }, 200);
    return () => clearInterval(timer);
  }, [onToken]);

  if (!SITE_KEY) return null;
  return (
    <>
      <Script src="https://challenges.cloudflare.com/turnstile/v0/api.js" strategy="lazyOnload" />
      <div ref={box} />
    </>
  );
}

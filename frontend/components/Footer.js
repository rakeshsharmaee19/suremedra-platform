import Link from "next/link";
import { company, nav } from "@/content/site";
import { ArrowUpRight } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-ink text-paper relative overflow-hidden">
      {/* Decorative gradients */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none opacity-20">
        <div className="absolute -bottom-[20%] -left-[10%] w-[50%] h-[80%] bg-brand blur-[120px] rounded-full"></div>
        <div className="absolute -top-[10%] -right-[10%] w-[40%] h-[60%] bg-gold blur-[120px] rounded-full"></div>
      </div>

      <div className="mx-auto max-w-6xl px-6 pt-20 pb-12 sm:px-8 relative z-10">
        <div className="grid gap-12 lg:grid-cols-[1.5fr_1fr_1fr]">
          <div className="max-w-md">
            <Link
              href="/"
              className="font-serif text-2xl font-semibold tracking-tight text-paper flex items-center gap-3"
            >
              <div className="w-10 h-10 bg-brand rounded-md flex items-center justify-center shadow-lg shadow-brand/20">
                <div className="w-4 h-4 bg-paper rounded-sm transform rotate-45"></div>
              </div>
              <span className="translate-y-[2px]">
                {company.shortName}
              </span>
            </Link>
            <p className="mt-6 text-[15px] leading-relaxed text-hairline">
              {company.tagline} {company.legalName} provides a dependable bridge between India's pharmaceutical manufacturing base and healthcare markets abroad.
            </p>
            <div className="mt-8 flex gap-4">
              {company.social.linkedin && (
                <a 
                  href={company.social.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-full border border-hairline/20 flex items-center justify-center text-hairline hover:bg-brand hover:border-brand hover:text-paper transition-all"
                >
                  <span className="sr-only">LinkedIn</span>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fillRule="evenodd" d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" clipRule="evenodd" />
                  </svg>
                </a>
              )}
            </div>
          </div>

          <div>
            <p className="text-sm font-semibold uppercase tracking-wider text-hairline/50 mb-6">
              Navigate
            </p>
            <ul className="space-y-4">
              {nav.map((item) => (
                <li key={item.href}>
                  <Link href={item.href} className="text-[15px] text-hairline hover:text-paper hover:translate-x-1 inline-block transition-all flex items-center gap-1 group">
                    {item.label}
                    <ArrowUpRight className="w-3 h-3 opacity-0 -translate-y-1 translate-x-1 group-hover:opacity-100 group-hover:translate-y-0 group-hover:translate-x-0 transition-all text-brand" />
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="text-sm font-semibold uppercase tracking-wider text-hairline/50 mb-6">
              Contact
            </p>
            <ul className="space-y-4 text-[15px] text-hairline">
              <li className="flex gap-3">
                <span className="text-brand">📍</span>
                <span>
                  {company.address.line1}<br />
                  {company.address.line2}
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-brand">✉️</span>
                <a href={`mailto:${company.email}`} className="hover:text-paper transition-colors">
                  {company.email}
                </a>
              </li>
              <li className="flex gap-3">
                <span className="text-brand">📞</span>
                <span>{company.phone}</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-16 flex flex-col gap-4 border-t border-hairline/10 pt-8 text-sm text-hairline/70 sm:flex-row sm:items-center sm:justify-between">
          <p>
            © {new Date().getFullYear()} {company.legalName}. All rights reserved.
          </p>
          <div className="flex gap-6">
            <Link href="/privacy-policy" className="hover:text-paper transition-colors">
              Privacy Policy
            </Link>
            <Link href="/terms" className="hover:text-paper transition-colors">
              Terms of Use
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

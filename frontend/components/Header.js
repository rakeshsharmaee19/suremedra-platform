"use client";

import Link from "next/link";
import { company, nav } from "@/content/site";
import { useEffect, useState } from "react";
import EnquiryLink from "./EnquiryLink";

export default function Header() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header 
      className={`sticky top-0 z-50 w-full transition-all duration-300 ${
        scrolled ? "glass py-3" : "bg-paper/0 py-5"
      }`}
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 sm:px-8">
        <Link
          href="/"
          className="font-serif text-xl font-semibold tracking-tight text-ink flex items-center gap-2"
        >
          {/* A small abstract cross/pill logo icon could go here */}
          <div className="w-8 h-8 bg-brand rounded-md flex items-center justify-center shadow-md shadow-brand/20">
            <div className="w-3 h-3 bg-paper rounded-sm transform rotate-45"></div>
          </div>
          <span className="translate-y-[1px]">
            {company.shortName}
          </span>
        </Link>

        <nav aria-label="Primary" className="hidden gap-8 md:flex">
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-[15px] font-medium text-ink-soft transition-all duration-200 hover:text-brand hover:-translate-y-[1px]"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <EnquiryLink className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white shadow-md shadow-brand/20 transition-all hover:bg-brand-mid active:scale-95 md:hidden" />

        <EnquiryLink className="hidden rounded-md bg-brand px-6 py-2.5 text-sm font-medium text-white shadow-md shadow-brand/20 transition-all hover:bg-brand-mid hover:shadow-lg hover:shadow-brand/30 hover:-translate-y-0.5 active:scale-95 md:inline-block" />
      </div>

      {/* mobile nav row - only visible when not fully scrolled to save space, or keep it always */}
      <nav
        aria-label="Primary mobile"
        className={`flex gap-5 overflow-x-auto border-t border-hairline/50 px-6 py-3 text-sm font-medium text-ink-soft sm:px-8 md:hidden transition-all duration-300 ${scrolled ? 'hidden' : 'block'}`}
      >
        {nav.map((item) => (
          <Link key={item.href} href={item.href} className="whitespace-nowrap transition-colors hover:text-brand">
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}

"use client";

import Link from "next/link";
import { Check, Plus } from "lucide-react";
import { useEnquiry } from "./EnquiryProvider";

export default function AddToEnquiryButton({ slug, name, size = "sm" }) {
  const { add, has, remove, ready } = useEnquiry();
  const added = ready && has(slug);
  const pad = size === "lg" ? "px-6 py-3 text-base" : "px-3 py-1.5 text-sm";

  if (added) {
    return (
      <span className="inline-flex items-center gap-2">
        <button
          type="button"
          onClick={() => remove(slug)}
          className={`inline-flex items-center gap-1.5 rounded-md border border-brand bg-brand/10 font-medium text-brand-mid transition hover:bg-brand/20 ${pad}`}
          aria-label={`Remove ${name} from enquiry list`}
        >
          <Check size={size === "lg" ? 18 : 15} /> Added
        </button>
        <Link href="/enquiry" className="text-sm text-brand-mid underline underline-offset-4">
          View list
        </Link>
      </span>
    );
  }
  return (
    <button
      type="button"
      onClick={() => add({ slug, name })}
      className={`inline-flex items-center gap-1.5 rounded-md bg-brand font-medium text-white shadow-sm transition hover:bg-brand-mid active:scale-95 ${pad}`}
      aria-label={`Add ${name} to enquiry list`}
    >
      <Plus size={size === "lg" ? 18 : 15} /> Add to enquiry
    </button>
  );
}

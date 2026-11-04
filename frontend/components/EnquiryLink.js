"use client";

import Link from "next/link";
import { ClipboardList } from "lucide-react";
import { useEnquiry } from "./EnquiryProvider";

export default function EnquiryLink({ className = "" }) {
  const { items, ready } = useEnquiry();
  const count = ready ? items.length : 0;
  return (
    <Link href="/enquiry" className={className} aria-label={`Enquiry list, ${count} item${count === 1 ? "" : "s"}`}>
      <ClipboardList size={16} className="mr-2 inline-block" />
      Enquiry list
      {count > 0 ? (
        <span className="ml-2 inline-flex min-w-5 items-center justify-center rounded-full bg-white/90 px-1.5 text-xs font-semibold text-brand-mid">
          {count}
        </span>
      ) : null}
    </Link>
  );
}

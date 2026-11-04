"use client";

import Link from "next/link";
import { useCallback, useRef, useState } from "react";
import { Trash2 } from "lucide-react";
import { useEnquiry } from "./EnquiryProvider";
import Turnstile from "./Turnstile";

const field =
  "w-full rounded-md border border-hairline bg-paper px-4 py-3 text-[15px] text-ink placeholder:text-ink-soft/60 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20";

function newKey() {
  return typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : undefined;
}

export default function EnquiryForm() {
  const { items, ready, update, remove, clear } = useEnquiry();
  const [form, setForm] = useState({ name: "", company: "", email: "", phone: "", country: "", message: "", website: "" });
  const [token, setToken] = useState("");
  const [state, setState] = useState({ status: "idle", reference: "", error: "", fieldErrors: {} });
  const idempotencyKey = useRef(newKey());
  const onToken = useCallback((t) => setToken(t), []);

  const set = (name) => (e) => setForm((f) => ({ ...f, [name]: e.target.value }));

  async function submit(e) {
    e.preventDefault();
    if (items.length === 0) {
      setState({ status: "error", reference: "", error: "Add at least one medicine to your enquiry list first.", fieldErrors: {} });
      return;
    }
    setState({ status: "sending", reference: "", error: "", fieldErrors: {} });
    try {
      const res = await fetch("/api/v1/public/enquiries", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          idempotency_key: idempotencyKey.current,
          turnstile_token: token,
          items: items.map((i) => ({ formulation: i.slug, quantity: Number(i.quantity) || 1, unit: i.unit || "" })),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.status === 201) {
        setState({ status: "done", reference: data.reference, error: "", fieldErrors: {} });
        clear();
        idempotencyKey.current = newKey();
        return;
      }
      if (res.status === 429) {
        setState({ status: "error", reference: "", error: "Too many enquiries from your connection. Please try again later or email us directly.", fieldErrors: {} });
        return;
      }
      setState({
        status: "error",
        reference: "",
        error: data.detail || "Please check the highlighted fields and try again.",
        fieldErrors: typeof data === "object" ? data : {},
      });
    } catch {
      setState({ status: "error", reference: "", error: "Could not reach the server. Please check your connection and try again.", fieldErrors: {} });
    }
  }

  if (state.status === "done") {
    return (
      <div className="rounded-lg border border-brand/30 bg-brand/5 p-8" role="status">
        <h2 className="font-serif text-2xl font-semibold text-ink">Thank you, your enquiry is with our team.</h2>
        <p className="mt-3 text-ink-soft">
          Your reference number is <strong className="text-ink">{state.reference}</strong>. We have sent a confirmation to
          your email and will reply with availability shortly.
        </p>
        <Link href="/catalogue" className="mt-6 inline-block text-brand-mid underline underline-offset-4">
          Continue browsing the catalogue
        </Link>
      </div>
    );
  }

  const err = (name) =>
    state.fieldErrors[name] ? (
      <span className="mt-1 block text-sm text-red-600">{[].concat(state.fieldErrors[name]).join(" ")}</span>
    ) : null;

  return (
    <form onSubmit={submit} className="grid gap-10 lg:grid-cols-[1.2fr_1fr]" noValidate>
      <section aria-labelledby="items-heading">
        <h2 id="items-heading" className="font-serif text-xl font-semibold text-ink">Medicines you are asking about</h2>
        {!ready ? (
          <p className="mt-4 text-ink-soft">Loading your list...</p>
        ) : items.length === 0 ? (
          <div className="mt-4 rounded-md border border-dashed border-hairline p-6 text-ink-soft">
            Your list is empty.{" "}
            <Link href="/catalogue" className="text-brand-mid underline underline-offset-4">Browse the catalogue</Link> and
            choose the medicines you need.
          </div>
        ) : (
          <ul className="mt-4 divide-y divide-hairline rounded-md border border-hairline">
            {items.map((item) => (
              <li key={item.slug} className="flex flex-wrap items-center gap-3 p-4">
                <span className="min-w-0 flex-1 basis-48 text-[15px] font-medium text-ink">{item.name}</span>
                <input
                  type="number" min="1" inputMode="numeric" value={item.quantity}
                  onChange={(e) => update(item.slug, { quantity: e.target.value })}
                  className={`${field} !w-28 !py-2`} aria-label={`Quantity for ${item.name}`}
                />
                <input
                  type="text" value={item.unit} placeholder="unit (e.g. strips)"
                  onChange={(e) => update(item.slug, { unit: e.target.value })}
                  className={`${field} !w-36 !py-2`} aria-label={`Unit for ${item.name}`}
                />
                <button type="button" onClick={() => remove(item.slug)} className="rounded p-2 text-ink-soft hover:bg-red-50 hover:text-red-600" aria-label={`Remove ${item.name}`}>
                  <Trash2 size={18} />
                </button>
              </li>
            ))}
          </ul>
        )}
        {err("items")}
      </section>

      <section aria-labelledby="contact-heading" className="grid content-start gap-4">
        <h2 id="contact-heading" className="font-serif text-xl font-semibold text-ink">Your details</h2>
        <label className="block"><span className="mb-1 block text-sm text-ink-soft">Full name *</span>
          <input required className={field} value={form.name} onChange={set("name")} autoComplete="name" />{err("name")}</label>
        <label className="block"><span className="mb-1 block text-sm text-ink-soft">Company</span>
          <input className={field} value={form.company} onChange={set("company")} autoComplete="organization" />{err("company")}</label>
        <label className="block"><span className="mb-1 block text-sm text-ink-soft">Email *</span>
          <input required type="email" className={field} value={form.email} onChange={set("email")} autoComplete="email" />{err("email")}</label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block"><span className="mb-1 block text-sm text-ink-soft">Phone / WhatsApp</span>
            <input className={field} value={form.phone} onChange={set("phone")} autoComplete="tel" />{err("phone")}</label>
          <label className="block"><span className="mb-1 block text-sm text-ink-soft">Country</span>
            <input className={field} value={form.country} onChange={set("country")} autoComplete="country-name" />{err("country")}</label>
        </div>
        <label className="block"><span className="mb-1 block text-sm text-ink-soft">Message (optional)</span>
          <textarea rows={4} className={field} value={form.message} onChange={set("message")} />{err("message")}</label>

        {/* Honeypot: hidden from people, bots fill it in. */}
        <div aria-hidden="true" style={{ position: "absolute", left: "-10000px" }}>
          <label>Website<input tabIndex={-1} autoComplete="off" value={form.website} onChange={set("website")} /></label>
        </div>

        <Turnstile onToken={onToken} />

        {state.error ? <p role="alert" className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{state.error}</p> : null}

        <button
          type="submit" disabled={state.status === "sending"}
          className="mt-2 w-fit rounded-md bg-brand px-7 py-3 text-base font-medium text-white shadow-md transition hover:bg-brand-mid disabled:opacity-60"
        >
          {state.status === "sending" ? "Sending..." : "Ask about availability"}
        </button>
        <p className="text-xs text-ink-soft">
          We only use your details to reply to this enquiry. No prices are shown online; we confirm availability and send an invoice by email.
        </p>
      </section>
    </form>
  );
}

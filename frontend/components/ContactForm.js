"use client";

import { useState } from "react";
import { company } from "@/content/site";

const fieldClasses =
  "w-full rounded-sm border border-hairline bg-paper px-4 py-3 text-[15px] text-ink placeholder:text-ink-soft/60 focus:border-brand focus:outline-none";

export default function ContactForm() {
  const [form, setForm] = useState({
    name: "",
    company: "",
    country: "",
    email: "",
    message: "",
  });

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const subject = `Export enquiry from ${form.name || "website visitor"}`;
    const body = [
      `Name: ${form.name}`,
      `Company: ${form.company}`,
      `Country: ${form.country}`,
      `Email: ${form.email}`,
      "",
      form.message,
    ].join("\n");

    window.location.href = `mailto:${company.email}?subject=${encodeURIComponent(
      subject
    )}&body=${encodeURIComponent(body)}`;
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-5" noValidate>
      <div className="grid gap-5 sm:grid-cols-2">
        <label className="block">
          <span className="mb-1.5 block text-sm text-ink-soft">Full name</span>
          <input
            required
            type="text"
            name="name"
            value={form.name}
            onChange={update("name")}
            className={fieldClasses}
            autoComplete="name"
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block text-sm text-ink-soft">Company</span>
          <input
            type="text"
            name="company"
            value={form.company}
            onChange={update("company")}
            className={fieldClasses}
            autoComplete="organization"
          />
        </label>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <label className="block">
          <span className="mb-1.5 block text-sm text-ink-soft">Country</span>
          <input
            type="text"
            name="country"
            value={form.country}
            onChange={update("country")}
            className={fieldClasses}
            autoComplete="country-name"
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block text-sm text-ink-soft">Email</span>
          <input
            required
            type="email"
            name="email"
            value={form.email}
            onChange={update("email")}
            className={fieldClasses}
            autoComplete="email"
          />
        </label>
      </div>

      <label className="block">
        <span className="mb-1.5 block text-sm text-ink-soft">
          What are you looking to source?
        </span>
        <textarea
          required
          name="message"
          rows={5}
          value={form.message}
          onChange={update("message")}
          className={fieldClasses}
        />
      </label>

      <button
        type="submit"
        className="mt-2 w-fit rounded-sm bg-brand px-6 py-3 text-sm text-paper transition-colors hover:bg-brand-mid"
      >
        Send enquiry
      </button>

      <p className="text-xs text-ink-soft">
        This opens your email client with the message pre-filled to{" "}
        {company.email}. In-page submission with confirmation goes live once
        this form is connected to the enquiry backend in Phase 2.
      </p>
    </form>
  );
}

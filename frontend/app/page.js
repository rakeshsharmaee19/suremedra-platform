import Link from "next/link";
import { Section, Eyebrow } from "@/components/Ui";
import {
  company,
  stats,
  capabilities,
  certifications,
  productCategories,
} from "@/content/site";
import { 
  ArrowRight, 
  ShieldCheck, 
  Globe2, 
  FileCheck2, 
  Building2,
  Pill,
  Activity,
  HeartPulse,
  Syringe,
  Leaf
} from "lucide-react";

export const metadata = {
  title: `${company.shortName} — Pharmaceutical Exports from India`,
  description:
    "GMP-certified pharmaceutical exports with complete regulatory documentation, serving international buyers across 35+ countries.",
  alternates: { canonical: "/" },
};

// Map categories to icons
const getCategoryIcon = (name) => {
  const lowercase = name.toLowerCase();
  if (lowercase.includes("antibiotic")) return <Pill className="w-6 h-6 text-brand" />;
  if (lowercase.includes("analgesic")) return <Activity className="w-6 h-6 text-brand" />;
  if (lowercase.includes("cardiac")) return <HeartPulse className="w-6 h-6 text-brand" />;
  if (lowercase.includes("diabetic")) return <Syringe className="w-6 h-6 text-brand" />;
  if (lowercase.includes("vitamin")) return <Leaf className="w-6 h-6 text-brand" />;
  if (lowercase.includes("topical")) return <ShieldCheck className="w-6 h-6 text-brand" />;
  return <Pill className="w-6 h-6 text-brand" />;
};

export default function HomePage() {
  return (
    <>
      {/* Premium Hero */}
      <section className="relative overflow-hidden pt-16 pb-20 sm:pt-24 sm:pb-32 min-h-[80vh] flex items-center bg-paper">
        {/* Abstract Background Gradients */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
          <div className="absolute top-[-10%] right-[-5%] w-[50%] h-[60%] bg-brand/10 blur-[120px] rounded-full"></div>
          <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[50%] bg-gold/10 blur-[100px] rounded-full"></div>
          
          {/* subtle grid pattern */}
          <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] opacity-5"></div>
        </div>

        <div className="mx-auto max-w-6xl px-6 sm:px-8 relative z-10 w-full">
          <div className="grid gap-16 lg:grid-cols-[1.2fr_1fr] lg:gap-24 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand/10 border border-brand/20 text-brand text-sm font-medium mb-8">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-brand"></span>
                </span>
                Verified Global Exporter
              </div>
              <h1 className="max-w-xl font-serif text-5xl font-semibold leading-[1.1] text-ink sm:text-6xl lg:text-7xl">
                {company.tagline}
              </h1>
              <p className="mt-8 max-w-lg text-lg sm:text-xl leading-relaxed text-ink-soft">
                {company.legalName} sources, certifies and exports quality-assured
                pharmaceutical formulations to buyers abroad — every shipment backed
                by verifiable licenses and complete regulatory paperwork.
              </p>
              <div className="mt-10 flex flex-wrap gap-4">
                <Link
                  href="/contact"
                  className="group flex items-center justify-center gap-2 rounded-md bg-brand px-6 py-3.5 text-[15px] font-medium text-paper shadow-lg shadow-brand/25 transition-all hover:bg-brand-mid hover:shadow-brand/40 hover:-translate-y-0.5 active:scale-95"
                >
                  Start an enquiry
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </Link>
                <Link
                  href="/certifications"
                  className="flex items-center justify-center rounded-md bg-white px-6 py-3.5 text-[15px] font-medium text-ink shadow-sm border border-hairline transition-all hover:border-brand hover:text-brand hover:shadow-md active:scale-95"
                >
                  View our certifications
                </Link>
              </div>
            </div>

            <div className="relative lg:h-[500px] w-full flex flex-col justify-center gap-6">
              {stats.map((stat, i) => (
                <div 
                  key={stat.label} 
                  className={`glass-dark p-6 rounded-xl relative overflow-hidden transition-transform duration-500 hover:-translate-y-1 ${
                    i === 0 ? "mr-12" : i === 1 ? "ml-12" : i === 2 ? "mr-8" : "ml-4"
                  }`}
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-brand/20 blur-[50px] rounded-full -translate-y-1/2 translate-x-1/2"></div>
                  <dt className="text-sm font-medium text-paper/70 uppercase tracking-wide">{stat.label}</dt>
                  <dd className="mt-2 font-serif text-4xl sm:text-5xl font-semibold text-paper flex items-baseline gap-2">
                    {stat.value}
                  </dd>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <Section shaded className="relative">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <Eyebrow className="justify-center">What we handle for you</Eyebrow>
          <h2 className="mt-4 font-serif text-3xl sm:text-4xl font-semibold text-ink leading-tight">
            Three parts of the export process, under one roof.
          </h2>
        </div>
        <div className="grid gap-8 sm:grid-cols-3">
          {[
            { icon: <Building2 className="w-8 h-8 text-brand" />, ...capabilities[0] },
            { icon: <ShieldCheck className="w-8 h-8 text-brand" />, ...capabilities[1] },
            { icon: <Globe2 className="w-8 h-8 text-brand" />, ...capabilities[2] },
          ].map((item, i) => (
            <div key={item.title} className="bg-paper rounded-2xl p-8 shadow-sm border border-hairline transition-all duration-300 hover:shadow-xl hover:shadow-brand/5 hover:-translate-y-2 group">
              <div className="w-14 h-14 bg-paper-shade rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                {item.icon}
              </div>
              <h3 className="font-serif text-xl font-semibold text-ink">
                {item.title}
              </h3>
              <p className="mt-4 text-[15px] leading-relaxed text-ink-soft">
                {item.body}
              </p>
            </div>
          ))}
        </div>
      </Section>

      {/* Certifications teaser */}
      <Section>
        <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between gap-6 mb-12">
          <div className="max-w-xl">
            <Eyebrow>Licenses &amp; certifications</Eyebrow>
            <h2 className="mt-4 font-serif text-3xl sm:text-4xl font-semibold text-ink">
              Every claim, backed by a document.
            </h2>
          </div>
          <Link
            href="/certifications"
            className="group flex items-center gap-2 text-sm font-medium text-brand transition-all hover:text-brand-mid"
          >
            View all {certifications.length} certifications
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {certifications.slice(0, 4).map((cert) => (
            <div key={cert.id} className="flex gap-5 p-6 rounded-xl border border-hairline hover:border-brand/30 hover:bg-paper-shade/50 transition-all group">
              <div className="flex-shrink-0 w-12 h-12 bg-paper-shade group-hover:bg-brand/10 rounded-full flex items-center justify-center transition-colors">
                <FileCheck2 className="w-5 h-5 text-brand" />
              </div>
              <div>
                <span className="inline-block px-2 py-0.5 rounded text-xs font-semibold bg-brand/10 text-brand mb-2">Valid till {cert.validTill}</span>
                <h3 className="text-[16px] font-semibold text-ink leading-snug">{cert.title}</h3>
                <p className="mt-1 text-sm text-ink-soft">{cert.issuer}</p>
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Product categories */}
      <Section shaded>
        <div className="flex flex-col lg:flex-row gap-12 lg:gap-24 mb-16 items-end">
          <div className="max-w-2xl">
            <Eyebrow>Export catalogue</Eyebrow>
            <h2 className="mt-4 font-serif text-3xl sm:text-4xl font-semibold text-ink leading-tight">
              Formulation categories we export.
            </h2>
            <p className="mt-4 text-[16px] leading-relaxed text-ink-soft">
              Full product-level catalogue with specifications and pricing goes live
              in the next phase of this platform. For now, here is where our current
              export range sits.
            </p>
          </div>
          <div className="flex-shrink-0">
             <Link
                href="/catalogue"
                className="group flex items-center gap-2 rounded-full bg-white px-5 py-2.5 text-sm font-medium text-ink shadow-sm border border-hairline transition-all hover:border-brand hover:text-brand"
              >
                Explore categories
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </Link>
          </div>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {productCategories.map((cat) => (
            <div key={cat.name} className="bg-paper p-8 rounded-2xl border border-hairline/50 shadow-sm hover:shadow-xl hover:shadow-brand/5 transition-all group">
              <div className="w-12 h-12 bg-paper-shade rounded-full flex items-center justify-center mb-6 group-hover:bg-brand/10 group-hover:scale-110 transition-all duration-300">
                {getCategoryIcon(cat.name)}
              </div>
              <h3 className="font-serif text-xl font-semibold text-ink">
                {cat.name}
              </h3>
              <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">
                {cat.description}
              </p>
            </div>
          ))}
        </div>
      </Section>

      {/* CTA band */}
      <Section className="!py-0 relative -mb-16 z-20">
        <div className="relative overflow-hidden rounded-2xl bg-brand p-10 sm:p-16 shadow-2xl shadow-brand/20 text-center sm:text-left">
          {/* Decorative shapes */}
          <div className="absolute top-0 right-0 w-full h-full overflow-hidden pointer-events-none">
            <div className="absolute -top-[50%] -right-[10%] w-[60%] h-[200%] bg-white/10 blur-[50px] rounded-full transform -rotate-45"></div>
            <div className="absolute -bottom-[50%] -left-[10%] w-[40%] h-[150%] bg-white/5 blur-[40px] rounded-full"></div>
          </div>
          
          <div className="relative z-10 flex flex-col items-center gap-8 sm:flex-row sm:justify-between">
            <div className="max-w-xl">
              <h2 className="font-serif text-3xl sm:text-4xl font-semibold text-paper leading-tight">
                Sourcing pharmaceuticals for import?
              </h2>
              <p className="mt-4 text-[16px] text-paper/80 leading-relaxed">
                Tell us your formulation and destination-market requirements —
                we&apos;ll respond with documentation and availability within 24 hours.
              </p>
            </div>
            <Link
              href="/contact"
              className="whitespace-nowrap flex-shrink-0 group rounded-md bg-paper px-8 py-4 text-[15px] font-semibold text-brand shadow-lg transition-all hover:bg-white hover:scale-105 hover:shadow-xl active:scale-95"
            >
              Start an enquiry
            </Link>
          </div>
        </div>
      </Section>
    </>
  );
}

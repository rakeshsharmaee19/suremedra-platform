import Link from "next/link";
import { notFound } from "next/navigation";
import { PageHeader, Section, SpecRow } from "@/components/Ui";
import AddToEnquiryButton from "@/components/AddToEnquiryButton";
import { getFormulation } from "@/lib/api";
import { siteUrl } from "@/lib/site";

async function load(slug) {
  try {
    return await getFormulation(slug);
  } catch {
    return undefined; // API down: show an error rather than a false 404
  }
}

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const f = await load(slug);
  if (!f) return { title: "Medicine not found", robots: { index: false } };
  return {
    title: `${f.display_name}: Export from India`,
    description:
      f.description?.slice(0, 160) ||
      `${f.display_name} available for export from India. Ask Suremedra about availability, documentation and shipping.`,
    alternates: { canonical: `/catalogue/${f.slug}` },
    robots: f.is_indexable ? undefined : { index: false, follow: true },
  };
}

export default async function FormulationPage({ params }) {
  const { slug } = await params;
  const f = await load(slug);
  if (f === null) notFound();
  if (f === undefined) {
    return (
      <Section>
        <p role="alert" className="rounded-md bg-amber-50 p-6 text-amber-900">
          This page is temporarily unavailable. Please try again shortly or <Link href="/contact" className="underline">contact us</Link>.
        </p>
      </Section>
    );
  }

  const breadcrumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: siteUrl },
      { "@type": "ListItem", position: 2, name: "Catalogue", item: `${siteUrl}/catalogue` },
      { "@type": "ListItem", position: 3, name: f.display_name, item: `${siteUrl}/catalogue/${f.slug}` },
    ],
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbs) }} />
      <PageHeader kicker={f.medicine_type.name} title={f.display_name} />
      <Section>
        <nav aria-label="Breadcrumb" className="mb-8 text-sm text-ink-soft">
          <Link href="/" className="hover:text-brand">Home</Link> / <Link href="/catalogue" className="hover:text-brand">Catalogue</Link> / {f.display_name}
        </nav>
        <div className="grid gap-12 lg:grid-cols-[1.4fr_1fr]">
          <div>
            <h2 className="font-serif text-2xl font-semibold text-ink">Composition</h2>
            <dl className="mt-4 border-t border-hairline">
              {f.compositions.map((c) => (
                <SpecRow key={c.slug} label={c.name} value={c.strength || "As per formulation"} />
              ))}
              <SpecRow label="Form" value={f.medicine_type.name} />
            </dl>
            {f.description ? (
              <div className="mt-10">
                <h2 className="font-serif text-2xl font-semibold text-ink">About this formulation</h2>
                <p className="mt-4 whitespace-pre-line leading-relaxed text-ink-soft">{f.description}</p>
              </div>
            ) : null}
          </div>
          <aside className="h-fit rounded-lg border border-hairline bg-paper-shade p-6">
            <h2 className="font-serif text-lg font-semibold text-ink">Ask about availability</h2>
            <p className="mt-2 text-[15px] leading-relaxed text-ink-soft">
              Add this to your enquiry list. We confirm stock, share documentation and send an invoice by email.
            </p>
            <div className="mt-5"><AddToEnquiryButton slug={f.slug} name={f.display_name} size="lg" /></div>
          </aside>
        </div>
      </Section>
    </>
  );
}

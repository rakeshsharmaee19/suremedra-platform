import { PageHeader, Section } from "@/components/Ui";
import { certifications, company } from "@/content/site";

export const metadata = {
  title: "Certifications & Licenses",
  description:
    "Suremedra Enterprises' pharmaceutical export licenses, WHO-GMP and quality certifications, available for buyer verification.",
  alternates: { canonical: "/certifications" },
};

export default function CertificationsPage() {
  return (
    <>
      <PageHeader
        kicker="Certifications & licenses"
        title="Every document that lets us export, in one place."
        lede="These are the active licenses and certifications behind our operations. Full certified copies are shared directly with verified buyers as part of due diligence."
      />

      <Section>
        <ol className="divide-y divide-hairline border-y border-hairline">
          {certifications.map((cert) => (
            <li key={cert.id} className="flex flex-col gap-4 py-8 sm:flex-row sm:gap-8">
              <span className="font-serif text-2xl text-gold sm:w-16 sm:shrink-0">
                {cert.id}
              </span>

              <div className="flex-1">
                <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
                  <h2 className="font-serif text-xl font-semibold text-ink">
                    {cert.title}
                  </h2>
                  <span className="text-sm text-ink-soft">
                    Valid till {cert.validTill}
                  </span>
                </div>
                <p className="mt-2 text-[15px] leading-relaxed text-ink-soft">
                  {cert.description}
                </p>
                <dl className="mt-4 flex flex-wrap gap-x-8 gap-y-1 text-sm text-ink-soft">
                  <div className="flex gap-2">
                    <dt className="text-ink-soft">Issuing authority:</dt>
                    <dd className="text-ink">{cert.issuer}</dd>
                  </div>
                  <div className="flex gap-2">
                    <dt className="text-ink-soft">Issued:</dt>
                    <dd className="text-ink">{cert.issued}</dd>
                  </div>
                </dl>
              </div>
            </li>
          ))}
        </ol>

        <p className="mt-10 max-w-xl text-sm leading-relaxed text-ink-soft">
          Need a certified copy for your import registration?{" "}
          <a
            href={`mailto:${company.email}?subject=Certification document request`}
            className="text-brand underline decoration-hairline underline-offset-4 hover:decoration-brand"
          >
            Request documents by email
          </a>{" "}
          and we&apos;ll share verified copies directly.
        </p>
      </Section>
    </>
  );
}

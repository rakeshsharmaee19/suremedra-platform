import { PageHeader, Section } from "@/components/Ui";
import { company } from "@/content/site";

export const metadata = {
  title: "Terms of Use",
  description: `Terms of Use for ${company.legalName}.`,
  alternates: { canonical: "/terms" },
  robots: { index: false, follow: true },
};

export default function TermsPage() {
  return (
    <>
      <PageHeader kicker="Legal" title="Terms of Use" />
      <Section className="max-w-3xl">
        <div className="space-y-6 text-[15px] leading-relaxed text-ink-soft">
          <p className="text-sm text-ink-soft">
            Placeholder text — to be replaced with counsel-reviewed copy before
            launch. Last updated: [date].
          </p>

          <p>
            These Terms of Use govern access to and use of this website by{" "}
            {company.legalName}. By using this site, you agree to these terms.
          </p>

          <h2 className="font-serif text-lg font-semibold text-ink">
            Website content
          </h2>
          <p>
            Product categories, certifications and company information on this
            site are provided for informational purposes. Formal quotations,
            product specifications and terms of sale are confirmed directly
            between {company.shortName} and the buyer, in writing.
          </p>

          <h2 className="font-serif text-lg font-semibold text-ink">
            No online ordering (current phase)
          </h2>
          <p>
            This website does not currently process orders or payments online.
            All export transactions are conducted directly with our team under
            a separately agreed contract.
          </p>

          <h2 className="font-serif text-lg font-semibold text-ink">
            Contact
          </h2>
          <p>
            Questions about these terms can be sent to{" "}
            <a href={`mailto:${company.email}`} className="text-brand hover:underline">
              {company.email}
            </a>
            .
          </p>
        </div>
      </Section>
    </>
  );
}

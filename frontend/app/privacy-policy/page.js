import { PageHeader, Section } from "@/components/Ui";
import { company } from "@/content/site";

export const metadata = {
  title: "Privacy Policy",
  description: `Privacy Policy for ${company.legalName}.`,
  alternates: { canonical: "/privacy-policy" },
  robots: { index: false, follow: true },
};

export default function PrivacyPolicyPage() {
  return (
    <>
      <PageHeader kicker="Legal" title="Privacy Policy" />
      <Section className="max-w-3xl">
        <div className="prose-legal space-y-6 text-[15px] leading-relaxed text-ink-soft">
          <p className="text-sm text-ink-soft">
            Placeholder text — to be replaced with counsel-reviewed copy before
            launch. Last updated: [date].
          </p>

          <p>
            {company.legalName} (&ldquo;we&rdquo;, &ldquo;us&rdquo;) respects
            your privacy. This policy explains what information we collect
            through this website, how we use it, and the choices available to
            you.
          </p>

          <h2 className="font-serif text-lg font-semibold text-ink">
            Information we collect
          </h2>
          <p>
            When you submit an enquiry through our contact form, we collect the
            name, company, country, email address and message you provide.
            We do not collect payment information through this website.
          </p>

          <h2 className="font-serif text-lg font-semibold text-ink">
            How we use it
          </h2>
          <p>
            Information submitted is used solely to respond to your enquiry —
            confirming product availability, sharing documentation, and
            discussing export terms. We do not sell or share your information
            with third parties for marketing purposes.
          </p>

          <h2 className="font-serif text-lg font-semibold text-ink">
            Contact
          </h2>
          <p>
            Questions about this policy can be sent to{" "}
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

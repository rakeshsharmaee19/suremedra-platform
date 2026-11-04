import { PageHeader, Section } from "@/components/Ui";
import ContactForm from "@/components/ContactForm";
import { company } from "@/content/site";

export const metadata = {
  title: "Contact",
  description:
    "Get in touch with Suremedra Enterprises for pharmaceutical export enquiries, documentation requests and bulk sourcing.",
  alternates: { canonical: "/contact" },
};

export default function ContactPage() {
  return (
    <>
      <PageHeader
        kicker="Contact"
        title="Tell us what you're looking to source."
        lede="Reach out directly, or send an enquiry below and we'll respond with availability, documentation and next steps."
      />

      <Section>
        <div className="grid gap-14 lg:grid-cols-[1fr_1.3fr] lg:gap-20">
          <div>
            <h2 className="font-serif text-lg font-semibold text-ink">
              Registered office
            </h2>
            <address className="mt-3 text-[15px] not-italic leading-relaxed text-ink-soft">
              {company.legalName}
              <br />
              {company.address.line1}
              <br />
              {company.address.line2}
            </address>

            <dl className="mt-8 space-y-3 border-t border-hairline pt-6 text-[15px]">
              <div className="flex justify-between gap-4">
                <dt className="text-ink-soft">Email</dt>
                <dd>
                  <a href={`mailto:${company.email}`} className="text-brand hover:underline">
                    {company.email}
                  </a>
                </dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-ink-soft">Phone</dt>
                <dd className="text-ink">{company.phone}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-ink-soft">WhatsApp</dt>
                <dd className="text-ink">{company.whatsapp}</dd>
              </div>
            </dl>
          </div>

          <ContactForm />
        </div>
      </Section>
    </>
  );
}

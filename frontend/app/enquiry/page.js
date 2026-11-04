import { PageHeader, Section } from "@/components/Ui";
import EnquiryForm from "@/components/EnquiryForm";

export const metadata = {
  title: "Your enquiry list",
  description: "Ask about availability of the medicines you need.",
  robots: { index: false, follow: false },
};

export default function EnquiryPage() {
  return (
    <>
      <PageHeader
        kicker="Availability enquiry"
        title="Ask us about the medicines you need."
        lede="Choose quantities, tell us who you are, and our team will confirm availability and send you an invoice by email."
      />
      <Section>
        <EnquiryForm />
      </Section>
    </>
  );
}

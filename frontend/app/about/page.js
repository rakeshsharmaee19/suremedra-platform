import { PageHeader, Section, Eyebrow, SpecRow } from "@/components/Ui";
import { company, mission, leadership, exportCapabilities } from "@/content/site";

export const metadata = {
  title: "About Us",
  description:
    "Suremedra Enterprises' vision, mission, leadership and export capabilities as a GMP-certified pharmaceutical exporter.",
  alternates: { canonical: "/about" },
};

export default function AboutPage() {
  return (
    <>
      <PageHeader
        kicker="About us"
        title={`Built to make ${company.shortName} a dependable name in export pharma.`}
        lede={`${company.legalName} was founded in ${company.foundedYear} to give international buyers a single, accountable source for quality-assured pharmaceutical formulations.`}
      />

      {/* Vision / Mission */}
      <Section>
        <div className="grid gap-10 sm:grid-cols-2 sm:gap-16">
          <div>
            <Eyebrow>Vision</Eyebrow>
            <p className="mt-4 font-serif text-xl leading-snug text-ink">
              {mission.vision}
            </p>
          </div>
          <div>
            <Eyebrow>Mission</Eyebrow>
            <p className="mt-4 font-serif text-xl leading-snug text-ink">
              {mission.mission}
            </p>
          </div>
        </div>
      </Section>

      {/* Leadership */}
      <Section shaded>
        <Eyebrow>Leadership</Eyebrow>
        <h2 className="mt-3 max-w-md font-serif text-3xl font-semibold text-ink">
          The people accountable for every shipment.
        </h2>
        <div className="mt-10 grid gap-8 border-t border-hairline pt-10 sm:grid-cols-2">
          {leadership.map((person) => (
            <div key={person.name}>
              <p className="font-serif text-lg font-semibold text-ink">
                {person.name}
              </p>
              <p className="mt-1 text-sm text-brand-mid">{person.role}</p>
              <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">
                {person.bio}
              </p>
            </div>
          ))}
        </div>
      </Section>

      {/* Export capabilities spec sheet */}
      <Section>
        <Eyebrow>Export capabilities</Eyebrow>
        <h2 className="mt-3 max-w-md font-serif text-3xl font-semibold text-ink">
          Operating parameters, at a glance.
        </h2>
        <dl className="mt-10 border-t border-hairline">
          {exportCapabilities.map((row) => (
            <SpecRow key={row.label} label={row.label} value={row.value} />
          ))}
        </dl>
      </Section>
    </>
  );
}

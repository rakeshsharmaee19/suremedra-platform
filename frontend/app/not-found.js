import Link from "next/link";
import { Section, Eyebrow } from "@/components/Ui";

export const metadata = {
  title: "Page not found",
  robots: { index: false, follow: false },
};

export default function NotFound() {
  return (
    <Section className="!py-28 text-center">
      <Eyebrow>404</Eyebrow>
      <h1 className="mt-3 font-serif text-3xl font-semibold text-ink">
        This page doesn&apos;t exist.
      </h1>
      <p className="mx-auto mt-3 max-w-md text-[15px] text-ink-soft">
        The page you&apos;re looking for may have moved or been renamed.
      </p>
      <Link
        href="/"
        className="mt-8 inline-block rounded-sm bg-brand px-5 py-3 text-sm text-paper transition-colors hover:bg-brand-mid"
      >
        Back to homepage
      </Link>
    </Section>
  );
}

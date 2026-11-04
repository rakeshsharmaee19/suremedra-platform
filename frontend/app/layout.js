import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { company } from "@/content/site";
import { siteUrl } from "@/lib/site";
import { EnquiryProvider } from "@/components/EnquiryProvider";

export const metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: `${company.shortName} — Pharmaceutical Exports from India`,
    template: `%s | ${company.shortName}`,
  },
  description:
    "Suremedra Enterprises exports quality-assured, GMP-certified pharmaceutical formulations to international buyers, with complete regulatory documentation and export logistics handled end to end.",
  authors: [{ name: company.legalName }],
  openGraph: {
    type: "website",
    locale: "en_IN",
    url: siteUrl,
    siteName: company.legalName,
    title: `${company.shortName} — Pharmaceutical Exports from India`,
    description:
      "GMP-certified pharmaceutical exports with complete regulatory documentation, serving international buyers across 35+ countries.",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: company.legalName }],
  },
  twitter: {
    card: "summary_large_image",
    title: `${company.shortName} — Pharmaceutical Exports from India`,
    description:
      "GMP-certified pharmaceutical exports with complete regulatory documentation, serving international buyers across 35+ countries.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#FFFFFF",
};

function OrganizationJsonLd() {
  const data = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: company.legalName,
    alternateName: company.shortName,
    url: siteUrl,
    email: company.email,
    telephone: company.phone,
    address: {
      "@type": "PostalAddress",
      streetAddress: company.address.line1,
      addressLocality: "Gurugram",
      addressRegion: "Haryana",
      addressCountry: "IN",
    },
    sameAs: [company.social.linkedin],
    description:
      "Pharmaceutical export company supplying GMP-certified formulations to international buyers.",
  };

  return (
    <script
      type="application/ld+json"
      // eslint-disable-next-line react/no-danger
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col bg-paper text-ink">
        <OrganizationJsonLd />
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-sm focus:bg-brand focus:px-4 focus:py-2 focus:text-paper"
        >
          Skip to content
        </a>
        <EnquiryProvider>
          <Header />
          <main id="main-content" className="flex-1">
            {children}
          </main>
          <Footer />
        </EnquiryProvider>
      </body>
    </html>
  );
}

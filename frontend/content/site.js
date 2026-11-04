// All copy and structured data for the site lives here.
// Phase 1 = static data. In Phase 2 this file is replaced by calls to the
// admin-managed catalogue/certification API — the page components don't change.

export const company = {
  legalName: "Suremedra Enterprises Private Limited",
  shortName: "Suremedra",
  tagline: "Pharmaceutical exports, documented and verified.",
  foundedYear: 2012,
  email: "enquiries@suremedra.com",
  phone: "+91 98XXX XXXXX",
  whatsapp: "+91 98XXX XXXXX",
  address: {
    line1: "Plot 14, Sector 6, Industrial Area",
    line2: "Gurugram, Haryana 122001, India",
  },
  social: {
    linkedin: "https://linkedin.com/company/suremedra",
  },
};

export const nav = [
  { label: "About", href: "/about" },
  { label: "Certifications", href: "/certifications" },
  { label: "Catalogue", href: "/catalogue" },
  { label: "Contact", href: "/contact" },
];

export const stats = [
  { value: "35+", label: "countries served" },
  { value: "120+", label: "formulations exported" },
  { value: String(company.foundedYear), label: "operating since" },
  { value: "6", label: "active licenses & certifications" },
];

export const capabilities = [
  {
    title: "Sourcing & manufacturing partners",
    body:
      "Formulations are sourced from WHO-GMP certified manufacturing partners across India, selected and audited against destination-market pharmacopeia standards before onboarding.",
  },
  {
    title: "Quality & regulatory compliance",
    body:
      "Every batch is released against certificate of analysis and matched to the importing country's registration requirements before it leaves our facility.",
  },
  {
    title: "Export logistics & documentation",
    body:
      "Cold-chain and ambient shipment handling, complete with legalized invoices, certificates of origin, and phytosanitary or free-sale certificates as required per shipment.",
  },
];

export const mission = {
  vision:
    "To be a dependable bridge between India's pharmaceutical manufacturing base and healthcare markets abroad — trusted for consistency of supply and clarity of documentation.",
  mission:
    "We give international buyers a single, accountable point of contact for sourcing quality-assured medicines: verified manufacturers, complete regulatory paperwork, and export logistics handled end to end.",
};

export const leadership = [
  {
    name: "Rahul Yadav",
    role: "Director",
    bio: "Leads sourcing, buyer relationships and export operations across Suremedra's active markets.",
  },
  {
    name: "[Co-founder / Director Name]",
    role: "Director, Quality & Regulatory Affairs",
    bio: "Oversees manufacturer audits, documentation and compliance with destination-market regulatory bodies.",
  },
];

export const exportCapabilities = [
  { label: "Export regions", value: "Africa, Middle East, Southeast Asia, CIS" },
  { label: "Formulation types", value: "Tablets, capsules, syrups, injectables, topicals" },
  { label: "Minimum order handling", value: "Retail-lot to full-container consolidated shipments" },
  { label: "Shipping terms", value: "FOB, CIF, CFR — as agreed per buyer" },
  { label: "Payment terms", value: "Advance / LC / DP, agreed per contract" },
  { label: "Cold-chain capability", value: "Available for temperature-sensitive formulations" },
];

// Numbered as "exhibits" deliberately — this is an enumerated document index, not decoration.
export const certifications = [
  {
    id: "01",
    title: "WHO-GMP Certificate of Manufacturing Compliance",
    issuer: "State Drug Control Authority",
    issued: "2024",
    validTill: "2027",
    description:
      "Confirms manufacturing partner facilities meet World Health Organization Good Manufacturing Practice standards.",
  },
  {
    id: "02",
    title: "Certificate of Pharmaceutical Product (COPP)",
    issuer: "Central Drugs Standard Control Organisation",
    issued: "2024",
    validTill: "2026",
    description:
      "Issued per WHO certification scheme, required by most importing-country regulators for product registration.",
  },
  {
    id: "03",
    title: "Import Export Code (IEC)",
    issuer: "Directorate General of Foreign Trade, India",
    issued: "2012",
    validTill: "Perpetual",
    description: "Statutory registration required to conduct import/export business from India.",
  },
  {
    id: "04",
    title: "Drug Export License",
    issuer: "State FDA / Drugs Controller",
    issued: "2023",
    validTill: "2028",
    description: "Authorizes the export of scheduled pharmaceutical formulations.",
  },
  {
    id: "05",
    title: "Free Sale Certificate",
    issuer: "Central Drugs Standard Control Organisation",
    issued: "2024",
    validTill: "2026",
    description: "Confirms products are freely sold and marketed within India, per shipment/product as required.",
  },
  {
    id: "06",
    title: "ISO 9001:2015 — Quality Management",
    issuer: "Accredited Certification Body",
    issued: "2023",
    validTill: "2026",
    description: "Certifies the quality management system governing sourcing, handling and export operations.",
  },
];

export const productCategories = [
  {
    name: "Antibiotics",
    description: "Broad and narrow-spectrum formulations across tablet, capsule and injectable forms.",
  },
  {
    name: "Analgesics & antipyretics",
    description: "Pain-relief and fever-reducing formulations for retail and hospital supply.",
  },
  {
    name: "Cardiac & antihypertensives",
    description: "Chronic-care formulations for cardiovascular management.",
  },
  {
    name: "Antidiabetics",
    description: "Oral and injectable formulations for diabetes management.",
  },
  {
    name: "Vitamins & nutraceuticals",
    description: "Supplement and nutraceutical lines for general and clinical use.",
  },
  {
    name: "Topical & dermatological",
    description: "Creams, ointments and topical solutions.",
  },
];

// Public URL of the website. Set NEXT_PUBLIC_SITE_URL (it is read at build time).
export const siteUrl = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

import { getAllFormulationSlugs } from "@/lib/api";
import { siteUrl } from "@/lib/site";

// Rendered on request (not at build time) so new medicines appear without a redeploy.
export const dynamic = "force-dynamic";

const staticRoutes = ["", "/about", "/certifications", "/catalogue", "/contact"];

export default async function sitemap() {
  const entries = staticRoutes.map((route) => ({
    url: `${siteUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: route === "" ? "weekly" : "monthly",
    priority: route === "" ? 1 : 0.7,
  }));

  try {
    const slugs = await getAllFormulationSlugs();
    slugs.forEach((slug) =>
      entries.push({ url: `${siteUrl}/catalogue/${slug}`, changeFrequency: "monthly", priority: 0.6 })
    );
  } catch (err) {
    // If the API is down we still serve the static pages rather than failing the sitemap.
    console.error(`[sitemap] could not load catalogue slugs: ${err.message}`);
  }
  return entries;
}

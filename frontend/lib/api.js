// Server-side helpers for the public catalogue API (used by server components only).
// Browser-side calls (the enquiry form) use relative URLs: /api/v1/public/...

const API = (process.env.API_INTERNAL_URL || "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function get(path, params = {}, revalidate = 300) {
  const url = new URL(`${API}/api/v1/public/${path}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    (Array.isArray(value) ? value : [value]).forEach((v) => url.searchParams.append(key, v));
  });
  let res;
  try {
    res = await fetch(url, { next: { revalidate } });
  } catch (err) {
    console.error(`[api] request failed: ${url} - ${err.message}`);
    throw new ApiError(0, "The catalogue service is not reachable");
  }
  if (res.status === 404) return null;
  if (!res.ok) {
    console.error(`[api] ${res.status} for ${url}`);
    throw new ApiError(res.status, `API returned ${res.status}`);
  }
  return res.json();
}

export const getFormulations = (params) => get("formulations", params, 60);
export const getFormulation = (slug) => get(`formulations/${encodeURIComponent(slug)}`, {}, 300);
export const getFilters = () => get("filters", {}, 300);

// Every public slug (for the sitemap). Pages of 100 until exhausted.
export async function getAllFormulationSlugs(limit = 5000) {
  const slugs = [];
  for (let page = 1; slugs.length < limit; page += 1) {
    const data = await get("formulations", { page, page_size: 100 }, 3600);
    if (!data) break;
    slugs.push(...data.results.map((r) => r.slug));
    if (!data.next) break;
  }
  return slugs;
}

import Link from "next/link";
import { PageHeader, Section } from "@/components/Ui";
import AddToEnquiryButton from "@/components/AddToEnquiryButton";
import { getFilters, getFormulations } from "@/lib/api";

const PAGE_SIZE = 24;

export async function generateMetadata({ searchParams }) {
  const sp = await searchParams;
  const filtered = Boolean(sp.q || sp.type || sp.composition || (sp.page && sp.page !== "1"));
  return {
    title: "Medicine Catalogue: Export Formulations by Composition",
    description:
      "Search pharmaceutical formulations by composition, strength and type (tablet, capsule, syrup, injection). Ask about availability for export.",
    alternates: { canonical: "/catalogue" },
    // Filtered and paged URLs are not indexed, so Google sees one clean catalogue page.
    robots: filtered ? { index: false, follow: true } : undefined,
  };
}

function buildHref(sp, patch) {
  const params = new URLSearchParams();
  const merged = { ...sp, ...patch };
  Object.entries(merged).forEach(([k, v]) => {
    if (!v || (k === "page" && String(v) === "1")) return;
    [].concat(v).forEach((x) => params.append(k, x));
  });
  const qs = params.toString();
  return qs ? `/catalogue?${qs}` : "/catalogue";
}

export default async function CataloguePage({ searchParams }) {
  const sp = await searchParams;
  const q = typeof sp.q === "string" ? sp.q : "";
  const type = typeof sp.type === "string" ? sp.type : "";
  const composition = typeof sp.composition === "string" ? sp.composition : "";
  const page = Math.max(1, parseInt(sp.page, 10) || 1);
  const current = { q, type, composition };

  let data = null;
  let filters = { types: [] };
  let failed = false;
  try {
    [data, filters] = await Promise.all([
      getFormulations({ q, type, composition, page }),
      getFilters(),
    ]);
  } catch {
    failed = true;
  }

  const results = data?.results ?? [];
  const totalPages = data ? Math.max(1, Math.ceil(data.count / PAGE_SIZE)) : 1;

  return (
    <>
      <PageHeader
        kicker="Export catalogue"
        title="Find formulations by composition."
        lede="Search by active ingredient, strength or type. Select what you need and ask us about availability. We reply with an invoice by email."
      />
      <Section>
        <div className="grid gap-10 lg:grid-cols-[260px_1fr]">
          <aside aria-label="Search and filters">
            <form action="/catalogue" method="get" className="grid gap-5">
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-ink">Search</span>
                <input
                  type="search" name="q" defaultValue={q} placeholder="e.g. paracetamol 500"
                  className="w-full rounded-md border border-hairline bg-paper px-4 py-2.5 text-[15px] focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20"
                />
              </label>
              <fieldset>
                <legend className="mb-2 text-sm font-medium text-ink">Medicine type</legend>
                <div className="grid gap-1.5 text-[15px]">
                  <label className="flex items-center gap-2"><input type="radio" name="type" value="" defaultChecked={!type} /> All types</label>
                  {filters.types.map((t) => (
                    <label key={t.slug} className="flex items-center gap-2">
                      <input type="radio" name="type" value={t.slug} defaultChecked={type === t.slug} />
                      {t.name} <span className="text-ink-soft">({t.count})</span>
                    </label>
                  ))}
                </div>
              </fieldset>
              {composition ? <input type="hidden" name="composition" value={composition} /> : null}
              <div className="flex items-center gap-4">
                <button type="submit" className="rounded-md bg-brand px-5 py-2.5 text-sm font-medium text-white hover:bg-brand-mid">Apply</button>
                {(q || type || composition) ? <Link href="/catalogue" className="text-sm text-ink-soft underline underline-offset-4">Clear all</Link> : null}
              </div>
            </form>
          </aside>

          <div>
            {failed ? (
              <p role="alert" className="rounded-md bg-amber-50 p-6 text-amber-900">
                The catalogue is temporarily unavailable. Please try again in a few minutes, or{" "}
                <Link href="/contact" className="underline">contact us</Link> directly.
              </p>
            ) : (
              <>
                <p className="mb-5 text-sm text-ink-soft" aria-live="polite">
                  {data.count} {data.count === 1 ? "formulation" : "formulations"}
                  {q ? <> matching &ldquo;{q}&rdquo;</> : null}
                  {composition ? (
                    <> with <Link href={buildHref(current, { composition: "" })} className="rounded bg-brand/10 px-2 py-0.5 text-brand-mid">{composition} &times;</Link></>
                  ) : null}
                </p>

                {results.length === 0 ? (
                  <p className="rounded-md border border-dashed border-hairline p-8 text-ink-soft">
                    Nothing matches your search. Try fewer words, or{" "}
                    <Link href="/contact" className="text-brand-mid underline underline-offset-4">ask us about a specific formulation</Link>.
                  </p>
                ) : (
                  <ul className="grid gap-4 sm:grid-cols-2">
                    {results.map((f) => (
                      <li key={f.id} className="flex flex-col justify-between rounded-lg border border-hairline bg-paper p-5 transition hover:border-brand/40 hover:shadow-md">
                        <div>
                          <span className="text-xs font-semibold uppercase tracking-wide text-brand-mid">{f.medicine_type.name}</span>
                          <h2 className="mt-1 font-serif text-lg font-semibold leading-snug text-ink">
                            <Link href={`/catalogue/${f.slug}`} className="hover:text-brand-mid">{f.display_name}</Link>
                          </h2>
                          <p className="mt-2 flex flex-wrap gap-1.5">
                            {f.compositions.map((c) => (
                              <Link key={c.slug} href={buildHref(current, { composition: c.slug, page: 1 })} className="rounded bg-paper-shade px-2 py-0.5 text-xs text-ink-soft hover:bg-brand/10">
                                {c.name}{c.strength ? ` ${c.strength}` : ""}
                              </Link>
                            ))}
                          </p>
                        </div>
                        <div className="mt-5"><AddToEnquiryButton slug={f.slug} name={f.display_name} /></div>
                      </li>
                    ))}
                  </ul>
                )}

                {totalPages > 1 ? (
                  <nav aria-label="Pagination" className="mt-8 flex items-center justify-between text-sm">
                    {page > 1 ? <Link rel="prev" href={buildHref(current, { page: page - 1 })} className="text-brand-mid underline underline-offset-4">&larr; Previous</Link> : <span />}
                    <span className="text-ink-soft">Page {page} of {totalPages}</span>
                    {page < totalPages ? <Link rel="next" href={buildHref(current, { page: page + 1 })} className="text-brand-mid underline underline-offset-4">Next &rarr;</Link> : <span />}
                  </nav>
                ) : null}
              </>
            )}
          </div>
        </div>
      </Section>
    </>
  );
}

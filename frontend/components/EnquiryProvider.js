"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "suremedra_enquiry_v1";
const EnquiryContext = createContext(null);

export function EnquiryProvider({ children }) {
  const [items, setItems] = useState([]);
  const [ready, setReady] = useState(false);

  // Load the saved basket after mount (avoids server/client mismatch).
  useEffect(() => {
    try {
      const saved = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "[]");
      if (Array.isArray(saved)) setItems(saved);
    } catch {
      /* ignore corrupt storage */
    }
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch {
      /* storage may be blocked; the basket then lives for this visit only */
    }
  }, [items, ready]);

  const add = useCallback((item) => {
    setItems((prev) =>
      prev.some((i) => i.slug === item.slug) ? prev : [...prev, { quantity: 1, unit: "", ...item }]
    );
  }, []);
  const remove = useCallback((slug) => setItems((prev) => prev.filter((i) => i.slug !== slug)), []);
  const update = useCallback(
    (slug, patch) => setItems((prev) => prev.map((i) => (i.slug === slug ? { ...i, ...patch } : i))),
    []
  );
  const clear = useCallback(() => setItems([]), []);

  const value = useMemo(
    () => ({ items, ready, add, remove, update, clear, has: (slug) => items.some((i) => i.slug === slug) }),
    [items, ready, add, remove, update, clear]
  );
  return <EnquiryContext.Provider value={value}>{children}</EnquiryContext.Provider>;
}

export function useEnquiry() {
  const ctx = useContext(EnquiryContext);
  if (!ctx) throw new Error("useEnquiry must be used inside <EnquiryProvider>");
  return ctx;
}

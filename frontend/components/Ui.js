"use client";

import { motion } from "framer-motion";

export function Section({ children, className = "", shaded = false }) {
  return (
    <section className={`${shaded ? "bg-paper-shade" : ""} ${className}`}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-50px" }}
        transition={{ duration: 0.7, ease: [0.21, 0.47, 0.32, 0.98] }}
        className="mx-auto max-w-6xl px-6 py-16 sm:px-8 sm:py-24"
      >
        {children}
      </motion.div>
    </section>
  );
}

export function Eyebrow({ children }) {
  return (
    <p className="text-sm font-semibold tracking-wide uppercase text-brand flex items-center gap-2">
      <span className="w-6 h-[2px] bg-brand rounded-full inline-block"></span>
      {children}
    </p>
  );
}

export function PageHeader({ kicker, title, lede }) {
  return (
    <div className="border-b border-hairline bg-paper-shade relative overflow-hidden">
      {/* Decorative gradient blob */}
      <div className="absolute top-0 right-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -right-[10%] w-[60%] h-[120%] bg-brand/5 blur-[100px] rounded-full transform rotate-12"></div>
      </div>
      
      <div className="mx-auto max-w-6xl px-6 py-16 sm:px-8 sm:py-24 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          {kicker ? <Eyebrow>{kicker}</Eyebrow> : null}
          <h1 className="mt-4 max-w-3xl font-serif text-4xl font-semibold leading-tight text-ink sm:text-6xl">
            {title}
          </h1>
          {lede ? (
            <p className="mt-6 max-w-xl text-lg sm:text-xl leading-relaxed text-ink-soft">{lede}</p>
          ) : null}
        </motion.div>
      </div>
    </div>
  );
}

export function SpecRow({ label, value }) {
  return (
    <div className="flex flex-col gap-1 border-b border-hairline py-4 sm:flex-row sm:items-baseline sm:justify-between group hover:bg-paper-shade/50 transition-colors -mx-2 px-2 rounded-md">
      <dt className="text-sm font-medium text-ink-soft group-hover:text-ink transition-colors">{label}</dt>
      <dd className="text-[15px] font-medium text-ink sm:text-right">{value}</dd>
    </div>
  );
}

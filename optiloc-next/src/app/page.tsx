import SmoothScrollHero from "@/components/ui/smooth-scroll-hero";

/* ─── Headline section — sits directly below the video ─── */
function HeroHeadline() {
  return (
    <section className="bg-[#0C0A09] px-6 py-24 md:px-14 md:py-32">
      <div className="mx-auto max-w-5xl">

        <p
          className="mb-8 font-mono text-[10px] tracking-[0.22em] text-[#0C9488] uppercase"
          style={{ fontFamily: "'Space Mono', monospace" }}
        >
          Hong Kong · Spatial Optimisation
        </p>

        <h1
          className="max-w-3xl text-5xl font-extrabold leading-[1.02] tracking-[-0.03em] text-[#F7F4EF]
                     md:text-7xl lg:text-8xl"
          style={{ fontFamily: "'Fraunces', Georgia, serif" }}
        >
          Where does your<br />
          network{" "}
          <em style={{ color: "#0C9488", fontStyle: "italic" }}>belong</em>?
        </h1>

        <p
          className="mt-8 max-w-lg text-base leading-[1.75] text-[#F7F4EF]/55 md:text-lg"
          style={{ fontFamily: "'Fraunces', Georgia, serif" }}
        >
          OptiLoc finds the optimal placement for physical facilities using
          Hong Kong's real road network and a 7.5&thinsp;M-resident demand
          model. Coverage-first. Distance-minimising.
        </p>

        <div className="mt-12 flex flex-wrap items-center gap-6">
          <a
            href="#system"
            className="inline-flex items-center gap-2 bg-[#F7F4EF] px-6 py-3.5
                       font-mono text-[11px] tracking-[0.1em] text-[#0C0A09] uppercase
                       transition-colors hover:bg-[#0C9488] hover:text-[#F7F4EF]"
            style={{ fontFamily: "'Space Mono', monospace" }}
          >
            Request a Free Analysis
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
              <path d="M2.5 7h9M8 3l4 4-4 4"/>
            </svg>
          </a>
          <a
            href="#"
            className="inline-flex items-center gap-2 border-b border-[#F7F4EF]/20 pb-0.5
                       font-mono text-[10px] tracking-[0.1em] text-[#F7F4EF]/50 uppercase
                       transition-colors hover:border-[#0C9488] hover:text-[#0C9488]"
            style={{ fontFamily: "'Space Mono', monospace" }}
          >
            Inspect the live system
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true">
              <path d="M2 6h8M6.5 2.5l3.5 3.5-3.5 3.5"/>
            </svg>
          </a>
        </div>

      </div>
    </section>
  );
}

/* ─── Stats / proof section ─── */
function ProofSection() {
  const stats = [
    { value: "~46%",   label: "Coverage improvement" },
    { value: "7.5 M",  label: "Residents modelled"  },
    { value: "18",     label: "Districts covered"   },
  ];

  return (
    <section id="system" className="bg-[#F7F4EF] px-6 py-24 md:px-14">
      <div className="mx-auto max-w-5xl">

        <p
          className="mb-6 font-mono text-[11px] tracking-[0.18em] text-[#0C9488] uppercase"
          style={{ fontFamily: "'Space Mono', monospace" }}
        >
          — 01 · A working system, not a pitch
        </p>

        <h2
          className="mb-16 max-w-2xl text-4xl font-bold leading-[1.08] tracking-[-0.025em] text-[#0C0A09]
                     md:text-5xl"
          style={{ fontFamily: "'Fraunces', Georgia, serif" }}
        >
          Coverage-first.<br />
          <em style={{ fontStyle: "italic", color: "#0C9488" }}>Distance-minimising.</em>
        </h2>

        <div className="grid grid-cols-1 divide-y divide-[#D6CFC5] border-y border-[#D6CFC5] md:grid-cols-3 md:divide-x md:divide-y-0">
          {stats.map(({ value, label }) => (
            <div key={label} className="px-0 py-10 md:px-8 md:py-12 first:md:pl-0 last:md:pr-0">
              <p
                className="mb-3 font-mono text-[10px] tracking-[0.18em] text-[#80786F] uppercase"
                style={{ fontFamily: "'Space Mono', monospace" }}
              >
                {label}
              </p>
              <p
                className="text-5xl font-extrabold tracking-[-0.04em] text-[#0C0A09] md:text-6xl"
                style={{ fontFamily: "'Fraunces', Georgia, serif" }}
              >
                {value}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-wrap items-center gap-6">
          <a
            href="#"
            className="inline-flex items-center gap-2 border-b border-[#D6CFC5] pb-0.5
                       font-mono text-[10px] tracking-[0.1em] text-[#80786F] uppercase
                       transition-colors hover:border-[#0C9488] hover:text-[#0C9488]"
            style={{ fontFamily: "'Space Mono', monospace" }}
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true">
              <rect x="1.5" y="1.5" width="9" height="9" rx="1"/><path d="M4.5 6h3M6 4.5v3"/>
            </svg>
            Live API Docs
          </a>
          <a
            href="#"
            className="inline-flex items-center gap-2 border-b border-[#D6CFC5] pb-0.5
                       font-mono text-[10px] tracking-[0.1em] text-[#80786F] uppercase
                       transition-colors hover:border-[#0C9488] hover:text-[#0C9488]"
            style={{ fontFamily: "'Space Mono', monospace" }}
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true">
              <path d="M6 1C3.24 1 1 3.24 1 6c0 2.21 1.43 4.08 3.41 4.74.25.05.34-.11.34-.24v-.82c-1.38.3-1.67-.67-1.67-.67-.23-.58-.56-.73-.56-.73-.46-.31.03-.3.03-.3.5.03.77.52.77.52.45.77 1.18.55 1.47.42.04-.33.18-.55.32-.68-1.12-.13-2.3-.56-2.3-2.49 0-.55.2-1 .52-1.35-.05-.13-.23-.64.05-1.33 0 0 .42-.13 1.38.52A4.77 4.77 0 0 1 6 3.9c.44 0 .88.06 1.3.17.96-.65 1.37-.52 1.37-.52.28.69.1 1.2.05 1.33.33.35.52.8.52 1.35 0 1.94-1.18 2.36-2.3 2.49.18.16.34.47.34.94v1.4c0 .13.09.29.35.24A5 5 0 0 0 11 6c0-2.76-2.24-5-5-5z"/>
            </svg>
            Open-source Repo
          </a>
        </div>

      </div>
    </section>
  );
}

/* ─── Page ─── */
export default function Home() {
  return (
    <main style={{ position: "relative", zIndex: 1 }}>
      <SmoothScrollHero
        videoSrc="/hero.mp4"
        scrollHeight={1800}
      />

      {/* Headline appears cleanly below the video section */}
      <HeroHeadline />

      {/* Proof / stats */}
      <ProofSection />
    </main>
  );
}

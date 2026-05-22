# OptiLoc HK — Product Roadmap

> Companion to `CONTEXT.md` (technical handoff) and `MATH.md` (math reference). This doc is the *product/business* North Star. Update at the end of each phase, or when strategy meaningfully shifts.

---

## North Star

OptiLoc becomes the math-credible facility location tool for Hong Kong logistics and infrastructure operators. The wedge is real operations-research mathematics applied to specific HK operational decisions (EV charger siting, micro-fulfillment hub placement, delivery network design), sold as either a self-serve tool, a consulting engagement, or both. Customer evidence will eventually decide which.

Until validated in HK, no other geography matters. If HK doesn't work, nothing works.

Kaito's primary goal through this build is **gaining repeatable experience pitching, presenting, and connecting with operational decision-makers at real companies**. Revenue is a downstream outcome of that experience. Sector specifics are secondary; any sector that generates 10+ substantive ops-director conversations is doing its job.

---

## Working principles

1. **HK-only through at least Session ~40.** Deep beats broad.
2. **Math foundations are non-skippable.** Road-network distance and capacitated p-median ship before any customer discovery begins. The math gates the pitching.
3. **Step-based, not date-based.** Phases have entry and exit criteria, not deadlines. Loose date markers OK.
4. **Hybrid open source.** `optiloc-core` (math library, public on GitHub for recruiter visibility and academic credibility) and `optiloc-app` (landing page, customer scenarios, eventual product surface; private).
5. **Don't ship half-baked.** When something ships publicly it must look like the work of someone who knows what they're doing.
6. **Customer discovery is execution, not preparation.** When the math and URL are ready, Kaito sends DMs the same week.
7. **Frontend choice deferred to Phase 3.** Researched and decided when needed, not pre-committed.
8. **Vertical default: HK EV charging operators.** Flexible; any HK vertical that generates ops-director conversations is acceptable.

---

## Phase 1 — GCP shipped + portfolio asset

**Entry:** Session 012 complete (current state).

**Goal:** Public Cloud Run URL serving the existing solvers via FastAPI Swagger, plus a one-page landing page with the k-sweep chart, the four-solver convergence map, the OZP-constrained k=5 map, and a "request a free audit" demo form. **Functional** ship, not a sandbox, not multi-tenant, no auth, but presentable enough to share with a real ops director without embarrassment.

**Sessions in this phase:**

- **Session 013 — k-sweep diminishing returns.** Solve OZP-constrained k-median for k ∈ {3, 5, 8, 10, 15, 20}. Plot objective vs k. This becomes the headline chart on the landing page (*"how many hubs is enough?"*). ~1 session.

- **Session 014 — Docker + FastAPI wrap.** Containerize existing solvers, expose `/solve/weber`, `/solve/kmedian`, `/solve/kmedian-ozp` endpoints. FastAPI auto-generates Swagger docs at `/docs`. ~2 sessions.

- **Session 015 — Cloud Run first deploy.** Push image to Artifact Registry, deploy to `asia-east2`, get the live URL. ACE-aligned (IAM, regions, container deployment).

- **Session 016 — Road-network distance integration.** *Math foundation #1.* Replace Euclidean distance with road-network distance using self-hosted OSRM on Cloud Run (or Google Distance Matrix API to start, cheaper if usage is low). All existing solvers re-run with road-network distance for HK. Compare results to Euclidean: by how many meters do the optima shift? Document the difference. This is the credibility-defining math upgrade. ~2-3 sessions.

- **Session 017 — Cloud Build CI/CD.** Auto-build and auto-deploy on push to `main`. ACE-aligned.

- **Session 018 — Landing page v1.** Single page with: hero (*"Mathematical facility location for Hong Kong logistics"*), the k-sweep diminishing-returns chart, the four-solver convergence map, the OZP-constrained k=5 map, a brief technical writeup, a "request a free audit" Calendly link or email form. Static HTML/CSS hosted on Cloud Run alongside the API, or on Cloud Storage + CDN. No React yet; this is a single page, not an app. ~2 sessions.

**Exit criteria:**
1. `optiloc.io` (or chosen domain) loads the landing page over HTTPS.
2. `optiloc.io/api/docs` loads Swagger; at least one endpoint runs end-to-end from a curl command.
3. Road-network distance is implemented and the new optima are documented.
4. The "request a free audit" form actually delivers messages somewhere Kaito reads.
5. Prof. Kuo follow-up email sent with Phase 1 results.

**Anti-goals:**
- No React, no Next.js, no shadcn/ui yet.
- No auth, no multi-tenancy, no Stripe.
- No second city.
- No pricing page.

**Loose date marker:** roughly mid-July if Kaito holds 1-3 sessions/day through FWD.

---

## Phase 2 — Customer discovery + math hardening

**Entry:** Phase 1 exit criteria met.

**Goal:** First substantive ops-director conversations, backed by the math foundations needed to handle real customer data. By end of Phase 2, target 1-2 real free-audit commitments from HK operators.

### Math track (blocks customer pitching)

- **Capacitated p-median.** *Math foundation #2.* Add throughput constraints to each facility. Real hubs have capacity limits; uncapacitated Lloyd gives geographically pretty but operationally wrong answers. Usually solved with MILP (Gurobi or open-source CBC) or a metaheuristic; both options to be evaluated when Phase 2 starts. ~3-4 sessions.

- **Existing-facility expansion.** Modify Lloyd to fix some centers and only optimize placement of new ones. Real customers have existing hubs; the question is almost always *"where do the next 5 go?"* not *"where do all 50 go from scratch?"* ~1-2 sessions on top of capacitated.

- **Sample scenario built.** One specific HK use case modeled with realistic dummy data: e.g., *"HK EV charging operator placing 20 new fast-charge stations across HK Island + Kowloon, capacity 8 chargers per site, existing 30 stations stay fixed."* Lives on the landing page as a downloadable PDF or interactive demo. ~2 sessions.

### Customer track (starts the moment the math track reaches "capacitated p-median works")

- **Build target list.** 30-40 HK operators across:
  - EV charging (CLP, HK Electric, Towngas, ChargedHK, EV Power, Sun Hung Kai's CDS Charging, etc.)
  - Last-mile delivery (Lalamove HK, SF Express HK, J&T HK, ZTO HK)
  - Food delivery / dark kitchens (Foodpanda HK, Deliveroo HK, KaTo Cloud Kitchens)
  - Specialty logistics (Kerry Logistics, HKTVmall last-mile, ParknShop ecommerce, Yuu ecosystem)
  - HK govt / quasi-govt referral sources (HK Productivity Council, Cyberport, HKSTP, HK Logistics Association)
  
  Find names + titles on LinkedIn: VP/Director of Operations, Head of Network Planning, COO, Head of Strategy, Site Selection / Real Estate teams. HKU IELM alumni are the warmest first hop.

- **DM cadence.** When Kaito asks, Claude provides the DM script template, tuned per persona. Send 3-5 DMs/week. Track responses in a spreadsheet.

- **Free audit offer.** *"I'll run your last 60-90 days of demand data through OptiLoc and produce a report on where your network is suboptimal. Free, takes me 2 weeks, you keep the report regardless of whether we work together further. All under mutual NDA."* Standard NDA template needed before the first audit; Claude drafts when the time comes.

- **First audit execution.** When someone says yes: 40-60 hours of work over 2 weeks. Output: PDF report + interactive Folium map + 5-slide executive deck. The deck format becomes the standard template for all future audits.

**Exit criteria:**
1. Capacitated p-median works on HK demand data.
2. Existing-facility expansion works.
3. One sample scenario published on landing page.
4. 20+ DMs sent.
5. 5+ substantive conversations had.
6. 1-2 free audit commitments secured (or, if zero, document why and adjust).

**Anti-goals:**
- No React frontend yet.
- No paid pricing discussed yet; audits are free.
- No second vertical until the first generates 3+ conversations.

---

## Phase 3 — First pilot + React frontend decision

**Entry:** Phase 2 exit criteria met (at least one free audit completed, generating concrete customer feedback).

**Goal:** Convert free audit → paid pilot. Build the React frontend with the lessons learned from real customer interaction.

### Customer track

- **First paid pilot.** Price: $5-10K USD depending on scope (see pricing table below). Deliverables: full network analysis + 1-2 follow-up consultations + executive deck. Timeline: ~6-8 weeks.
- **Case study published.** Anonymized if customer requires; named if they consent. This becomes the credibility asset for pilots #2 and #3.
- **Math additions if pilot demands them:**
  - Chance constraints (service level: *"95% of demand within 30 min"*)
  - Multi-objective formulation (minimize cost + maximize coverage)
  - Cost models (rent by polygon, labor by district, transport by mile)

### Frontend track (decision deferred to here per Kaito's preference)

- **Research and pick frontend stack.** Kaito researches current AI frontend tools (v0, Bolt, Lovable, Cursor + manual Next.js, etc.). Tradeoffs discussed in-session. Pick one. Build the React app on top of the existing FastAPI backend.
- **Build customer-facing app v1.** Auth (Firebase Auth or GCP Identity Platform), file upload (CSV demand data), scenario management (save/load/compare), result visualization (interactive map), report export (PDF). Cloud Run hosts both frontend and backend.
- **Pricing page goes live.** Two tiers, with pricing informed by what the first pilot customer actually paid. Anti-pattern to avoid: pricing pulled from thin air like the original business plan PDF.

**Exit criteria:**
1. One paid pilot completed and paid for.
2. One published case study (anonymized or named).
3. React app v1 live with at least one logged-in customer account using it.

**Anti-goals:**
- No multi-tenancy infrastructure beyond what the first 2-3 customers strictly need.
- No marketing automation (no HubSpot, no email drip).
- No multi-city expansion.

---

## Phase 4 — Productize what consulting taught

**Entry:** Phase 3 exit criteria met.

**Goal:** 3-5 paid pilots completed. Recurring patterns in customer requests crystallize into standard product features.

- **Pilot pipeline:** 2-4 more pilots run, each generating a case study.
- **Product features extracted from consulting work:** features that appear in 3+ customer projects become standard product. One-offs stay one-offs.
- **Polished landing page:** real customer logos (with permission), real metrics from real case studies, real testimonials.
- **Domain mature:** `optiloc.io` / `.ai` / `.com` decision finalized, full SEO, blog with technical posts linking back to GitHub `optiloc-core`.
- **Second city evaluated:** if HK is generating consistent revenue, evaluate Singapore as second city. Native Japanese makes Tokyo the easier fallback.

**Exit criteria:**
1. $30-80K USD annualized revenue.
2. 5+ published case studies.
3. Pipeline of 5-10 active conversations.
4. Clear answer to *"does this generate enough revenue to be worth full-time attention?"*

---

## Phase 5 — Decision gate

**Entry:** Kaito's senior-year graduation approaches.

**Goal:** Make the call.

Three legitimate outcomes, all wins:

- **(a) Full-time on OptiLoc post-grad.** Probably requires a co-founder by this point. Pre-seed raise possible if traction warrants. HK PR after graduation aligns with this path.
- **(b) Strong industry offer + keep OptiLoc as side project.** OptiLoc as the calling card that got the offer; continued evening/weekend build. Co-founder or freelancer to keep momentum.
- **(c) Top OR / data science Master's.** OptiLoc as the project that got the admission. Pause customer work; convert to research project (possibly under Prof. Kuo if collaboration solidifies).

The decision is data-driven by Phase 4 outcomes, not pre-committed here.

---

## The math stack — non-skippable foundation

| Status | Layer | What it does | Why a customer cares | Phase |
|---|---|---|---|---|
| ✅ Shipped | Weber unconstrained | Optimal single facility, Euclidean | Doesn't really; toy version | Done |
| ✅ Shipped | KKT-constrained Weber | Single facility with feasibility constraints | Doesn't directly, but proves math rigor | Done |
| ✅ Shipped | Weiszfeld iteration | Fast convergence for Weber | Enables k-median scaling | Done |
| ✅ Shipped | Uncapacitated k-median (Lloyd) | k facilities, Euclidean, no capacity | Foundational, not deployable as-is | Done |
| ✅ Shipped | OZP-constrained k-median | k facilities on commercially-zoned land only | Compliance is non-negotiable | Done |
| 🔜 Phase 1 | **Road-network distance** | Real drive times, not Euclidean | **Customer's first question: "are these realistic distances?"** | Session 016 |
| 🔜 Phase 2 | **Capacitated p-median** | Hubs have throughput limits | **Customer's second question: "can the hub actually handle that demand?"** | Phase 2 math track |
| 🔜 Phase 2 | **Existing-facility expansion** | Fix existing hubs, optimize only new ones | **Customer's actual problem: "where do my next 5 go?"** | Phase 2 math track |
| 📋 Phase 3 if needed | Chance constraints | "95% of demand within 30 min" | Service-level guarantees | Phase 3 |
| 📋 Phase 3 if needed | Multi-objective | Minimize cost + maximize coverage | Real decisions have multiple objectives | Phase 3 |
| 📋 Phase 3 if needed | Cost models | Rent + labor + transport | Optimum changes when objective is $ not km | Phase 3 |

**Rule:** rows marked 🔜 ship before the corresponding phase ends. Rows marked 📋 ship only if a paying customer demands them. Don't speculatively build math features no customer has paid for.

---

## Customer discovery playbook

### Personas to target (HK, Phase 2)
- VP / Director of Operations
- Head of Network Planning / Logistics
- COO at mid-size operators (50-500 employees)
- Head of Strategy
- Site Selection / Real Estate teams at EV charging operators

### Where to find them
- LinkedIn search by company + title
- HKU IELM alumni network (warmest first hop)
- HK Productivity Council events
- HKSTP / Cyberport events for logistics startups
- HK Logistics Association member list
- HK Trade Development Council (HKTDC) industry contact lists

### DM template
Claude drafts a personalized version per persona when Phase 2 starts. Format: short, math-credibility-led, no jargon dump, no pitch deck attached, one specific ask (20-minute call to learn how their team currently makes hub-placement decisions).

### Free audit offer scope
- Customer provides: 60-90 days of order or demand data with location stamps
- Kaito provides: PDF report + interactive Folium map + 5-slide executive deck
- Timeline: 2 weeks
- Free, under mutual NDA
- No expectation of paid follow-up; a paid pilot is the natural next step but not the price of admission

### NDA template
Claude drafts a standard mutual NDA when the first customer asks. HK-jurisdiction. Reviewed by a lawyer before signing the third one (lawyer cost ~HKD 2,000-5,000 for a one-time review).

---

## Pricing strategy (first 5 pilots)

| Pilot # | Price | Purpose |
|---|---|---|
| 1 | Free | First case study; learn what real customers care about |
| 2 | Free | Second case study; refine deliverables |
| 3 | $5-10K USD | First paid; price informed by what customer 1 said they'd pay |
| 4 | $10-15K USD | Validate pricing |
| 5 | $15-20K USD | Premium positioning if pilots 3-4 generated strong references |

After pilot 5, pricing stabilizes at $15-25K USD per engagement, or shifts to recurring SaaS pricing if product surface justifies it.

---

## Anti-roadmap (what to NOT build)

- **No multi-tenancy / billing / Stripe before Phase 4.** Premature.
- **No mobile app, ever.** Wrong form factor for the buyer persona.
- **No "AI-powered" framing.** OptiLoc is *mathematics*-powered. The math is the credibility. Don't dilute it.
- **No second city before HK validates.** Geographic discipline.
- **No second vertical before the first generates 3+ conversations.** Vertical discipline.
- **No marketing automation before there are 10+ inbound leads to automate.** Premature optimization.
- **No fundraising before Phase 4.** Investor conversations distract from customer conversations at this stage.
- **No co-founder search before Phase 3.** Solo discipline forces clarity; team forms when the work outgrows one person.
- **No conferences, no Twitter brand-building, no podcasting until Phase 4.** All distractions disguised as marketing.
- **No retail site selection pivot.** Placer.ai dominates that space in the US; HK is too small to fund a Placer-killer; not the wedge.

---

## Operational checklist (for when revenue starts)

To be addressed in Phase 3 onward, not now:
- Domain registration: `optiloc.io` vs `.ai` vs `.com` (Claude decides when asked)
- HK PIPL compliance basics for handling customer demand data
- Mutual NDA template
- Lawyer review of NDA after 2-3 signings
- Stripe HK account or alternative for HKD invoicing
- HK Business Registration (when revenue exceeds ~HKD 100K/yr)
- Basic insurance (professional indemnity) once paid pilots start
- GCP cost modeling; set billing alerts at HKD 100, 500, 1000

---

## Repo structure (planned)

**Public — `github.com/Kaito-ishiguro/optiloc-hk`** (current repo, becomes `optiloc-core`):
- All math implementations (Weber, KKT, Weiszfeld, Lloyd, OZP constraints, road-network distance, capacitated p-median)
- Data ingestion scripts (WorldPop, OZP fetch, OSRM setup)
- All Folium visualization scripts
- CONTEXT.md, JOURNAL.md, MATH.md, ROADMAP.md (this file)
- MIT licensed for academic and recruiting visibility

**Private — `optiloc-app`** (created when Phase 2 ends):
- FastAPI app, landing page HTML
- React frontend (when Phase 3 builds it)
- Customer scenario data
- Cloud Run deployment configs
- NDA templates, customer report templates

---

## Update cadence

- Update this doc at the end of each phase (Phase 1 → 2 → 3 → 4 → 5).
- Update mid-phase if strategy meaningfully shifts (e.g., customer feedback forces a vertical change).
- Companion to `CONTEXT.md` (technical state) and `MATH.md` (mathematical reference).
- Source of truth for the *business* dimension of OptiLoc.

---

*Roadmap v1 — drafted at the Session 012 → Session 013 transition, in response to Kaito's pivot from class project to actual money-making project. Step-based, not date-based. HK-only. Math foundations non-skippable. Hybrid open source. Customer discovery starts the moment Phase 1 ships.*

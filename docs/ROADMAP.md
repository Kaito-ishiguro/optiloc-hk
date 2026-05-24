# OptiLoc HK — Product & Business Roadmap

> Companion to `CONTEXT.md` (technical handoff) and `MATH.md` (math reference).
> This doc is the *product/business* North Star.
> **Last updated: Session 019 — May 23, 2026. Major revision: consolidated business plan, Phase 0 added, customer discovery overhauled, startup principles integrated.**

---

## North Star

OptiLoc becomes the math-credible facility location tool for Hong Kong logistics and infrastructure operators. The wedge is real operations-research mathematics applied to specific HK operational decisions (EV charger siting, micro-fulfillment hub placement, delivery network design), sold as a consulting engagement first, self-serve product later.

**The target that matters this year: first real money by December 2026.** Not rich. Not a unicorn. One company pays Kaito real money for real work. That is the proof of concept — for investors, for grad schools, for future customers, and for himself. Everything in this roadmap points at that target.

Until validated in HK, no other geography matters. If HK doesn't work, nothing works.

Kaito's primary goal through this build is **gaining repeatable experience pitching, presenting, and connecting with operational decision-makers at real companies**. Revenue is the proof that the work has real-world value — not just impressive, but useful enough that someone paid for it.

---

## Founding principles

1. **HK-only through at least Session ~40.** Deep beats broad.
2. **Math foundations are non-skippable.** Road-network distance and capacitated p-median ship before any paid customer work begins. The math gates the credibility.
3. **Step-based, not date-based.** Phases have entry and exit criteria, not deadlines.
4. **Outreach starts NOW, not after Phase 2.** The demo is live. Waiting for more math before talking to customers is backwards. Sell the demo first, then build more.
5. **Measure commitment, not opinions.** Don't ask "would you use this?" Ask "will you share your data for a free audit?" Actions are truth. Words are noise.
6. **Handpick the first customers.** Free audits go to the 2 highest-potential companies — growing operators with a real network problem and a decision-maker who will actually engage. Not first-come-first-served.
7. **Revenue over funding.** First $5K teaches more than $2M in investor money. Bootstrap to first 3 paying customers before any fundraising conversation.
8. **Outcome-first, always.** Don't pitch "I built a facility location optimizer." Pitch "I can show you where your network is losing money and exactly where your next hub should go."
9. **Don't ship half-baked.** When something ships publicly it must look like the work of someone who knows what they're doing.
10. **Frontend choice deferred to Phase 3.** Researched and decided when needed, not pre-committed.
11. **Vertical default: HK EV charging operators.** Flexible; any HK vertical that generates ops-director conversations is acceptable.

---

## The money timeline

| Milestone | Target date | What it proves |
|---|---|---|
| 2 calls booked | Before June 8 | Outreach works |
| Free audit #1 delivered | July 2026 | You can execute |
| Free audit #2 delivered | August 2026 | You can repeat it |
| First "I'd pay for this" | August/September 2026 | Business model works |
| First invoice sent | October/November 2026 | It's a real business |
| First invoice paid | November/December 2026 | **You made money** |

**Revenue target by December 2026: $3,000–8,000 USD.** First paid pilot. One company. That's the win for this year.

---

## Phase 0 — Pre-Internship Sprint *(ACTIVE NOW)*
**Now → June 7, 2026 (16 days)**

**This is the most important window in the plan.** No internship, no classes, maximum energy. Use it entirely on outreach — not building.

### Actions

**Day 1–2:**
- Send Prof. Kuo follow-up email (Phase 1 results + warm connection ask)
- Update LinkedIn (see LinkedIn section below) — one focused sitting, done

**Day 3–7:**
- Reach out to Cathay Pacific connection (tennis mentorship) — warm ask: *"Do you know anyone in operations or network planning at CX Cargo or HKIA who'd take a 15-minute call?"*
- Reach out to HKIA connection — same ask
- Build target list of 20 HK companies (see target list below)
- Find the right person at each: VP Operations, Head of Network Planning, COO

**Day 8–16:**
- Send 20 LinkedIn DMs using outcome-first language (see DM template below)
- Follow up on any warm intro responses

**Exit criterion:** 2–3 calls booked before June 8.

---

## Phase 1 — GCP shipped + portfolio asset ✅ COMPLETE

**Shipped:**
- Live URL: `https://optiloc-api-809774362984.asia-east2.run.app`
- Swagger at `/api/docs` ✅
- Road-network distance implemented ✅
- CI/CD auto-deploy on push to main ✅
- Landing page with charts and audit form ✅
- Formspree audit form delivering to Kaito ✅
- Prof. Kuo follow-up email: pending (Phase 0 action)

---

## Phase 2 — First audits + math hardening
**June → September 2026 (parallel with FWD internship)**

### Customer track *(starts Week 1 of internship, based on Phase 0 conversations)*

**Free audit scope (per audit):**
- Customer provides: 60–90 days of demand/order data with location stamps (CSV with coordinates or addresses)
- Kaito provides: PDF report + interactive Folium map + 5-slide executive deck
- Timeline: 2–3 weeks per audit (not 6 weeks — scope it tight)
- Free, under mutual NDA
- In every debrief call, ask the commitment question: *"Based on what you saw, would your team pay for a full network analysis? What would that need to look like?"*

**Handpick rule:** Free audits go to the 2 companies that are (a) actively growing, (b) have a real network problem visible from the outside, and (c) have a senior decision-maker engaged. Do not offer free audits broadly.

**Customer track milestones:**
- Free audit #1 delivered: July 2026
- Free audit #2 delivered: August 2026
- 1 company signals willingness to pay: August/September 2026
- 20+ DMs sent total across Phase 0 + Phase 2
- 5+ substantive conversations had

### Math track *(mornings/evenings, 1–2 sessions per week)*

- **Capacitated p-median** — add throughput constraints to each facility. Real hubs have capacity limits. ~3–4 sessions.
- **Existing-facility expansion** — fix existing hubs, optimize only new ones. Real customers ask "where do my next 5 go?" not "where do all 50 go from scratch?" ~2 sessions.
- **One sample HK EV charging scenario** — "20 new fast-charge stations across HK Island + Kowloon, capacity 8 chargers per site, 30 existing stations fixed." Published on landing page as a demo. ~2 sessions.

**Exit criteria:**
1. 2 free audits delivered
2. Capacitated p-median working on HK demand data
3. Existing-facility expansion working
4. 1 sample scenario on landing page
5. 1 company has signaled willingness to pay

---

## Phase 3 — First paid pilot
**September → December 2026**

**Price: $3,000–5,000 USD** for first paid engagement. Lower than original roadmap. First money matters more than first margin. Price goes up after the first case study exists.

**Deliverables:**
- Full network analysis PDF report
- Interactive Folium map
- 5-slide executive deck
- 1 follow-up consultation call

**Timeline:** 4–6 weeks from kick-off to delivery.

**After delivery:**
- Get a testimonial — even one sentence. That quote is worth more than the $5K for the next conversation.
- Publish case study (anonymized if required, named if they consent)
- Start second paid conversation immediately

**Exit criteria:**
1. One paid pilot completed and invoice paid
2. One case study published
3. Second paid conversation active or pipeline warm

---

## Phase 4 — Scale the consulting model
**2027 — post-graduation runway**

- Pilots 4–5: $10–20K USD each
- 5+ case studies published
- React frontend decision made and built (Phase 3 deferred this)
- Pricing stabilizes at $15–25K per engagement, or shifts to SaaS if product surface justifies it
- Singapore evaluated as second city if HK generating consistent revenue

**Revenue target by end of 2027: $30–80K USD annualized.**

---

## Phase 5 — Decision gate
**Senior year, approaching graduation**

Three legitimate outcomes, all wins:

- **(a) Full-time on OptiLoc post-grad.** Requires co-founder by this point. Pre-seed raise possible if traction warrants. HK PR path aligns.
- **(b) Strong industry offer + keep OptiLoc as side project.** OptiLoc as the calling card that got the offer.
- **(c) Top OR / data science Master's.** OptiLoc as the project that got the admission. Possibly under Prof. Kuo if collaboration solidifies.

Decision is data-driven by Phase 4 outcomes, not pre-committed here.

---

## Customer discovery playbook

### The pitch (outcome-first, always)

**Wrong:** *"I built a mathematical facility location optimizer for Hong Kong."*

**Right:** *"I can show you where your network is losing money — and exactly where your next hub should go to fix it."*

Same product. Completely different conversation. Lead with the customer's outcome, not your technical achievement.

### Warm connections first (highest priority)

Before any cold DMs, exhaust warm connections:

1. **Cathay Pacific connection (tennis mentorship)** — CX Cargo is one of Asia's largest air freight operations. Ask: *"Do you know anyone in operations or network planning at CX Cargo or HKIA who'd take a 15 minutes call from me?"*
2. **HKIA connection (tennis mentorship)** — Airport Authority HK manages cargo facility siting. Same ask.
3. **Prof. Kuo** — UG research collaboration offered. Ask if he has industry contacts at HK logistics operators.
4. **HKU IELM alumni** — Warmest cold outreach. LinkedIn search: HKU IELM alumni at target companies.

### Target company list

**Priority 1 — EV charging (fastest-growing, clear network problem)**
- ChargedHK
- EV Power HK
- CLP EV (CLP Holdings)
- HK Electric EV
- Sun Hung Kai CDS Charging
- Towngas EV

**Priority 2 — Last-mile delivery (high volume, real network pain)**
- Lalamove HK
- J&T Express HK
- SF Express HK
- ZTO HK
- HKTVmall last-mile

**Priority 3 — Food delivery / dark kitchens**
- Foodpanda HK
- Deliveroo HK
- KaTo Cloud Kitchens

**Priority 4 — Specialty logistics**
- Kerry Logistics
- ParknShop ecommerce
- Yuu ecosystem

**Warm referral sources (not direct customers, but open doors)**
- HK Productivity Council
- Cyberport
- HKSTP (Hong Kong Science and Technology Parks)
- HK Logistics Association

### Personas to target

- VP / Director of Operations
- Head of Network Planning / Logistics
- COO at mid-size operators (50–500 employees)
- Head of Strategy
- Site Selection / Real Estate teams at EV charging operators

### Where to find them

- LinkedIn search: company name + title
- HKU IELM alumni network (filter by company)
- HKSTP / Cyberport events for logistics startups
- HK Logistics Association member list

### The DM that gets replies

> Hi [Name], I'm a 2nd-year engineering student at HKU — I've built a facility location optimizer specifically for HK logistics operators, using the full HK road network and commercial zoning data. I'm offering free network audits to 2–3 operators this summer: you share 60 days of demand data, I return a full report showing where your network is losing efficiency and where your next hub should go. Free, 2 weeks, you keep the report. Worth a 15-minute call?

Rules: Short. Specific. One ask. No jargon. No pitch deck attached. If they don't reply in 5 days, one follow-up only.

### Free audit offer scope

- Customer provides: 60–90 days of order/demand data with location stamps
- Kaito provides: PDF report + interactive Folium map + 5-slide deck
- Timeline: 2–3 weeks
- Free, mutual NDA
- No expectation of paid follow-up stated upfront — but ask the commitment question at debrief

### The commitment question (ask at every debrief)

*"Based on what you saw in this report — would your team pay for a full analysis? And if so, what would it need to include to justify the spend?"*

Don't soften it. Don't apologize for asking. Their answer is the most valuable data point in the entire process.

### NDA template

Claude drafts a standard mutual NDA when the first customer asks. HK-jurisdiction. Reviewed by a lawyer before signing the third one (lawyer cost ~HKD 2,000–5,000 for one-time review).

---

## Technical FAQ — for customer conversations

Know these cold. Practice them out loud before every call.

**"How does it work?"**
"We take your historical demand data — delivery addresses, order locations, wherever your customers are — and run it through a mathematical optimization model that finds the network configuration minimizing total distance to your customers. We use real HK road network distances, not straight-line estimates, and we constrain results to commercially-zoned land so every output is actually leasable."

**"Is my data safe?"**
"We sign a mutual NDA before you share anything. Your data is used only for your analysis and deleted after delivery. Standard HK jurisdiction."

**"What do I need to give you?"**
"60–90 days of demand data with location information. Usually a CSV with coordinates or addresses. That's it."

**"How is this different from Google Maps?"**
"Google Maps tells you how to get from A to B. We tell you where A should be in the first place."

**"Who else have you done this for?"**
"I'm running my first audits with HK operators now. The model is built on real HK population data — 7.5 million residents, real road network, OZP commercial zoning constraints. I'm offering free audits specifically to generate the first case studies. That's why the timing is good for you — you get the full analysis at no cost."

**"Why should I trust a student?"**
Don't wait for this — address it proactively. *"I'm a 2nd-year IELM student at HKU, which is exactly where this math comes from. The model is open source on GitHub, the methodology is peer-reviewed operations research, and the live system is already running on Google Cloud. You're not trusting a pitch deck — you're trusting a working system you can inspect right now."*

---

## LinkedIn optimization (do this in one sitting, Day 1–2)

**Headline** (most important — shows in DM previews):
> IELM Student at HKU · Building OptiLoc HK — Mathematical Facility Location for Hong Kong Logistics · FWD Group Intern

**About section (3–4 sentences):**
> I'm a 2nd-year Industrial Engineering & Logistics Management student at HKU, building OptiLoc HK — a facility location optimizer using real Hong Kong road network and population data to help logistics operators decide where to place their hubs. The system is live on Google Cloud and open source on GitHub. I'm currently offering free network audits to 2–3 HK operators this summer. If your team makes hub placement or network expansion decisions, let's talk.

**Featured section:**
- OptiLoc HK live URL: `https://optiloc-api-809774362984.asia-east2.run.app`
- GitHub repo link

**Experience:**
- FWD Group internship (add immediately, June 2026)
- OptiLoc HK — Founder & Developer (add as current)

**Education:**
- HKU, BEng Industrial Engineering & Logistics Management, Class of 2028

---

## Pricing strategy

| Engagement | Price | Purpose |
|---|---|---|
| Free audit #1 | Free | First case study; learn what customers care about |
| Free audit #2 | Free | Second case study; refine deliverables |
| Paid pilot #1 | $3,000–5,000 USD | First money; price informed by debrief signals |
| Paid pilot #2 | $5,000–10,000 USD | Validate pricing |
| Paid pilot #3 | $10,000–15,000 USD | Premium positioning with references |

After pilot 3, pricing stabilizes at $15,000–25,000 USD per engagement, or shifts to recurring SaaS if product surface justifies it.

---

## The math stack

| Status | Layer | What it does | Why a customer cares | Phase |
|---|---|---|---|---|
| ✅ Shipped | Weber unconstrained | Optimal single facility, Euclidean | Proves math foundation | Done |
| ✅ Shipped | KKT-constrained Weber | Single facility with feasibility constraints | Proves math rigor | Done |
| ✅ Shipped | Weiszfeld iteration | Fast convergence for Weber | Enables k-median scaling | Done |
| ✅ Shipped | Uncapacitated k-median | k facilities, Euclidean | Foundational | Done |
| ✅ Shipped | OZP-constrained k-median | k facilities on commercial land only | Compliance is non-negotiable | Done |
| ✅ Shipped | Road-network distance | Real drive times, not Euclidean | Customer's first question: "are these realistic?" | Done |
| 🔜 Phase 2 | **Capacitated p-median** | Hubs have throughput limits | Customer's second question: "can it handle the demand?" | Phase 2 |
| 🔜 Phase 2 | **Existing-facility expansion** | Fix existing, optimize new only | Customer's actual problem: "where do my next 5 go?" | Phase 2 |
| 📋 Phase 3 if needed | Chance constraints | "95% of demand within 30 min" | Service-level guarantees | Phase 3 |
| 📋 Phase 3 if needed | Multi-objective | Minimize cost + maximize coverage | Real decisions have multiple objectives | Phase 3 |
| 📋 Phase 3 if needed | Cost models | Rent + labor + transport | Optimum changes when objective is $ not km | Phase 3 |

**Rule:** 🔜 rows ship before the corresponding phase ends. 📋 rows ship only if a paying customer demands them.

---

## Anti-roadmap (what NOT to build)

- **No multi-tenancy / billing / Stripe before Phase 4.** Premature.
- **No mobile app, ever.** Wrong form factor for the buyer persona.
- **No "AI-powered" framing.** OptiLoc is *mathematics*-powered. The math is the credibility.
- **No second city before HK validates.**
- **No second vertical before the first generates 3+ conversations.**
- **No marketing automation before 10+ inbound leads.**
- **No fundraising before Phase 4.**
- **No co-founder search before Phase 3.** Solo discipline forces clarity. Team forms when the work outgrows one person. If considering a co-founder, do a 3-month project together first — never commit on trust alone.
- **No conferences, podcasting, or Twitter brand-building before Phase 4.** Distractions disguised as marketing.
- **No retail site selection pivot.** Wrong wedge for HK market size.
- **No LinkedIn updates that take more than one sitting.** Done is better than perfect.

---

## Repo structure (planned)

**Public — `github.com/Kaito-ishiguro/optiloc-hk`** (current repo, becomes `optiloc-core`):
- All math implementations
- Data ingestion scripts
- All Folium visualization scripts
- CONTEXT.md, JOURNAL.md, MATH.md, ROADMAP.md
- MIT licensed for academic and recruiting visibility

**Private — `optiloc-app`** (created when Phase 2 ends):
- FastAPI app, landing page HTML
- React frontend (when Phase 3 builds it)
- Customer scenario data, Cloud Run deployment configs
- NDA templates, customer report templates

---

## Operational checklist (Phase 3 onward)

- Domain: `optiloc.io` vs `.ai` vs `.com` — decide when revenue starts
- HK PIPL compliance basics for handling customer demand data
- Mutual NDA template (Claude drafts on request)
- Lawyer review of NDA after 2–3 signings (~HKD 2,000–5,000)
- Stripe HK or alternative for HKD invoicing
- HK Business Registration when revenue exceeds ~HKD 100K/yr
- GCP billing alerts at HKD 100, 500, 1,000
- Basic professional indemnity insurance once paid pilots start

---

*Roadmap v2 — Session 019, May 23, 2026. Major revision from v1 (Session 012). Phase 0 added. Customer discovery overhauled with outcome-first framing, warm connection strategy, and commitment-based validation. Pricing revised: first paid pilot at $3,000–5,000 USD. Startup principles integrated. Money target set: first real revenue by December 2026.*
---

## Phase 1.5 Backlog — Session 021 Brainstorm Output

Session 021 was a pure brainstorm session with Opus that evaluated four Perplexity research outputs covering visualization tools, outreach/sales tooling, audit delivery infrastructure, HK market intelligence, and demand data enrichment. Output: a structured NOW/FUTURE backlog plus one new feature proposal.

### NOW list (Sessions 022-024 plus Phase 0 outreach)

**Session 022 precondition: split repo into public/private**
Create new private repo `optiloc-hk-private` for sensitive docs (CONTEXT, ROADMAP, JOURNAL, future PITCH_INTELLIGENCE, future audit deliverables, future customer data). Public repo keeps code, frontend, technical docs, MATH.md. Cost: $0 (GitHub free tier). Setup time: ~30 minutes.

**Product / code work (Sessions 022-023)**

1. **DATA.GOV.HK EV chargers ingest pipeline**. Public charger locations and details. Source: https://data.gov.hk/en-data/dataset/hk-epd-evcpateam-evc-1. Free, monthly updates. Enables the coverage-gap pitch for EV operators.
2. **DATA.GOV.HK building footprints ingest pipeline**. Upgrade from OZP-only constraint to actual leasable buildings. Source: https://data.gov.hk/en-data/dataset/hk-landsd-openmap-landsd-building. Free, monthly updates. Output sharpens from "this commercial area" to "this specific building."
3. **Baseline-aware solver mode**. New endpoint `POST /analyze_network` accepts existing facility locations, computes baseline objective, computes optimal objective, returns delta + gap map + recommended locations. Bridges from academic optimizer to audit product by quantifying value. Math reuses existing `solve_kmedian_road`. Estimated: one session of work.

**Outreach infrastructure (set up before June 8)**

4. Google Sheet CRM with 7 columns: Name, Company, Channel, Status, Last Touch, Next Action, Notes.
5. Calendly Free (or Google Calendar appointment schedules if functional).
6. Google Calendar reminders tied to Next Action column.
7. Google Meet + Gemini for call summaries (verify Gemini Pro subscription covers this feature). Fireflies Free as fallback. Manual notes as floor.
8. Manual LinkedIn research with Notion or Docs template for personalized openers. No automation.

**Documentation work (this week or next focused session)**

9. **Adopt SCQA framework** (Situation, Complication, Question, Answer) for DMs and audit report structure. Free.
10. **Draft `docs/PITCH_INTELLIGENCE.md`** with LegCo-sourced defensible stats (~105K EVs, ~9,100 chargers, ~1,500 fast chargers, 6,600+ private vs 2,550 government managed), secondary-source caveats (Fuuffy/FreightAmigo pricing data: HKD 20-50 base parcel, HKD 60-150 same-day, HKD 30-50 outlying premium), forbidden claims list, pre-written discovery call openers, audit report market-context boilerplate. 1-2 hours focused work; defer to dedicated session.

**Pitch assets (Session 022 or 023)**

11. Kepler.gl pitch visuals for landing page refresh. External tool only, no API integration. Free.
12. Commit Kepler.gl map state JSON configs to `docs/visualizations/kepler_configs/` for reproducibility.

### FUTURE list (revisit per stage, never proactively)

**Data and API integrations**
- Stadia Maps drive-time API. When paid pilot requires traffic-aware routing. Free tier 200K credits/month. ⚠️ $20/month if exceeded.
- openrouteservice self-hosted. Stadia backup. Free.
- HK Lands Department 3D building data. Post-pilot enterprise demos. Free.
- Customer-supplied demand data ingest pipeline. When audit #1 starts.

**Visualization upgrades**
- Mapbox Studio + Mapbox GL JS. Post-pilot brand polish. Free tier exists; ⚠️ paid scales with map loads.
- deck.gl / pydeck. When map endpoint outgrows Folium. Free.

**Delivery infrastructure**
- Felt Enterprise. When audit volume justifies API access. ⚠️ Enterprise tier required for API.
- Quarto for PDF reports. Audit #2+, when template is repeatable. Free.
- Pitch or Gamma for executive deck. Post-audit summary. Both have free tiers; ⚠️ paid for brand/collab.
- Self-hosted client portal with MapLibre/React. Post-pilot, when 5+ customers justify. Mostly hosting cost.

**Sales infrastructure**
- HubSpot Free. When 50+ conversations make pipeline view useful. Free; ⚠️ persistent upgrade prompts.
- Sales Navigator 1-month free trial. For one focused 2-day prospecting sprint, then cancel. ⚠️ $80/month if not canceled before trial ends.
- Fireflies paid tier. When call volume justifies. ⚠️ paid.
- Clay. When prospecting becomes a repeatable bottleneck. ⚠️ paid.

**Intelligence gaps to fill later**
- Verify HK Climate Action Plan 2050 EV targets (EPD source).
- HK total registered vehicle count for EV penetration ratio.
- EV registration growth rate year-over-year.
- HK Census commercial vehicle data by district.
- Model's first published coverage-gap stat once EV chargers ingested.

### Standing rules (applies to all future sessions)

- Alert user before any decision involving money or recurring costs (subscriptions, paid API tiers, software licenses, free trials that auto-convert). Let user decide before proceeding. Locked into Claude memory in Session 021.

### Note on Perplexity-based brainstorm process

All four Perplexity prompts from Session 021 have been run and triaged. Future brainstorm sessions should focus on: results from audit calls, specific technical research questions, or strategic pivots. Avoid generic Perplexity tool-discovery prompts without a specific gap to fill.
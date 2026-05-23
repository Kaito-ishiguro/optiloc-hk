# OptiLoc HK — Claude Project Context

> **This file is the canonical handoff. Add it to Project knowledge so every new chat in this Project starts with full context. Update it whenever a session meaningfully changes the project state.**

---

## TL;DR for new chats

OptiLoc HK is a Hong Kong facility location optimizer being built by **Kaito Ishiguro**, a 2nd-year IELM student at HKU. It applies the math from his DASE2135 course (Mathematical Optimization, Spring 2026, Dr. Y.H. Kuo) to real HK demographic data. Public GitHub repo:

**https://github.com/Kaito-ishiguro/optiloc-hk**

**Current phase:** Phase 1 complete. Sessions 001–019 done. **Session 019 shipped: ROADMAP v2 consolidated, LinkedIn rebuilt, business plan finalized.** Live URL: `https://optiloc-api-809774362984.asia-east2.run.app`. Landing page at `/`, Swagger at `/api/docs`.

**Critical discovery from Session 019:** The live API only exposes Euclidean distance solvers. Road-network solvers exist in notebooks 21-23 but are NOT wired into any API endpoint. This must be fixed before any demo or customer outreach.

**Money target: $3,000–8,000 USD by December 2026.** First paid pilot. One company.

**FWD Group internship starts June 8, 2026.** 16 days from Session 019.

**The immediate task at the start of the next chat: Session 020 — wire road-network solvers into the API and add a map output endpoint.**

---

## End-of-session protocol (MANDATORY — follow exactly)

When Kaito says **"wrap up this session"** or **"log this"**, do these four things in order:

**1. Generate the JOURNAL.md entry** following the standard template (see "Journaling workflow" below). Always output it in a single copy-pasteable code block.

**2. Tell him to paste it into JOURNAL.md and commit:**
> Paste the entry above at the bottom of your `JOURNAL.md`, save it, then commit:
> ```
> git add <files-from-this-session> JOURNAL.md
> git commit -m "Session NNN: <short description>"
> git push
> ```

**3. Always ask the chat-switch question.** After he confirms the commit, ALWAYS ask:

> *"This chat is now [N messages / has covered X sessions / has crossed a major milestone]. Do you want to switch to a new chat in the OptiLoc HK Project? If yes, I'll generate an updated CONTEXT.md with the latest project state and walk you through re-uploading it to Project knowledge."*

Recommend YES if: chat has covered 2+ full sessions, major milestone just closed, chat is over ~50 messages, or context strain is showing. Recommend NO if only one short session happened or we're mid-flow.

**4. If he says yes to switching, generate a fresh CONTEXT.md as a downloadable file** then walk him through:
1. `Move-Item $HOME\Downloads\CONTEXT.md . -Force`
2. `git add CONTEXT.md`, commit, push
3. Delete old CONTEXT.md from Project knowledge, upload new version
4. Start new chat with *"Where are we and what's next?"* or *"Session NNN: <direction>"*

---

## How to work with Kaito

### Step-by-step rhythm for terminal work

**Give ONE step at a time and wait for him to reply "done" (or paste any errors) before giving the next step.** He uses Windows and hits platform-specific errors. Single-step rhythm only.

### Teaching style

- Learns through visual and interactive examples connecting math to real applications
- Likes full hand-derivations when learning new math
- Treat failures as pedagogical — he values seeing real failure modes
- Honest engineering feedback over hype. Tell him when an idea is harder than it looks
- **The math-concept-tutor skill** at `/mnt/skills/user/math-concept-tutor/SKILL.md` is canonical for any new math concept
- Real-world interpretation matters as much as math

### Journaling workflow

```
## Session NNN — YYYY-MM-DD — [3-word title]

**What I built / learned**
- 2-4 concrete bullets

**Key insight or aha moment**
One paragraph.

**What I got stuck on**
Honest.

**Next session's first move**
One concrete specific action.

**Time spent / mood**
Optional.
```

Optional bonus: **Real-world meaning of the output** when deployment-relevant result shipped.

Journal lives in `JOURNAL.md`. Commit messages: `Session NNN: <short description>`.

**Journal entries always output in a single copy-pasteable code block.**

### Formatting preferences

- Prose by default in conversation. Bullets/tables for structured content
- Math: LaTeX inline (`$...$`) or display (`$$...$$`)
- Be concise by default. Token efficiency matters
- He uses VS Code as his editor
- **Never use em dashes in emails, DMs, or any writing intended for external audiences.** Sounds AI-generated. Use commas, colons, or rewrite the sentence instead.

### Security posture

Proportional security, not maximal. Phase 1 is a public portfolio asset. Skip items wrong for this stage.

---

## About Kaito

- 2nd-year BEng IELM, HKU, Class of 2028. Concentration: Intelligent Systems and Automation
- Languages: native English and Japanese; conversational Mandarin; basic functional Thai. **Do NOT claim Cantonese in any documents.**
- Based between Hong Kong and Kochi, Japan
- Top-30 nationally ranked tennis player (Thailand U18)
- Short-term goal: Hong Kong PR after graduation
- Long-term goals: support two future children's NYU tuition; own apartments in HK and Japan; retire to renovated grandparents' house in Kochi
- Has Claude Pro and Gemini Pro
- **FWD Group internship** starts June 8, 2026
- DASE2135 final exam done (May 11, 2026)
- **Studying for Google Cloud ACE certification.** GCP project: `ace-prep-496408`, region: `asia-east2`
- **Primary goal:** gain repeatable experience pitching and connecting with operational decision-makers. **Enjoys cold outreach** — Claude should tell him when to send DMs
- **Confident presenter and talker.** Not fully confident on technical deployment questions. Prepare him with the Technical FAQ cheat sheet before customer conversations.
- **Warm contacts via tennis mentorship program:** one person at Cathay Pacific (pilot), one at HKIA. Reach out at next tennis session (next week from Session 019).

### Model routing (OptiLoc sessions)

- **Opus:** new math, algorithm design, solver logic, deep reasoning
- **Sonnet:** debugging, feature adds, HTML/CSS, CI/CD, journaling, business strategy

State briefly at session start, e.g. "Sonnet is fine" or "Use Opus for this."

---

## The project at a glance

OptiLoc's pipeline ingests WorldPop raster → 41,288 weighted demand points (population 7,496,988) → solves Weber and k-median facility-location variants → visualizes as Folium maps or matplotlib galleries. Solvers exposed over HTTP via containerized FastAPI, live on Cloud Run. Every push to main auto-deploys via Cloud Build. Landing page live at `/`, Swagger at `/api/docs`.

**CRITICAL GAP (Session 019 discovery):** The live API only exposes Euclidean distance. Road-network solvers (notebooks 21-23) are built and working but not wired into any API endpoint. Fix this in Session 020 before any demo or customer outreach.

---

## Business plan (consolidated Session 019)

### Money target

**$3,000–8,000 USD by December 2026.** First paid pilot. One company.

### Money timeline

| Milestone | Target | What it proves |
|---|---|---|
| 2 calls booked | Before June 8 | Outreach works |
| Free audit #1 delivered | July 2026 | You can execute |
| Free audit #2 delivered | August 2026 | You can repeat it |
| First "I'd pay for this" | Aug/Sep 2026 | Business model works |
| First invoice sent | Oct/Nov 2026 | It's a real business |
| First invoice paid | Nov/Dec 2026 | **You made money** |

### Phase 0 — Pre-Internship Sprint (ACTIVE — 16 days left)

- Send Prof. Kuo follow-up email (drafted in Session 019, ready to send)
- Update LinkedIn (DONE in Session 019)
- Reach out to Cathay Pacific + HKIA warm contacts at next tennis session
- Build target list of 20 HK companies (EV charging first)
- Send 20 LinkedIn DMs using outcome-first language
- Goal: 2-3 calls booked before June 8

### Pitch language (outcome-first, always)

**Wrong:** "I built a mathematical facility location optimizer for Hong Kong."

**Right:** "I can show you where your network is losing money and exactly where your next hub should go."

### The DM that gets replies

> Hi [Name], I'm a 2nd-year engineering student at HKU — I've built a facility location optimizer specifically for HK logistics operators, using the full HK road network and commercial zoning data. I'm offering free network audits to 2-3 operators this summer: you share 60 days of demand data, I return a full report showing where your network is losing efficiency and where your next hub should go. Free, 2 weeks, you keep the report. Worth a 15-minute call?

### The commitment question (ask at every debrief)

"Based on what you saw in this report — would your team pay for a full analysis? And if so, what would it need to include to justify the spend?"

### Technical FAQ cheat sheet (for customer conversations)

**"How does it work?"**
"We take your historical demand data and run it through a mathematical optimization model that finds the network configuration minimizing total distance to your customers. We use real HK road network distances, not straight-line estimates, and we constrain results to commercially-zoned land so every output is actually leasable."

**"Is my data safe?"**
"We sign a mutual NDA before you share anything. Your data is used only for your analysis and deleted after delivery."

**"What do I need to give you?"**
"60-90 days of demand data with location information. Usually a CSV with coordinates or addresses."

**"How is this different from Google Maps?"**
"Google Maps tells you how to get from A to B. We tell you where A should be in the first place."

**"Who else have you done this for?"**
"I'm running my first audits with HK operators now. I'm offering free audits specifically to generate the first case studies."

**"Why should I trust a student?"**
"I'm a 2nd-year IELM student at HKU, which is exactly where this math comes from. The model is open source on GitHub, the methodology is peer-reviewed operations research, and the live system is already running on Google Cloud. You're not trusting a pitch deck — you're trusting a working system you can inspect right now."

### Pricing

| Engagement | Price | Purpose |
|---|---|---|
| Free audit 1 | Free | First case study |
| Free audit 2 | Free | Second case study |
| Paid pilot 1 | $3,000-5,000 USD | First money |
| Paid pilot 2 | $5,000-10,000 USD | Validate pricing |
| Paid pilot 3 | $10,000-15,000 USD | Premium positioning |

---

## Session 020 plan (next session)

**Priority 1 — Wire road-network solvers into API**
- Add `POST /solve_weber_road` endpoint using notebook 21-22 logic
- Add `POST /solve_kmedian_road` endpoint using notebook 23 logic
- Both return coordinates using road-network distance, not Euclidean

**Priority 2 — Add map output endpoint**
- New endpoint that returns an interactive Folium map HTML
- Customer inputs k, gets back a map with hub locations, catchment areas, road distances
- This is what the demo video will record

**Priority 3 — Retake visuals (after map endpoint works)**
- Use f4map.com (free, 3D HK with buildings + traffic) for background screenshots
- Use city-roads (anvaka.github.io/city-roads) for HK road network SVG
- Clean screenshots for LinkedIn service page, landing page, audit report template

**Priority 4 — Demo video (Session 021)**
- 90-second Loom recording of live product
- Edit in Canva (free)
- Upload to LinkedIn service page and landing page

---

## LinkedIn (updated Session 019 — DONE)

**Headline:** Industrial Engineering and Logistics Management Year 2 at HKU | Built OptiLoc HK: Live Facility Location Optimizer on Google Cloud | FWD Group Intern

**About:** Updated with OptiLoc as main project, free audit offer, live URL

**Experience order:**
1. OptiLoc HK — Founder and Developer (April 2026 - Present)
2. FWD Group Intern (add June 8)
3. HKU IELM Industrial Engineering Student
4. NTT Com Asia
5. Prosper Foods
6. Lohakij
7. Nikkei Research
8. Tennis Team Leader (last or remove)

**Services page:** Published. "Providing services" enabled. "Open to work" set to Recruiters only.

**Remaining:** Remove old Student Athlete entry (duplicate of Tennis Team Leader).

---

## Useful visual tools (identified Session 019)

For demo visuals and landing page — use these in Session 020-021:

- **f4map.com** (free) — Interactive 3D HK map with buildings and traffic. Best for screenshots.
- **city-roads (anvaka.github.io/city-roads)** (free) — Renders HK road network as clean SVG. Use on landing page.
- **Cityweft (app.cityweft.com)** (freemium) — 3D city model with export options.
- **topoexport.com** (freemium) — Clean 2D/3D vector map export. Good for audit report backgrounds.
- **Figma** (freemium) — UI mockups and presentation design.
- **Napkin AI (napkin.ai)** (freemium) — Text to diagrams. Good for methodology explainers.

Kaito will continue suggesting tools. Accept if useful for OptiLoc demo/product/customer work. Reject everything else (fitness, crafting, games, pure aesthetic design).

---

## Codebase reference — file by file

### Frontend (Session 018)

#### `frontend/index.html`
Single-page landing. Dark navy aesthetic, Syne + DM Sans fonts, teal accent. Sections: nav, hero (animated live-API badge), stats bar (41,288 / 7.5M / 59.1% / 5,852m), 3-chart showcase (GitHub raw image URLs), how-it-works pipeline, math writeup, Formspree audit form. Formspree endpoint: `https://formspree.io/f/xdajdarn`. Images: `08_ksweep_diminishing_returns.png`, `four_solvers_wide.png`, `kmedian_ozp_map_wide.png` — all served from `raw.githubusercontent.com`.

**Visual debt:** Screenshots on landing page are notebook outputs, not presentation quality. Fix in Session 021 after map endpoint is built.

### CI/CD layer (Session 017)

#### `cloudbuild.yaml`
3-step pipeline: docker build → push to Artifact Registry → gcloud run deploy. Flags: `--max-instances=3`, `--port=8000`, `--allow-unauthenticated`, region `asia-east2`. Image tagged with `$COMMIT_SHA`.

#### Cloud Build trigger `deploy-on-push`
Region: asia-east2. Event: push to `^main$`. Ignored files: `README.md,JOURNAL.md,CONTEXT.md,docs/**`. Config: `cloudbuild.yaml`. SA: `cloudbuild-deployer@ace-prep-496408.iam.gserviceaccount.com`.

### API + container layer (Sessions 014-015, updated 018)

#### `api/main.py`
FastAPI app. `docs_url="/api/docs"`, `redoc_url="/api/redoc"`. Endpoints: `GET /` (landing page), `GET /healthz`, `POST /solve_weber`, `POST /solve_kmedian_ozp`. **BOTH use Euclidean distance — road-network not yet wired in.**

#### `api/solvers.py`
Loads files 08 and 16 via importlib. Caches graph + demand data at startup. File 16 geopandas import is lazy.

#### `api/config.py`
`MAX_K=25`, `MAX_RESTARTS=20`. Rate limit: `5/minute`. Timeouts: Weber 30s, k-median 180s.

### Notebooks (01–23)

- **01** — WorldPop ingest → `demand_points.csv` (41,288 points)
- **02** — HK population heatmap
- **03** — Unconstrained Weber. Optimum: Sham Shui Po (114.17071, 22.33729)
- **03_multi** — 4 starting points, backtracking line search
- **04** — 8 convergence trails visualization
- **05** — KKT-constrained Weber. Optimum: (114.17323, 22.34038)
- **06** — Constrained map visualization
- **07** — Hessian condition number. κ: 1.24–3.25
- **08** — Weiszfeld + 4-solver comparison. **Imported by API.**
- **09** — Four-solver convergence map
- **10** — ArcGIS OZP fetch. 11,963 polygons
- **11** — Filter to 590 C+CDA, union → 499-piece MultiPolygon (10.30 km²)
- **12** — Weber constrained to OZP commercial. Optimum: (114.16944, 22.33321)
- **13** — OZP-constrained map
- **14** — k-median (k=5, 10 restarts). Best obj 274,830 = 59.1% reduction
- **15** — k=5 k-median map with Voronoi
- **16** — OZP-constrained k-median. Best obj 277,595. **Imported by API.**
- **17** — OZP k-median map
- **18** — k-sweep k∈{3,5,8,10,15,20}. Elbow at k≈8-10
- **19** — Diminishing-returns chart
- **20** — 2×3 hub-location gallery
- **21** — Road network prep. HK driving network (18,820 nodes, 35,848 edges). **NOT in API yet.**
- **22** — Road-network Weber. Optimum: (22.32462, 114.18873), 2.33 km SE of Euclidean. **NOT in API yet.**
- **23** — Road k-median (k=5). Best: 5,852 m/resident, 54.4% reduction. **NOT in API yet.**

---

## Tech stack

- **Language:** Python 3.14
- **Env:** `.venv/`, activate via `.venv\Scripts\Activate.ps1`
- **Numerical:** NumPy, SciPy (BFGS, SLSQP)
- **Geographic:** rasterio, osmnx 2.1.0, shapely, GeoPandas, pyogrio, pyproj, scikit-learn 1.8.0
- **Visualization:** Folium, matplotlib
- **API:** FastAPI 0.136.1 + Uvicorn 0.47.0 + Pydantic 2.13.4 + slowapi 0.1.9
- **Frontend:** Static HTML/CSS/JS. Syne + DM Sans (Google Fonts). Formspree for form handling.
- **Container:** Docker Desktop 4.67.0, `python:3.14-slim`, linux/amd64
- **Cloud:** GCP `ace-prep-496408`, `asia-east2`. Artifact Registry `optiloc`. Cloud Run `optiloc-api`. URL: `https://optiloc-api-809774362984.asia-east2.run.app`
- **CI/CD:** Cloud Build trigger `deploy-on-push`, SA `cloudbuild-deployer`
- **VCS:** Git, GitHub `github.com/Kaito-ishiguro/optiloc-hk`

---

## Environment specifics (Windows quirks)

- Smart App Control disabled (Session 002)
- `mkdir -p` doesn't work → use `New-Item -ItemType Directory -Force`
- Always use `python -m pip install ...`
- `Move-Item` with `-Force` if destination exists
- `&&` invalid in PowerShell → use `;`
- Multi-line string edits → use Python helper script
- Activate venv first: `cd "C:\Users\Kaito Ishiguro\Documents\optiloc-hk"` then `.venv\Scripts\Activate.ps1`
- Use `Invoke-RestMethod` not `curl`
- Docker Desktop must be running for docker commands
- LF→CRLF warnings from Git are harmless
- VS Code is his editor — he creates files there rather than via PowerShell when possible

---

## Where we are right now

**Session 019 complete. Phase 1 is complete. Business plan consolidated.**

**Done:**
- Landing page live at `https://optiloc-api-809774362984.asia-east2.run.app`
- Swagger at `/api/docs`
- Formspree audit form live
- Road-network solvers built (notebooks 21-23) but NOT in API
- CI/CD auto-deploy on push to main
- ROADMAP v2 committed
- LinkedIn fully rebuilt
- Prof. Kuo follow-up email drafted (ready to send)
- Business plan: money target set, Phase 0 outreach plan defined

**Critical gap:** API serves only Euclidean distance. Road-network not exposed.

**Next up:**
1. Commit CONTEXT.md update (this file)
2. Session 020: wire road-network solvers into API + map output endpoint
3. Session 021: retake visuals + record demo video
4. Phase 0 outreach: send Prof. Kuo email, warm contacts at tennis, 20 LinkedIn DMs before June 8

---

## Session history (compressed)

- **001** — Project genesis. Weber facility location scoped.
- **002** — WorldPop ingestion. 41k demand points.
- **003** — GD + Newton + BFGS solvers. Optimum: Sham Shui Po.
- **004** — Multi-start visualization. Backtracking line search.
- **005** — KKT-constrained SLSQP. Constrained optimum: Beacon Hill.
- **006** — README + Phase 1 shipped. LinkedIn post.
- **007** — Condition number analysis. κ: 1.24–3.25.
- **Email from Prof. Kuo** — UG research collaboration offered.
- **008+009** — Weiszfeld + four-solver comparison. 10⁻⁹ degree convergence.
- **010** — OZP commercial zoning. 590 C+CDA, 499-piece MultiPolygon.
- **010b** — SLSQP buffer-smoothness fix.
- **011** — k-median + Voronoi. k=5. 59.1% reduction.
- **012** — OZP-constrained k-median. +1.0% penalty. MATH.md extracted.
- **Inter-session 2026-05-22** — Strategic pivot. ROADMAP.md v1 shipped.
- **013** — k-sweep k∈{3,5,8,10,15,20}. Elbow k≈8-10.
- **014** — FastAPI + Docker. Local validation.
- **015** — Cloud Run deploy. Live API.
- **016** — Road-network solvers (notebooks 21-23). Road Weber: 2.33 km shift. Road k-median: 5,852 m/resident.
- **017** — Cloud Build CI/CD. Auto-deploy on push to main.
- **018** — Landing page v1. Phase 1 complete.
- **019** — Business plan consolidated. ROADMAP v2. LinkedIn rebuilt. Critical gap found: road-network not in API. Demo video plan scoped.

---

## Files in Git (after Session 019)

README.md, JOURNAL.md, CONTEXT.md, docs/MATH.md, **docs/ROADMAP.md (v2)**, requirements.txt, .gitignore, LICENSE, cloudbuild.yaml, notebooks/01-23, docs/maps/*.png (13 screenshots), data/raw/.gitkeep, data/processed/.gitkeep, **data/processed/demand_points.csv**, **data/processed/ozp_commercial_union.geojson**, api/__init__.py, api/config.py, api/models.py, api/solvers.py, api/main.py, api/requirements.txt, .dockerignore, Dockerfile, **frontend/index.html**.

## Files NOT in Git

- `data/raw/hkg_ppp_2020_UNadj_constrained.tif`
- `data/processed/ozp_all_zones.geojson` (~120 MB)
- `data/processed/hk_road_network.graphml`
- `data/processed/demand_points_road.csv`
- `data/processed/demand_nodes_aggregated.csv`
- `docs/maps/*.html`
- `.venv/`

---

## Triggers and protocols

- **"wrap up this session"** / **"log this"** → journal entry in code block + chat-switch question
- **"let's start session NNN"** → proceed directly into work
- **"don't include this in the file but tell me..."** → thorough technical debrief outside journal
- **Terminal commands** → ONE step at a time
- **New math concept** → math-concept-tutor skill
- **Math grounding** → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md
- **Business grounding** → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/ROADMAP.md
- **Security question** → proportional security, not maximal
- **CONTEXT.md update** → always generate as downloadable file
- **Tool suggestions from Kaito** → accept if useful for OptiLoc demo/product/customer work; reject fitness, crafting, games, pure aesthetic design

---

*Last updated: end of Session 019 (May 24, 2026). Business plan consolidated. LinkedIn rebuilt. Critical API gap found. Session 020 starts with wiring road-network solvers into API endpoints.*

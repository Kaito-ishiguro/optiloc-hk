# OptiLoc HK — Claude Project Context

> **This file is the canonical handoff. Add it to Project knowledge so every new chat in this Project starts with full context. Update it whenever a session meaningfully changes the project state.**

---

## TL;DR for new chats

OptiLoc HK is a Hong Kong facility location optimizer being built by **Kaito Ishiguro**, a 2nd-year IELM student at HKU. It applies the math from his DASE2135 course (Mathematical Optimization, Spring 2026, Dr. Y.H. Kuo) to real HK demographic data. Public GitHub repo:

**https://github.com/Kaito-ishiguro/optiloc-hk**

**Current phase:** Phase 1 active. Sessions 001–016 complete (solver pipeline, OZP zoning, k-median network, Dockerized FastAPI, Cloud Run deploy, road-network distance integration). **Session 015 shipped: container is live on Cloud Run at `https://optiloc-api-809774362984.asia-east2.run.app/docs`. Session 016 shipped: road-network Weber and k-median solvers (files 21–23), file-16 lazy-load refactor.** Next: Session 017 Cloud Build CI/CD → Session 018 landing page v1. The canonical product/business plan is **`docs/ROADMAP.md`** (commit `57b630d`). Companion to CONTEXT.md (technical handoff) and MATH.md (mathematical reference). The DASE2135 final exam was on May 11, 2026 (in the past). Prof. Kuo has emailed back acknowledging the project and offering UG research collaboration. **FWD Group internship starts June 8, 2026.** Kaito plans to maintain ~1-3 sessions/day through the internship. Kaito is studying for the **Google Cloud Associate Cloud Engineer (ACE) certification** and has ~HKD 2,000 (~USD 255) in free GCP trial credit (project `ace-prep-496408`).

**The immediate pending task at the start of this new chat: Session 017.**

Per `docs/ROADMAP.md` Phase 1, Session 017 = **Cloud Build CI/CD** — connect the GitHub repo to Cloud Build so every push to main auto-builds and deploys a new Cloud Run revision. Session 018 follows: landing page v1.

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

Use judgment on whether to recommend switching. Recommend YES if:
- The chat has covered 2+ full sessions
- A major milestone just closed (phase complete, new artifact shipped, exam break starting)
- The chat is over ~50 messages long
- Claude has started showing signs of context strain (repeating itself, forgetting earlier details)

Recommend NO (or "your call") if:
- Only one short session has happened
- We're mid-flow on something that benefits from immediate context

**4. If he says yes to switching, generate a fresh CONTEXT.md** with these updates:
- Bump the "Current phase" line to reflect the new state
- Add the latest session(s) to the "Session history (compressed)" section at the bottom
- Add any new files to the "Codebase reference — file by file" section
- Update the "Where we are right now" section to reflect the new pause point
- Update the "Last updated" line at the bottom

Then walk him through the upload process using the standard step-by-step rhythm:
1. Download the updated CONTEXT.md
2. Move it into the repo (overwriting the old one): `Move-Item $HOME\Downloads\CONTEXT.md . -Force`
3. Commit: `git add CONTEXT.md`, `git commit -m "Update CONTEXT.md after Session NNN"`, `git push`
4. Re-upload to Claude Project knowledge: open the OptiLoc HK Project → delete the old CONTEXT.md from Project knowledge → upload the new version
5. Start new chat in the Project with prompt: *"Where are we and what's next?"* (or with the session number directly: *"Session NNN: <direction>"* — the latter is more token-efficient).

**Always generate CONTEXT.md as a downloadable file** so Kaito can move it into the repo directly without copy-pasting.

---

## How to work with Kaito

These are non-negotiable working agreements built up across all prior sessions. Honor them in every new chat.

### Step-by-step rhythm for terminal work

When code or PowerShell commands are involved, **give ONE step at a time and wait for him to reply "done" (or paste any errors) before giving the next step**. He explicitly asked for this rhythm because he hits Windows-specific errors and prefers small atomic steps over big chunks of instructions.

Counter-example to avoid: don't write a long "here's everything you need to do" message with 8 numbered terminal commands. Single-step rhythm only.

### Teaching style

- He learns through **visual and interactive examples connecting math to real applications**.
- He likes **full hand-derivations** (chain rule step by step) when learning new math.
- When something fails (gradient descent overshoot, singular Hessian, Newton hitting max_iter from tolerance mismatch, SLSQP hitting maxiter on a non-smooth constraint, Lloyd hitting max-iters on assignment oscillation), **treat the failure as pedagogical**. He values seeing real failure modes more than getting clean answers on the first try.
- He likes **honest engineering feedback over hype**. Tell him when an idea is harder than it looks. Tell him when his instincts are sharp (they often are). Tell him when your prior (the AI's) was wrong — Session 012 surfaced one such case (conditional-invocation runtime savings prediction was wrong); the inter-session strategic pivot surfaced another (the original B2B SaaS plan PDF he uploaded was generic AI-template work with several real errors, and Claude told him so directly); Session 014 surfaced a third (Claude's first cut of `api/requirements.txt` missed that file 16 imports geopandas at module level, and the lean dep list had to be widened).
- **The math-concept-tutor skill** at `/mnt/skills/user/math-concept-tutor/SKILL.md` is the canonical format for any new math concept he asks about. It mandates: real-world hook → visual diagram → concept explanation → vocabulary → connection. Use it.
- **Real-world interpretation matters as much as math.** When shipping a new result, briefly translate it into deployment terms (avg km per resident, cost penalty in human units, what business use cases this maps to). The math is the value; the interpretation is what makes it sellable.

### Journaling workflow

The journal entry template:

```
## Session NNN — YYYY-MM-DD — [3-word title]

**What I built / learned**
- 2-4 concrete bullets

**Key insight or aha moment**
One paragraph. The conceptual thing that clicked.

**What I got stuck on**
Honest. Includes both bugs and conceptual confusions.

**Next session's first move**
One concrete specific action.

**Time spent / mood**
Optional but valuable.
```

Optional bonus section: **Real-world meaning of the output** — used when the session shipped a deployment-relevant result. For strategy/inter-session entries, "Session NNN" can be replaced with "Inter-session" (precedent: the May 22, 2026 strategic-pivot entry).

Journal lives in `JOURNAL.md` in the repo root. Source of truth for everything. Notion is just a scratchpad. Each commit message follows the pattern `Session NNN: <short description>` (or `Inter-session: <description>` for non-coding milestones). Combined commits (e.g. `Sessions 010b + 011: ...`) are fine when sessions are tightly coupled, matching the 008+009 precedent.

**Journal entries are always output in a single copy-pasteable code block.**

### After-session debrief

He routinely asks **"don't include this in the file but tell me what we used, how you did it, what tool you used, so I can explain this as if I wasn't just copy-pasting from you."** When he asks this, give a thorough technical explanation outside the journal — tech stack, code architecture, design decisions, the "why this and not that" reasoning, and what specifically came from his own thinking vs scaffolded by Claude.

### Formatting preferences

- Avoid heavy bullets in conversational replies. Use prose by default.
- For structured content (project pitches, tables of options, step-by-step instructions), bullets and tables are fine.
- Math should use LaTeX inline (`$...$`) or display (`$$...$$`).
- He has Claude Pro and Gemini Pro subscriptions and is comfortable with technical detail.
- **Be concise by default.** Going long is a tool, not a default. Reserve depth for when he asks for it or when the conceptual ground genuinely needs it.
- **Claude credit is the practical limiter.** Kaito's credits run out fast. Token efficiency matters: don't restate context, don't pad responses, don't ask questions that could be answered from CONTEXT.md or ROADMAP.md.

### Security posture

When Kaito brings security questions or AI-generated security checklists, **the goal is proportional security, not maximal security**. Session 014 surfaced this clearly: a generic security checklist had us about to disable `/docs` in production, add API auth, and lock CORS to specific origins — all wrong for a Phase 1 portfolio asset whose entire purpose is to be a publicly-pokeable DM artifact. The right move was to keep the cheap-and-essential items (Pydantic input limits, rate limit, solver timeouts, sanitized errors, non-root user, read-only FS, `.dockerignore` allow-list) and skip the items wrong for this stage (auth, hidden docs, restrictive CORS, background queue, environment-loaded data when the data is public). Phase 2-3 will tighten as we add real customer data and money changes hands.

---

## About Kaito (load this into every new chat)

- 2nd-year BEng Industrial Engineering and Logistics Management (IELM), HKU, Class of 2028
- Concentration: Intelligent Systems and Automation
- Languages: native English and Japanese; conversational Mandarin; basic functional Thai. **Do NOT claim Cantonese in any documents.**
- Based between Hong Kong and Kochi, Japan
- Top-30 nationally ranked tennis player (Thailand U18)
- Short-term goal: Hong Kong PR after graduation
- Long-term goals: support two future children's NYU tuition; own apartments in HK and Japan; eventually retire to renovated grandparents' house in Kochi
- Has Claude Pro and Gemini Pro
- **FWD Group internship** starts June 8, 2026. Kaito plans to maintain ~1-3 sessions/day through the internship; FWD will not significantly slow OptiLoc velocity.
- DASE2135 final exam done (May 11, 2026)
- **Currently studying for the Google Cloud Associate Cloud Engineer (ACE) certification** — wants to connect every concept back to OptiLoc. GCP project: `ace-prep-496408`, region: `asia-east2`. Has ~HKD 2,000 (~USD 255) in free GCP trial credit available.
- **Primary goal through the OptiLoc build (per inter-session 2026-05-22):** gain repeatable experience pitching, presenting, and connecting with operational decision-makers at real companies. Revenue is a downstream outcome of that experience. Sector specifics are secondary. **He enjoys cold outreach and customer conversations** — this is an asset, not a chore. Claude should tell him when to send DMs; he's willing to do them anytime.

---

## The project at a glance

OptiLoc's pipeline ingests the WorldPop population raster → derives 41,288 weighted demand points (total population 7,496,988) → solves variants of the Weber facility-location problem (unconstrained, OSM-Kowloon-polygon-constrained, OZP-commercial-constrained, road-network-distance) → and k-median network variants (unconstrained, OZP-constrained, road-network-distance, plus a full k-sweep over k ∈ {3, 5, 8, 10, 15, 20}) → visualizing each as an interactive Folium map or a static matplotlib gallery. **As of Session 014, the solvers are exposed over HTTP via a containerized FastAPI app. As of Session 015, the container is live on Cloud Run at `https://optiloc-api-809774362984.asia-east2.run.app`. As of Session 016, road-network distance solvers are implemented in notebooks 21–23.** All numbered scripts live in `notebooks/` (files 01–23). Math reference lives in `docs/MATH.md`. Product/business plan lives in `docs/ROADMAP.md`.

---

## Codebase reference — file by file

### API + container layer (Session 014)

#### `api/__init__.py`
Marks `api/` as a Python package and exposes `__version__ = "0.1.0"`.

#### `api/config.py`
Centralizes all paths, security limits, and solver defaults. DoS-prevention ceilings: `MAX_K=25`, `MAX_RESTARTS=20`. Rate limit: `5/minute`. Timeouts: Weber 30s, k-median 180s.

#### `api/models.py`
Pydantic v2 request/response schemas with bounded inputs.

#### `api/solvers.py`
Loads files 08 and 16 via importlib. Caches graph + demand data at startup. **File 16's geopandas import is now lazy (inside `main()`) so the API import no longer triggers geopandas loading at startup.**

#### `api/main.py`
FastAPI app. Endpoints: `GET /healthz`, `POST /solve_weber`, `POST /solve_kmedian_ozp`, `GET /docs`, `GET /redoc`. CORS open, slowapi rate limiter, asyncio timeouts, sanitized 500s.

#### `api/requirements.txt`
`fastapi==0.136.1`, `uvicorn[standard]==0.47.0`, `slowapi==0.1.9`, `numpy==2.4.4`, `scipy==1.17.1`, `pandas==3.0.2`, `shapely==2.1.2`, `geopandas==1.1.3`, `pyogrio==0.12.1`, `pyproj==3.7.2`.

#### `Dockerfile`
Single-stage build off `python:3.14-slim`. Non-root `appuser`, `HEALTHCHECK`, exposes 8000.

#### `.dockerignore`
Allow-list pattern. Build context 3.69 MB.

### `notebooks/01_ingest_worldpop.py`
Converts WorldPop GeoTIFF → `demand_points.csv`. ~41,288 demand points, total weight ~7.5M.

### `notebooks/02_render_demand_points.py`
HK population heatmap. Output: `docs/maps/01_first_map.html`.

### `notebooks/03_solve_weber.py`
Unconstrained Weber. GD + Newton + BFGS. Optimum at lon=114.17071, lat=22.33729 (Sham Shui Po / Shek Kip Mei).

### `notebooks/03_solve_weber_multi.py`
Same math, 4 starting points. Newton uses backtracking line search.

### `notebooks/04_visualize_convergence.py`
8 convergence trails + 4 starts + gold optimum star. Output: `docs/maps/02_convergence_map.html`.

### `notebooks/05_solve_constrained.py`
KKT-constrained Weber (OSM Kowloon polygon + MTR proximity + 5 competitor exclusion). SLSQP. Constrained optimum at (114.17323, 22.34038).

### `notebooks/06_visualize_constrained.py`
Output: `docs/maps/03_constrained_map.html`.

### `notebooks/07_condition_number.py`
Hessian conditioning across HK. κ ranges 1.24–3.25.

### `notebooks/08_solve_weber_weiszfeld.py`
Weiszfeld + 4-solver comparison. All converge to same optimum to 10⁻⁹ degrees. **Imported by `api/solvers.py`.**

### `notebooks/09_visualize_four_solvers.py`
Four-solver convergence map. Output: `docs/maps/04_four_solvers_map.html`.

### `notebooks/10_fetch_ozp.py`
Paginated fetch of 11,963 HK OZP polygons from ArcGIS REST.

### `notebooks/11_filter_and_union_ozp.py`
Filter to 590 C+CDA features, union into 499-piece MultiPolygon (10.30 km²).

### `notebooks/12_solve_constrained_ozp.py`
Weber constrained to OZP commercial union. SLSQP Exit mode 0 in 16 iters. Optimum: (114.16944, 22.33321).

### `notebooks/13_visualize_ozp_constrained.py`
Output: `docs/maps/05_ozp_constrained_map.html`.

### `notebooks/14_solve_kmedian.py`
k-median (k=5, 10 restarts). Best obj 274,830 = 59.1% reduction. ≥4 local minima.

### `notebooks/15_visualize_kmedian.py`
k=5 k-median map with Voronoi. Output: `docs/maps/06_kmedian_map.html`.

### `notebooks/16_solve_kmedian_ozp.py`
OZP-constrained k-median. Best obj 277,595 = +1.0% penalty. 9 local minima. **geopandas import is now lazy (inside `main()`) — API import no longer triggers geopandas loading.** **Imported by `api/solvers.py`.**

### `notebooks/17_visualize_kmedian_ozp.py`
Output: `docs/maps/07_kmedian_ozp_map.html`.

### `notebooks/18_ksweep_ozp.py`
k-sweep over k ∈ {3, 5, 8, 10, 15, 20}. Elbow at k ≈ 8–10.

### `notebooks/19_visualize_ksweep.py`
Two-panel diminishing-returns chart. Output: `docs/maps/08_ksweep_diminishing_returns.png`.

### `notebooks/20_visualize_ksweep_maps.py`
2×3 hub-location gallery. Output: `docs/maps/09_ksweep_hub_locations.png`.

### `notebooks/21_road_network_prep.py` *(Session 016)*
Downloads HK driving network via osmnx (18,820 nodes, 35,848 edges). Snaps 41,288 demand points to nearest road nodes → 12,513 unique nodes. Saves `demand_points_road.csv` and `demand_nodes_aggregated.csv`. Caches graph as `hk_road_network.graphml`.

### `notebooks/22_solve_weber_road.py` *(Session 016)*
Discrete road-network Weber. Multi-start local search on the graph (Dijkstra from candidate node + neighbours, move to best, repeat). 3 seeds. Road optimum: (22.32462, 114.18873) — 2.33 km southeast of Euclidean optimum (Sham Shui Po → To Kwa Wan / Hung Hom). Avg road distance per resident: 12,831 m. Runtime 12.8s. Key finding: discrete road Weber has multiple local optima unlike continuous Euclidean Weber.

### `notebooks/23_solve_kmedian_road.py` *(Session 016)*
Road-network k-median (k=5, 3 restarts). Lloyd with Dijkstra assignment + centroid-snap location update. Best obj 43.9B m → **5,852 m/resident**, 54.4% reduction from road Weber. 3 restarts found objectives of 54.2B / 49.4B / 43.9B m (24% gap — strong non-convexity). F4 (Kwun Tong/Kowloon Bay) dominates at 42.5% of population. Runtime 17.4s.

---

## The math, frozen for reference

Math reference lives in **`docs/MATH.md`**. `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md when needed.

## The product/business plan

Lives in **`docs/ROADMAP.md`** (commit `57b630d`). `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/ROADMAP.md when needed.

---

## Tech stack

- **Language:** Python 3.14
- **Environment:** `venv` at `.venv/`, activated via `.venv\Scripts\Activate.ps1`
- **Package install:** `python -m pip install -r requirements.txt`
- **Numerical:** NumPy, SciPy (BFGS, SLSQP)
- **Geographic:** rasterio, osmnx 2.1.0, shapely, GeoPandas, pyogrio, pyproj, scikit-learn 1.8.0 (osmnx nearest_nodes dependency)
- **Visualization:** Folium, matplotlib
- **Tabular:** pandas
- **Module reuse:** `importlib.util.spec_from_file_location`
- **HTTP API:** FastAPI 0.136.1 + Uvicorn 0.47.0 + Pydantic 2.13.4 + slowapi 0.1.9
- **Containerization:** Docker Desktop 4.67.0 (Engine 29.3.1), `python:3.14-slim`, linux/amd64
- **Cloud:** GCP project `ace-prep-496408`, region `asia-east2`. Artifact Registry repo `optiloc`. Cloud Run service `optiloc-api`. Live URL: `https://optiloc-api-809774362984.asia-east2.run.app`
- **Version control:** Git, public GitHub at `github.com/Kaito-ishiguro/optiloc-hk`

**Planned for ROADMAP Phase 1 (Sessions 017–018):**
- Session 017: Cloud Build CI/CD from GitHub
- Session 018: landing page v1

---

## Environment specifics (Windows quirks)

- **Smart App Control was disabled** in Session 002.
- **PowerShell `mkdir -p` doesn't work.** Use `New-Item -ItemType Directory -Force`.
- **`pip` direct calls can be blocked.** Always use `python -m pip install ...`
- **`Move-Item` with `-Force`** needed if destination exists.
- **`&&` is not valid in PowerShell.** Use `;` to chain commands.
- **Multi-line string replacement in PowerShell is unreliable.** Backtick-n in single-quoted strings is literal, not a newline. Use a Python helper script for any multi-line file edits.
- **Activate venv first** in every new PowerShell session: `cd "C:\Users\Kaito Ishiguro\Documents\optiloc-hk"` then `.venv\Scripts\Activate.ps1`.
- **`Invoke-RestMethod`** for HTTP endpoints, NOT `curl`.
- **Docker Desktop** must be running before `docker build` / `docker run`.
- **Git on Windows** complains about LF→CRLF line endings. Harmless; ignore.
- **Snipping Tool** (`Win+Shift+S`) for screenshots, paste into Paint, save as PNG into `docs/maps/`.

---

## Where we are right now

**Session 016 is shipped.** Road-network distance integration complete:

- `notebooks/21_road_network_prep.py` — HK road network downloaded, demand points snapped
- `notebooks/22_solve_weber_road.py` — road Weber, 2.33 km shift from Euclidean optimum
- `notebooks/23_solve_kmedian_road.py` — road k-median k=5, 5,852 m/resident (54.4% reduction)
- `notebooks/16_solve_kmedian_ozp.py` — geopandas import moved inside `main()` (lazy-load)
- `scikit-learn==1.8.0` added to `requirements.txt`

**Road-network key results:**
- Road Weber optimum: (22.32462, 114.18873), avg 12,831 m/resident
- Road k-median (k=5) best: 5,852 m/resident, 54.4% reduction
- Discrete road problem has stronger non-convexity than Euclidean (24% obj gap across 3 restarts)

**Next up: Session 017 — Cloud Build CI/CD.** Connect GitHub repo to Cloud Build so every push to main auto-builds and deploys a new Cloud Run revision.

---

## Session history (compressed)

- **Session 001** — Project genesis. Scoped the project, picked Weber facility location.
- **Session 002** — WorldPop ingestion pipeline. SAC fix, data pipeline, 41k demand points.
- **Session 003** — Hand-rolled solvers. GD + Newton + BFGS. Optimum at Sham Shui Po.
- **Session 004** — Multi-start visualization. Backtracking line search after singular Hessian.
- **Session 005** — KKT-constrained optimization. SLSQP. Constrained optimum at Beacon Hill.
- **Session 006** — README + Phase 1 shipped. LinkedIn post.
- **Session 007** — Condition number analysis. κ ranges 1.24–3.25.
- **Email from Prof. Kuo** — Acknowledged project, offered UG research collaboration.
- **Sessions 008+009** — Weiszfeld + four-solver comparison. All converge to 10⁻⁹ degrees.
- **Session 010** — ArcGIS / OZP commercial zoning. 590 C+CDA features, 499-piece MultiPolygon.
- **Session 010b** — SLSQP buffer-smoothness fix. Exit mode 0 in 16 iters.
- **Session 011** — k-median network + Voronoi. Lloyd + Weiszfeld, k=5. 59.1% reduction.
- **Session 012** — Constrained k-median. +1.0% OZP penalty. 9 local minima. MATH.md extracted.
- **Inter-session 2026-05-22** — Strategic pivot. ROADMAP.md shipped. Primary goal: pitching experience.
- **Session 013** — k-sweep k∈{3,5,8,10,15,20}. Elbow at k≈8–10.
- **Session 014** — FastAPI + Docker. API package, Dockerfile, security hardening. Local validation.
- **Session 015** — Cloud Run deploy. Live at `https://optiloc-api-809774362984.asia-east2.run.app`.
- **Session 016** — Road-network distance integration. Files 21–23. Road Weber: 2.33 km shift. Road k-median: 5,852 m/resident (54.4% reduction). File-16 lazy-load refactor. scikit-learn added.

---

## Triggers and protocols

- **"wrap up this session"** or **"log this"** → generate journal entry in a single copy-pasteable code block, THEN ask the chat-switch question.
- **"let's start session NNN"** → assume Kaito has read this context file and proceed directly into the work.
- **"don't include this in the file but tell me..."** → give thorough technical explanation outside the journal.
- **Terminal commands** → ONE step at a time, wait for "done" or error.
- **New math concept** → use the math-concept-tutor skill at `/mnt/skills/user/math-concept-tutor/SKILL.md`.
- **Empirical findings that contradict textbook predictions** → treat as the more interesting result.
- **Real-world deployment-relevant result shipped** → translate math finding into deployment terms. Add "Real-world meaning of the output" to journal entry.
- **Math grounding needed mid-session** → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md
- **Business/product grounding needed mid-session** → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/ROADMAP.md
- **Security checklist or security question** → goal is proportional security, not maximal. Cut items wrong for the current phase.
- **Context.md update requested** → always generate as a downloadable file, not inline text.

---

## Files NOT in Git but referenced

- `data/raw/hkg_ppp_2020_UNadj_constrained.tif` — WorldPop GeoTIFF
- `data/processed/*.csv` — generated outputs (gitignored, regenerable)
- `data/processed/ozp_all_zones.geojson` — ~120 MB (gitignored)
- `data/processed/ozp_commercial_union.geojson` — ~1.27 MB (baked into Docker image)
- `data/processed/demand_points.csv` — ~1 MB (baked into Docker image)
- `data/processed/hk_road_network.graphml` — cached osmnx graph (gitignored)
- `data/processed/demand_points_road.csv` — snapped demand points (gitignored)
- `data/processed/demand_nodes_aggregated.csv` — 12,513 unique nodes (gitignored)
- `docs/maps/*.html` — generated maps (gitignored)
- `.venv/` — Python virtual environment (gitignored)
- Docker image `optiloc-hk:dev` — local; pushed to Artifact Registry as `v0.1.0`

Files IN Git: README.md, JOURNAL.md, CONTEXT.md, docs/MATH.md, docs/ROADMAP.md, requirements.txt, .gitignore, LICENSE, all `notebooks/*.py` (01–23), thirteen committed screenshots in `docs/maps/*.png`, data/raw/.gitkeep, data/processed/.gitkeep, `api/__init__.py`, `api/config.py`, `api/models.py`, `api/solvers.py`, `api/main.py`, `api/requirements.txt`, `.dockerignore`, `Dockerfile`.

---

*Last updated: end of Session 016 (May 23, 2026). Road-network distance integration shipped. Session 017 (Cloud Build CI/CD) is next per ROADMAP Phase 1. Update this file at the end of every session that meaningfully changes project state.*

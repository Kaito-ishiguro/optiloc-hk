# OptiLoc HK — Claude Project Context

> **This file is the canonical handoff. Add it to Project knowledge so every new chat in this Project starts with full context. Update it whenever a session meaningfully changes the project state.**

---

## TL;DR for new chats

OptiLoc HK is a Hong Kong facility location optimizer being built by **Kaito Ishiguro**, a 2nd-year IELM student at HKU. It applies the math from his DASE2135 course (Mathematical Optimization, Spring 2026, Dr. Y.H. Kuo) to real HK demographic data. Public GitHub repo:

**https://github.com/Kaito-ishiguro/optiloc-hk**

**Current phase:** Phase 1 active. Sessions 001–014 complete (solver pipeline, OZP zoning, k-median network, Dockerized FastAPI). **Session 015 shipped: container is live on Cloud Run at `https://optiloc-api-809774362984.asia-east2.run.app/docs` — publicly accessible on the open internet.** Next: Session 016 road-network distance integration (math foundation #1, blocking before first paid pilot) → Session 017 Cloud Build CI/CD → Session 018 landing page v1. The canonical product/business plan is **`docs/ROADMAP.md`** (commit `57b630d`). Companion to CONTEXT.md (technical handoff) and MATH.md (mathematical reference). The DASE2135 final exam was on May 11, 2026 (in the past). Prof. Kuo has emailed back acknowledging the project and offering UG research collaboration. **FWD Group internship starts June 8, 2026.** Kaito plans to maintain ~1-3 sessions/day through the internship. Kaito is studying for the **Google Cloud Associate Cloud Engineer (ACE) certification** and has ~HKD 2,000 (~USD 255) in free GCP trial credit (project `ace-prep-496408`).

**The immediate pending task at the start of this new chat: Session 016.**

Per `docs/ROADMAP.md` Phase 1, Session 016 = **road-network distance integration** — swap straight-line Euclidean distance for real road-network distances in the Weber and k-median solvers. This is math foundation #1 per ROADMAP and the blocking item before the first paid pilot conversation. Also the right session to do the file-16 geopandas lazy-load refactor (deferred from Session 014) since both touch the same surface area. Options: self-hosted OSRM on Cloud Run, or Google Distance Matrix API. Decision to be made at session start based on cost/complexity tradeoff.

Sessions 017-018 follow per ROADMAP Phase 1: Cloud Build CI/CD (017) → landing page v1 (018).

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

OptiLoc's pipeline ingests the WorldPop population raster → derives 41,288 weighted demand points (total population 7,496,988) → solves variants of the Weber facility-location problem (unconstrained, OSM-Kowloon-polygon-constrained, OZP-commercial-constrained) → and k-median network variants (unconstrained, OZP-constrained, plus a full k-sweep over k ∈ {3, 5, 8, 10, 15, 20}) → visualizing each as an interactive Folium map or a static matplotlib gallery. **As of Session 014, the solvers are exposed over HTTP via a containerized FastAPI app (`api/` directory, `Dockerfile`). As of Session 015, the container is live on Cloud Run at `https://optiloc-api-809774362984.asia-east2.run.app`.** All numbered scripts live in `notebooks/` (files 01–20); each is described in the codebase reference below. Math reference (objectives, gradients, KKT, Weiszfeld, Lloyd) lives in `docs/MATH.md`. Product/business plan lives in `docs/ROADMAP.md`. Claude can `web_fetch` either when needed mid-session.

---

## Codebase reference — file by file

Every file in `notebooks/`, plus the API + container layer added in Session 014, and what each does. Use this as ground truth.

### API + container layer (Session 014)

#### `api/__init__.py`

Marks `api/` as a Python package and exposes `__version__ = "0.1.0"`. Imported by `api/main.py` for the FastAPI `version=` field.

#### `api/config.py`

Centralizes all paths, security limits, and solver defaults for the API. Includes:
- Path resolution via `Path(__file__).resolve().parent.parent` (works both locally and inside the container).
- DoS-prevention ceilings: `MAX_K=25`, `MAX_RESTARTS=20`.
- `RATE_LIMIT_SOLVE = "5/minute"` (per-IP, applied to `/solve_*`).
- Wall-clock timeouts: `WEBER_TIMEOUT_S=30`, `KMEDIAN_TIMEOUT_S=180`.
- Solver defaults matching Session 012/013: `DEFAULT_K=5`, `DEFAULT_RESTARTS=10`, `BUFFER_DEG=1e-6`, `RNG_SEED=42`.

#### `api/models.py`

Pydantic v2 request/response schemas. Bounded inputs (`k`, `n_restarts` with `Field(ge=, le=)`) prevent pathological-value DoS. `WeberRequest` is empty for Session 014 (no caller-supplied params yet). Response models include nested `Facility` and `RestartSummary` so the response is self-documenting in Swagger.

#### `api/solvers.py`

Loads `notebooks/08_solve_weber_weiszfeld.py` and `notebooks/16_solve_kmedian_ozp.py` as modules via `importlib.util.spec_from_file_location`. Caches the loaded modules + demand points CSV + buffered OZP geometry at FastAPI startup via `initialize_solvers()`. Thin wrappers `solve_weber()` and `solve_kmedian_ozp(k, n_restarts)` are what the endpoints call.

**Gotcha caught in Session 014:** file 16 imports `geopandas as gpd` at module level. When the API imports file 16 via importlib, that top-level import fires, so the container needs `geopandas + pyogrio + pyproj` in its requirements file. Deferred refactor (lazy-load geopandas inside `main()`) noted for Session 016.

#### `api/main.py`

The FastAPI app. Exposes:
- `GET /healthz` — liveness probe
- `POST /solve_weber` — Weiszfeld on baked-in HK demand
- `POST /solve_kmedian_ozp` — k-median + OZP commercial constraint, with caller-tunable `k` and `n_restarts`
- `GET /docs` — Swagger UI (public — this IS the DM artifact in Phase 1)
- `GET /redoc` — ReDoc (also public)

Security layer: slowapi rate limiter, `asyncio.wait_for` solver timeouts, global exception handler with sanitized 500 + request_id. CORS open via `allow_origins=["*"]` (deliberate Phase 1 choice).

#### `api/requirements.txt`

Lean runtime dep list: `fastapi==0.136.1`, `uvicorn[standard]==0.47.0`, `slowapi==0.1.9`, `numpy==2.4.4`, `scipy==1.17.1`, `pandas==3.0.2`, `shapely==2.1.2`, `geopandas==1.1.3`, `pyogrio==0.12.1`, `pyproj==3.7.2`.

#### `Dockerfile`

Single-stage build off `python:3.14-slim`. Non-root `appuser`, `HEALTHCHECK` via urllib.request every 30s, exposes 8000, `CMD` uses `sh -c` so Cloud Run's `${PORT}` env var expands at runtime.

#### `.dockerignore`

Allow-list pattern. Build context 3.69 MB. Excludes the 120 MB `ozp_all_zones.geojson` cache and all dev-only files.

### `notebooks/01_ingest_worldpop.py`

Converts WorldPop GeoTIFF raster into `data/processed/demand_points.csv` with columns `(lat, lon, weight)`. ~41,288 demand points, total weight ~7.5M.

### `notebooks/02_render_demand_points.py`

HK population heatmap. Output: `docs/maps/01_first_map.html`.

### `notebooks/03_solve_weber.py`

Unconstrained Weber problem. Three solvers (GD, Newton, BFGS) from single start. All converge to lon=114.17071, lat=22.33729 (Sham Shui Po / Shek Kip Mei area).

### `notebooks/03_solve_weber_multi.py`

Same math, 4 starting points. Newton uses backtracking line search (added after singular-Hessian failure from Tung Chung start).

### `notebooks/04_visualize_convergence.py`

Session 004 hero map — 8 convergence trails + 4 starts + gold optimum star. Output: `docs/maps/02_convergence_map.html`.

### `notebooks/05_solve_constrained.py`

KKT-constrained Weber (OSM Kowloon polygon + MTR proximity + 5 competitor exclusion). SLSQP with signed-distance constraints. Constrained optimum at (114.17323, 22.34038) — Beacon Hill / Tai Wo Ping area.

### `notebooks/06_visualize_constrained.py`

Output: `docs/maps/03_constrained_map.html` + two screenshots.

### `notebooks/07_condition_number.py`

Hessian conditioning across HK. κ ranges 1.24–3.25 — Weber uniformly well-conditioned. Non-quadratic spatial variation in curvature is the real reason GD is slow, not high κ.

### `notebooks/08_solve_weber_weiszfeld.py`

Weiszfeld + 4-solver comparison. All converge to same optimum to 10⁻⁹ degrees. Weiszfeld: 23 iters, ~7.6ms. Newton: 4 iters, ~7.2ms. BFGS: 7 iters, ~5.5ms. GD: 255 iters, ~55ms. **Imported by `api/solvers.py`.**

### `notebooks/09_visualize_four_solvers.py`

Four-solver convergence map. Output: `docs/maps/04_four_solvers_map.html` + two screenshots.

### `notebooks/10_fetch_ozp.py`

Paginated fetch of 11,963 HK OZP polygons from ArcGIS REST. Output: `data/processed/ozp_all_zones.geojson` (~120 MB, gitignored).

### `notebooks/11_filter_and_union_ozp.py`

Filter to 590 C+CDA features, union into 499-piece MultiPolygon (10.30 km², 0.9% of HK land area). Output: `data/processed/ozp_commercial_union.geojson` (~1.27 MB, baked into Docker image).

### `notebooks/12_solve_constrained_ozp.py`

Weber constrained to OZP commercial union. Buffer-smoothness fix (`.buffer(1e-6)`). SLSQP Exit mode 0 in 16 iterations. Optimum: (114.16944, 22.33321) — Shek Kip Mei, ~474 m southwest of unconstrained.

### `notebooks/13_visualize_ozp_constrained.py`

OZP-constrained comparison map with 499 C+CDA polygons overlay. Output: `docs/maps/05_ozp_constrained_map.html` + two screenshots.

### `notebooks/14_solve_kmedian.py`

k-median (k=5, 10 restarts). Lloyd + Weiszfeld. Best obj 274,830 = 59.1% reduction from single-facility. ≥4 distinct local minima — empirical non-convexity proof. Runtime ~5.74s.

### `notebooks/15_visualize_kmedian.py`

k=5 k-median map with Voronoi service areas. Output: `docs/maps/06_kmedian_map.html` + two screenshots.

### `notebooks/16_solve_kmedian_ozp.py`

OZP-constrained k-median. Conditional Weiszfeld → SLSQP fallback (SLSQP fired ~100% of time empirically). Best obj 277,595 = +1.0% penalty over unconstrained. 9 distinct local minima. Runtime ~107s. **Imported by `api/solvers.py`.**

### `notebooks/17_visualize_kmedian_ozp.py`

OZP-constrained k=5 map with commercial-zone overlay + Voronoi cells. Output: `docs/maps/07_kmedian_ozp_map.html` + two screenshots.

### `notebooks/18_ksweep_ozp.py`

k-sweep over k ∈ {3, 5, 8, 10, 15, 20}, 10 restarts each. Total runtime 6.3 min. Elbow at k ≈ 8–10. Convergence rate drops at k=20 (5/10).

### `notebooks/19_visualize_ksweep.py`

Two-panel diminishing-returns chart. Output: `docs/maps/08_ksweep_diminishing_returns.png`.

### `notebooks/20_visualize_ksweep_maps.py`

2×3 hub-location gallery at each k. Output: `docs/maps/09_ksweep_hub_locations.png`.

---

## The math, frozen for reference

Math reference (objectives, gradients, Hessian, Weiszfeld, KKT, k-median, Lloyd, constrained k-median) is in **`docs/MATH.md`**. When math grounding is needed mid-session, `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md.

## The product/business plan

Product and business roadmap is in **`docs/ROADMAP.md`** (shipped at commit `57b630d`, May 22, 2026). Canonical 5-phase plan. When business/product context is needed mid-session, `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/ROADMAP.md.

---

## Tech stack

- **Language:** Python 3.14
- **Environment:** `venv` at `.venv/`, activated via `.venv\Scripts\Activate.ps1` on Windows
- **Package install:** `python -m pip install -r requirements.txt` (NOT `pip install` — Smart App Control blocks unsigned pip.exe)
- **Numerical:** NumPy, SciPy (BFGS, SLSQP)
- **Geographic:** rasterio, osmnx, shapely, GeoPandas, `requests`
- **Visualization:** Folium (interactive HTML maps), matplotlib (static PNGs)
- **Tabular:** pandas
- **Module reuse:** `importlib.util.spec_from_file_location` for loading numbered scripts
- **HTTP API:** FastAPI 0.136.1 + Uvicorn 0.47.0 + Pydantic 2.13.4 + slowapi 0.1.9
- **Containerization:** Docker Desktop 4.67.0 (Engine 29.3.1) on Windows with WSL2, `python:3.14-slim` base, linux/amd64
- **Cloud:** GCP project `ace-prep-496408`, region `asia-east2`. Artifact Registry repo `optiloc`. Cloud Run service `optiloc-api`. Live URL: `https://optiloc-api-809774362984.asia-east2.run.app`
- **Version control:** Git, public GitHub repo at `github.com/Kaito-ishiguro/optiloc-hk`

**Planned for ROADMAP Phase 1 (Sessions 016–018):**
- Session 016: road-network distance (OSRM self-hosted on Cloud Run or Google Distance Matrix API) + file-16 geopandas lazy-load refactor
- Session 017: Cloud Build CI/CD from GitHub
- Session 018: landing page v1

---

## Environment specifics (Windows quirks)

Kaito is on Windows 11 with PowerShell.

- **Smart App Control was disabled** in Session 002 to allow pandas/rasterio C extensions to load.
- **PowerShell `mkdir -p` doesn't work.** Use comma-separated args or `New-Item -ItemType Directory -Force`.
- **`pip` direct calls can be blocked by SAC.** Always use `python -m pip install ...`
- **`Move-Item` with `-Force`** is needed if the destination file exists.
- **Git on Windows complains about LF→CRLF line endings.** Harmless; ignore.
- **`osmnx` creates a `cache/` folder** in the repo root. Gitignored.
- **Activate venv first** in every new PowerShell session: `cd "C:\Users\Kaito Ishiguro\Documents\optiloc-hk"` then `.venv\Scripts\Activate.ps1`.
- **Snipping Tool** (`Win+Shift+S`) for screenshots, paste into Paint, save as PNG into `docs/maps/`.
- **For PowerShell one-liner Python with `requests`:** double quotes on the outside, single quotes inside. Don't use multi-line `-c` strings.
- **PowerShell here-strings** (`@' ... '@`) require the closing `'@` at column 0. Single-quoted here-strings don't interpolate `$VARS` — safe for Dockerfile and Python content.
- **`Invoke-RestMethod`** for hitting HTTP endpoints from PowerShell, NOT `curl`.
- **Docker Desktop on Windows** runs Linux containers via WSL2. Daemon must be running before `docker build` / `docker run`.

---

## Where we are right now (the immediate state)

**Session 015 is shipped.** The OptiLoc API is live on Cloud Run:

- **URL:** `https://optiloc-api-809774362984.asia-east2.run.app`
- **Swagger:** `https://optiloc-api-809774362984.asia-east2.run.app/docs` — confirmed rendering in a real browser from the open internet
- **Image:** `asia-east2-docker.pkg.dev/ace-prep-496408/optiloc/optiloc-hk:v0.1.0` in Artifact Registry
- **Config:** `--allow-unauthenticated`, 1Gi memory, 1 CPU, concurrency=10, max-instances=3, region `asia-east2`

This is the Phase 1 DM artifact. Anyone Kaito cold-messages can hit the URL right now without installing anything.

**Next up: Session 016 — road-network distance integration.** Decision to make at session start: self-hosted OSRM on Cloud Run vs Google Distance Matrix API. Also: file-16 geopandas lazy-load refactor (deferred from Session 014 — `import geopandas as gpd` at module level in file 16 forces the Docker image to carry geopandas even though the API's `lloyd_one_restart` function doesn't use it; moving the import inside `main()` would allow a leaner dep list in a future image rebuild).

---

## Session history (compressed)

- **Session 001 — Project genesis.** Scoped the project, picked Weber facility location, decided on logistics pivot for Phase 3.
- **Session 002 — WorldPop ingestion pipeline.** Set up Python env (with SAC fix), built the data pipeline, rendered 41k demand points.
- **Session 003 — Hand-rolled solvers.** Derived gradient + Hessian by hand. GD + Newton + BFGS. Optimum at Sham Shui Po / Shek Kip Mei area.
- **Session 004 — Multi-start visualization.** 4 starting points × 2 methods. Added backtracking line search to Newton after singular-Hessian failure.
- **Session 005 — KKT-constrained optimization.** Hand-derived Lagrangian + 4 KKT conditions. Signed-distance constraints. Constrained optimum on OSM "Kowloon" polygon boundary, Beacon Hill / Tai Wo Ping area.
- **Session 006 — README + Phase 1 shipped.** Polished README, screenshots, LinkedIn post draft.
- **Session 007 / Integration #1 — Condition number analysis.** κ ranges 1.24–3.25 across HK; Weber uniformly well-conditioned. Non-quadratic spatial variation in curvature is the real reason GD is slow.
- **Email from Prof. Kuo (between sessions).** Acknowledged the project, suggested ArcGIS and Weiszfeld, offered UG research collaboration.
- **Session 008+009 — Weiszfeld + four-solver visualization.** 4-solver comparison; all converge to same optimum to 10⁻⁹ degrees. Weiszfeld ties Newton on wall-clock despite linear vs quadratic rate.
- **Email reply to Prof. Kuo sent.** Four-solver results + commitment to ArcGIS/OZP integration.
- **Session 010 — ArcGIS / OZP commercial zoning integration.** Fetched 11,963 OZP polygons, filtered to 590 C+CDA features, unioned into 499-piece MultiPolygon (10.30 km²). Constrained Weber optimum at Shek Kip Mei.
- **Session 010b — SLSQP buffer-smoothness fix.** `.buffer(1e-6)`. SLSQP Exit mode 0 in 16 iterations.
- **Session 011 — k-median network + Voronoi visualization.** Lloyd + Weiszfeld at k=5, 10 restarts. Best obj 274,830 = 59.1% reduction. ≥4 distinct local minima.
- **Session 012 — Constrained k-median shipped.** Best obj 277,595 = +1.0% penalty. 9 distinct local minima. SLSQP fired ~100% of time. Phase 1c+ shipped. Math reference extracted to `docs/MATH.md`.
- **Inter-session — 2026-05-22 — Strategic pivot & roadmap.** Rebuilt business plan as realistic 5-phase roadmap. Shipped `docs/ROADMAP.md`. Primary goal clarified: gain repeatable pitching/presenting experience with operational decision-makers.
- **Session 013 — 2026-05-22 — k-sweep diminishing returns + hub-location maps.** Files 18–20 shipped. k-sweep over k ∈ {3,5,8,10,15,20}. Elbow at k ≈ 8–10. Spatial finding: marginal hubs at high k cluster in urban density, not underserved areas.
- **Session 014 — 2026-05-23 — FastAPI + Docker ship.** Eight new files: `api/` package + `Dockerfile` + `.dockerignore`. Solvers exposed over HTTP. Security hardening. Image built, validated locally. `optiloc-hk:dev` reproduced all notebook results exactly inside the container.
- **Session 015 — 2026-05-23 — Cloud Run ship.** Enabled Artifact Registry + Cloud Run APIs on `ace-prep-496408`. Created `optiloc` repo in `asia-east2`. Tagged + pushed `v0.1.0`. Deployed to Cloud Run. Swagger confirmed live at `https://optiloc-api-809774362984.asia-east2.run.app/docs`. Phase 1 DM artifact exists.

---

## Triggers and protocols

- **"wrap up this session"** or **"log this"** → generate journal entry in a single copy-pasteable code block, THEN ask the chat-switch question.
- **"let's start session NNN"** → assume Kaito has read this context file and proceed directly into the work.
- **"don't include this in the file but tell me..."** → give thorough technical explanation outside the journal.
- **Terminal commands** → ONE step at a time, wait for "done" or error.
- **New math concept** → use the math-concept-tutor skill at `/mnt/skills/user/math-concept-tutor/SKILL.md`.
- **Empirical findings that contradict textbook predictions** → treat as the more interesting result.
- **Optimizer non-convergence or surprising results** → don't smooth them over; visualize, diagnose, and document the failure mode.
- **Real-world deployment-relevant result shipped** → translate math finding into deployment terms. Add "Real-world meaning of the output" to journal entry.
- **Math grounding needed mid-session** → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md
- **Business/product grounding needed mid-session** → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/ROADMAP.md
- **Kaito ready to do customer outreach** → draft personalized DM script for the persona. He's willing to send DMs anytime.
- **Security checklist or security question** → goal is proportional security, not maximal. Cut items wrong for the current phase.

---

## Files NOT in Git but referenced

- `data/raw/hkg_ppp_2020_UNadj_constrained.tif` — WorldPop GeoTIFF
- `data/processed/*.csv` — all generated outputs (gitignored, regenerable)
- `data/processed/ozp_all_zones.geojson` — ~120 MB cached ArcGIS response (gitignored)
- `data/processed/ozp_commercial_union.geojson` — ~1.27 MB (gitignored locally; **baked into Docker image**)
- `data/processed/demand_points.csv` — ~1 MB (gitignored locally; **baked into Docker image**)
- `docs/maps/*.html` — generated maps (gitignored, regenerable)
- `cache/*.json` — osmnx cache (gitignored)
- `.venv/` — Python virtual environment (gitignored)
- Docker image `optiloc-hk:dev` — in Docker Desktop locally; pushed to Artifact Registry as `v0.1.0`

Files IN Git: README.md, JOURNAL.md, CONTEXT.md, docs/MATH.md, docs/ROADMAP.md, requirements.txt, .gitignore, LICENSE, all `notebooks/*.py` (01–20), thirteen committed screenshots in `docs/maps/*.png`, data/raw/.gitkeep, data/processed/.gitkeep, `api/__init__.py`, `api/config.py`, `api/models.py`, `api/solvers.py`, `api/main.py`, `api/requirements.txt`, `.dockerignore`, `Dockerfile`.

---

*Last updated: end of Session 015 (May 23, 2026). Cloud Run deploy shipped. API live at `https://optiloc-api-809774362984.asia-east2.run.app`. Session 016 (road-network distance integration) is next per ROADMAP Phase 1. Update this file at the end of every session that meaningfully changes project state.*

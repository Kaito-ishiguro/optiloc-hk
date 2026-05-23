# OptiLoc HK — Claude Project Context

> **This file is the canonical handoff. Add it to Project knowledge so every new chat in this Project starts with full context. Update it whenever a session meaningfully changes the project state.**

---

## TL;DR for new chats

OptiLoc HK is a Hong Kong facility location optimizer being built by **Kaito Ishiguro**, a 2nd-year IELM student at HKU. It applies the math from his DASE2135 course (Mathematical Optimization, Spring 2026, Dr. Y.H. Kuo) to real HK demographic data. Public GitHub repo:

**https://github.com/Kaito-ishiguro/optiloc-hk**

**Current phase:** Phase 1 complete plus ten technical extensions (Integration #1 condition-number analysis; Sessions 008+009 Weiszfeld + four-solver visualization; Session 010 ArcGIS/OZP zoning integration; Session 010b SLSQP buffer-smoothness fix; Session 011 multi-facility k-median + Voronoi visualization; Session 012 OZP-constrained k-median network; Session 013 k-sweep diminishing returns + hub-location map gallery; **Session 014 Dockerize + FastAPI wrapper**). Phase 1c+ (multi-facility network optimization, unconstrained and OZP-constrained) is shipped, plus a diminishing-returns analysis. **ROADMAP Phase 1 (GCP ship + portfolio asset) is now actively underway: Session 014 shipped the containerized API with full security hardening; Session 015 will deploy it to Cloud Run in `asia-east2`.** The canonical product/business plan is **`docs/ROADMAP.md`** (commit `57b630d`). Companion to CONTEXT.md (technical handoff) and MATH.md (mathematical reference). The DASE2135 final exam was on May 11, 2026 (in the past). Prof. Kuo has emailed back acknowledging the project and offering UG research collaboration; the reply email with four-solver results was sent at the start of the Session 010 chat. **FWD Group internship starts June 8, 2026.** Kaito plans to maintain ~1-3 sessions/day through the internship (Claude credit usage is the practical limiter, not time). Kaito is studying for the **Google Cloud Associate Cloud Engineer (ACE) certification** and has ~HKD 2,000 (~USD 255) in free GCP trial credit.

**The immediate pending task at the start of this new chat: Session 015.**

Per `docs/ROADMAP.md` Phase 1, Session 015 = **first Cloud Run deploy.** Set up the GCP project (or confirm an existing one), enable the Artifact Registry + Cloud Run APIs, authenticate `gcloud`, create an Artifact Registry repo in `asia-east2`, tag and push the local `optiloc-hk:dev` image, then `gcloud run deploy` with the same security flags we validated in Session 014 (`--no-allow-unauthenticated=false` for public access; memory + CPU limits; concurrent-request cap; read-only filesystem). Final step: hit the Cloud Run URL's `/docs` from a browser to confirm Swagger renders on the open internet. This converts the DM artifact from "URL I can show you on my laptop" to "URL you can poke right now" — a step-change in Phase 1 narrative power.

Sessions 016-018 follow per ROADMAP Phase 1: road-network distance integration (016, *math foundation #1*, blocking before first paid pilot) → Cloud Build CI/CD (017) → landing page v1 (018). Detail in ROADMAP.

Alternative directions considered and deprioritized: oscillation fix for the convergence-rate dropoff seen across Sessions 012-013 (change Lloyd's stop criterion from "assignment vector unchanged" to "max facility shift < ε"); Prof. Kuo follow-up email (deferred until Phase 1 ships so the email can include the Cloud Run URL); shared `optiloc/` package refactor that would lazy-load geopandas in file 16 (deferred to Session 016 alongside road-network distance work — same surface area touched).

---

## End-of-session protocol (MANDATORY — follow exactly)

When Kaito says **"wrap up this session"** or **"log this"**, do these four things in order:

**1. Generate the JOURNAL.md entry** following the standard template (see "Journaling workflow" below).

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
- **Currently studying for the Google Cloud Associate Cloud Engineer (ACE) certification** — wants to connect every concept back to OptiLoc. Has ~HKD 2,000 (~USD 255) in free GCP trial credit available.
- **Primary goal through the OptiLoc build (per inter-session 2026-05-22):** gain repeatable experience pitching, presenting, and connecting with operational decision-makers at real companies. Revenue is a downstream outcome of that experience. Sector specifics are secondary. **He enjoys cold outreach and customer conversations** — this is an asset, not a chore. Claude should tell him when to send DMs; he's willing to do them anytime.

---

## The project at a glance

OptiLoc's pipeline ingests the WorldPop population raster → derives 41,288 weighted demand points (total population 7,496,988) → solves variants of the Weber facility-location problem (unconstrained, OSM-Kowloon-polygon-constrained, OZP-commercial-constrained) → and k-median network variants (unconstrained, OZP-constrained, plus a full k-sweep over k ∈ {3, 5, 8, 10, 15, 20}) → visualizing each as an interactive Folium map or a static matplotlib gallery. **As of Session 014, the solvers are also exposed over HTTP via a containerized FastAPI app (`api/` directory, `Dockerfile`).** All numbered scripts live in `notebooks/` (files 01–20); each is described in the codebase reference below. Math reference (objectives, gradients, KKT, Weiszfeld, Lloyd) lives in `docs/MATH.md`. Product/business plan lives in `docs/ROADMAP.md`. Claude can `web_fetch` either when needed mid-session.

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

Pydantic v2 request/response schemas. Bounded inputs (`k`, `n_restarts` with `Field(ge=, le=)`) prevent pathological-value DoS. `WeberRequest` is empty for Session 014 (no caller-supplied params yet); Session 015+ will widen it. Response models include nested `Facility` and `RestartSummary` so the response is self-documenting in Swagger.

#### `api/solvers.py`

Loads `notebooks/08_solve_weber_weiszfeld.py` and `notebooks/16_solve_kmedian_ozp.py` as modules via `importlib.util.spec_from_file_location` (same pattern as Session 013's file 18 — needed because Python module names can't start with digits). Caches the loaded modules + demand points CSV + buffered OZP geometry at FastAPI startup via `initialize_solvers()`. Thin wrappers `solve_weber()` and `solve_kmedian_ozp(k, n_restarts)` are what the endpoints call — zero math duplication; notebooks remain source of truth.

**Gotcha caught in Session 014:** file 16 imports `geopandas as gpd` at module level (for `gpd.read_file(OZP_GEOJSON)` inside `main()`). When the API imports file 16 via importlib, that top-level import fires, so the container needs `geopandas + pyogrio + pyproj` in its requirements file. Claude's first cut of `api/requirements.txt` missed this; widened on the second pass.

#### `api/main.py`

The FastAPI app. Exposes:
- `GET /healthz` — liveness probe (used by Docker `HEALTHCHECK` and Cloud Run)
- `POST /solve_weber` — Weiszfeld on baked-in HK demand
- `POST /solve_kmedian_ozp` — k-median + OZP commercial constraint, with caller-tunable `k` and `n_restarts`
- `GET /docs` — Swagger UI (kept public — this IS the DM artifact in Phase 1)
- `GET /redoc` — ReDoc (also public)

Security layer: slowapi rate limiter (`@limiter.limit(RATE_LIMIT_SOLVE)`), `asyncio.wait_for(asyncio.to_thread(...), timeout=...)` to enforce wall-clock solver timeouts, global `@app.exception_handler(Exception)` that returns `{"detail": "Internal server error.", "request_id": <uuid>}` so stack traces never leak to clients while still being grep-able server-side. CORS is `allow_origins=["*"]` (deliberate Phase 1 choice; Session 018 will lock to the landing-page origin).

Lifespan startup runs `initialize_solvers()` once per process. Lifespan shutdown is a no-op (cleanup happens via process exit).

#### `api/requirements.txt`

Lean runtime dep list — only what the container needs:
- `fastapi==0.136.1`, `uvicorn[standard]==0.47.0`, `slowapi==0.1.9`
- `numpy==2.4.4`, `scipy==1.17.1`, `pandas==3.0.2`
- `shapely==2.1.2`, `geopandas==1.1.3`, `pyogrio==0.12.1`, `pyproj==3.7.2`

Explicitly excludes folium / matplotlib / osmnx / networkx / requests / rasterio / branca / xyzservices etc. — they're needed for the notebook dev work (in repo-root `requirements.txt`) but never at API runtime. This keeps the Docker image lean (~500 MB est., compared to ~700 MB if we shipped the full dev env).

#### `Dockerfile`

Single-stage build off `python:3.14-slim`. Creates a non-root `appuser`, installs deps in a separate layer (caches well across code edits), copies only what's needed (the two notebook solver files, the two data assets, the `api/` directory), `chown`s everything to `appuser`, runs as `appuser`, adds a `HEALTHCHECK` that hits `/healthz` via `urllib.request` every 30s, exposes 8000, and `CMD`s `uvicorn` with `sh -c` so `${PORT}` env var (injected by Cloud Run) expands at runtime. No apt-get / build-essential needed — `cp314` manylinux wheels exist for all 10 deps on Linux x86_64.

#### `.dockerignore`

Allow-list pattern for `data/processed/` (only `demand_points.csv` and `ozp_commercial_union.geojson` get into the build context, not the 120 MB `ozp_all_zones.geojson` cache). Also excludes `.git`, `.venv`, `__pycache__`, `docs/`, `cache/`, `README.md`, `JOURNAL.md`, `CONTEXT.md`, `requirements.txt` (dev requirements; the API uses its own), etc. Build context for the Session 014 build was 3.69 MB total.

### `notebooks/01_ingest_worldpop.py`

**Purpose:** Convert WorldPop GeoTIFF raster into a flat CSV of demand points.

**Input:** `data/raw/hkg_ppp_2020_UNadj_constrained.tif` (downloaded from HDX; not in Git, gitignored)
**Output:** `data/processed/demand_points.csv` with columns `(lat, lon, weight)`

**Expected output:** ~41,288 demand points, total weight ~7.5M

### `notebooks/02_render_demand_points.py`

**Purpose:** Visualize the demand points as a HK population heatmap.

**Input:** `data/processed/demand_points.csv`
**Output:** `docs/maps/01_first_map.html`

Folium with HeatMap plugin (KDE-style density) plus top-50 cells as overlay markers for sanity-checking. CartoDB Positron base tiles.

### `notebooks/03_solve_weber.py`

**Purpose:** Solve the unconstrained Weber problem from a single starting point with three methods.

**Output:** `data/processed/solver_results.csv`, `trail_gradient_descent.csv`, `trail_newton.csv`

Three solvers, all vectorized NumPy: gradient descent (`alpha=1e-9, max_iter=10_000, tol=1e-3`), Newton-Raphson using `np.linalg.solve(H, -g)`, SciPy BFGS as reference. Starting point `(114.17, 22.32)`. All three converge to lon=114.17071, lat=22.33729 to 8 decimal places.

**Geographic location:** The optimum is in the **Sham Shui Po / Shek Kip Mei area**, ~1.5 km north of Prince Edward MTR. The weighted geometric median is pulled north of urban Kowloon because the New Territories holds >50% of HK's population. This is a real geographic finding, not a bug.

**Math constants:** `EPS = 1e-9` inside the square root to avoid division by zero at demand points.

### `notebooks/03_solve_weber_multi.py`

**Purpose:** Same math, 4 starting points (Tung Chung, Stanley, Sai Kung, Lok Ma Chau) for the multi-start visualization. Newton uses backtracking line search here (added in Session 004 to fix singular-Hessian failure from Tung Chung start).

### `notebooks/04_visualize_convergence.py`

**Purpose:** The Session 004 hero map — population heatmap + 8 convergence trails + 4 starting markers + gold optimum star + title + legend baked into HTML.

**Output:** `docs/maps/02_convergence_map.html`

### `notebooks/05_solve_constrained.py`

**Purpose:** KKT-constrained Weber problem with 7 inequality constraints (1 OSM "Kowloon" polygon + 1 MTR proximity + 5 competitor exclusion).

**Output:** `data/processed/constrained_result.csv`, `constraints_geo.csv`, `kkt_multipliers.csv`

**Method:** SciPy SLSQP. Fetches the OSM polygon labeled "Kowloon" and all 624 MTR exits live from OSM via `osmnx`.

**Critical design decision (signed-distance constraints):** All constraints are continuous signed-distance functions in standard `g_j(x) <= 0` form. NOT boolean inside/outside checks. Boolean checks make the constraint function flat with cliffs at the boundary; signed distances give the optimizer a smooth gradient pointing toward feasibility.

**Sign convention gotcha:** Textbook math uses `g_j <= 0`. SciPy's `{"type": "ineq", "fun": ...}` expects `fun(x) >= 0`. Each constraint is negated when handed to SLSQP.

**Result:** Constrained optimum at `(114.17323, 22.34038)` — on the OSM "Kowloon" polygon boundary, ~444 m **northeast** of the unconstrained answer. Geographically the constrained optimum lands at the Beacon Hill / Tai Wo Ping area. Kowloon constraint active ($\mu_1 > 0$); MTR and 5 competitor constraints inactive. Empirical demo of complementary slackness.

**Geographic finding (revised in Session 010 from map inspection):** The OSM polygon labeled "Kowloon" that osmnx returned in this session has its boundary at the **Lion Rock / Beacon Hill ridge**, NOT at Boundary Street as originally documented. The polygon's actual provenance — whether it's the modern Kowloon administrative district, a particular historical boundary, or some OSM-specific tagging — wasn't pinned down at the time and warrants re-investigation. The constraint binds because the unconstrained Weber center (Sham Shui Po / Shek Kip Mei area, lat 22.337) sits just south of the polygon's boundary, and SLSQP pushes north onto the boundary.

### `notebooks/06_visualize_constrained.py`

**Output:** `docs/maps/03_constrained_map.html` + two screenshots (`constrained_map_wide.png`, `constrained_map_zoom.png`).

### `notebooks/07_condition_number.py`

**Purpose (Integration #1):** Empirically measure Hessian conditioning across HK to explain why GD was 50× slower than Newton.

**Output:** Prints analysis tables to terminal; no output file.

**Empirical finding (committed as fact):**
- $\kappa$ ranges 1.24–3.25 across all 6 points: **Weber problem is uniformly well-conditioned everywhere in HK.**
- $\lambda_{\max}$ varies by 3.4× across space: **Hessian magnitude is non-constant**, signature of a non-quadratic objective.
- $\alpha_{\text{opt}}$ varies by ~4× across space.
- Our chosen $\alpha = 10^{-9}$ was 8–45× smaller than optimal at every test point.
- **Lecture 6's textbook "high $\kappa$ ⇒ slow GD" does NOT apply here.** The real reason is non-quadratic spatial variation in curvature. Newton's $H^{-1}$ self-adapts; constant-$\alpha$ GD cannot.

### `notebooks/08_solve_weber_weiszfeld.py`

**Purpose (Session 008):** Implements the Weiszfeld fixed-point iteration that Prof. Kuo flagged in his email — the FONC-derived solver missing from Session 003. Also re-runs all 4 solvers (Weiszfeld, Newton, BFGS, GD) from the same Victoria Harbour start and records trails.

**Math:** See `docs/MATH.md` (the Weiszfeld iteration section).

**Output:** `data/processed/solver_comparison.csv` (4-row summary), `data/processed/four_solver_trails.csv` (292 trail positions across all 4 solvers).

**Empirical results on 41,288 HK demand points (committed as fact):**
- **Weiszfeld:** 23 iterations, ~7.6ms
- **Newton:** 4 iterations, ~7.2ms
- **BFGS:** 7 iterations, ~5.5ms
- **GD:** 255 iterations, ~55ms
- All four agree on the (Shek Kip Mei area) optimum to within $7.7 \times 10^{-9}$ degrees (sub-millimeter on the ground)

**Key insight from Session 008:** Weiszfeld *ties* Newton on wall-clock despite Newton's quadratic convergence rate (4 iterations) vs Weiszfeld's linear rate (23 iterations). Reason: Time = iterations × per-iteration cost. Newton's per-iteration cost is ~6× Weiszfeld's because it computes and factorizes the 2×2 Hessian; Weiszfeld just does one weighted average. **On 2D Weber, the per-iteration cost gap cancels the asymptotic-rate advantage.** Linear convergence with cheap iterations beats quadratic with expensive iterations on small problems. **Sessions 011, 012, 013, and 014 reinforced this empirically across thousands of sub-solves with zero Weiszfeld failures.**

**Convergence criterion gotcha:** All four solvers in this file use **step-size convergence** ($\|x_{\text{new}} - x\| < \varepsilon$), not gradient-norm convergence. Newton originally hit max_iter=100 chasing floating-point noise in $\|\nabla f\|$ — switching to step-size made Newton report its real iteration count (4). Convergence criteria must be consistent across solvers for benchmarking to be honest.

**Imported by the API as of Session 014:** `api/solvers.py` loads this file via `importlib.util` and calls `weiszfeld(points, weights, x0)` and `objective(x, points, weights)` directly. Function signatures are now part of the API contract; changes to them would need coordinated updates in `api/solvers.py`.

### `notebooks/09_visualize_four_solvers.py`

**Purpose (Session 009):** The four-solver convergence map. Reads `four_solver_trails.csv` and renders a Folium map with all four convergence trails color-coded.

**Output:** `docs/maps/04_four_solvers_map.html` + two committed screenshots:
- `docs/maps/four_solvers_wide.png` (zoomed out, shows journey from Victoria Harbour to the optimum with all 4 trails)
- `docs/maps/four_solvers_zoom.png` (zoomed in on the optimum, shows all 4 trails converging to gold star)

**Visual encoding:**
- **Weiszfeld** = purple thick solid (the star of the show)
- **Newton** = red thin solid (only 4 segments — short)
- **BFGS** = teal dashed (7 segments — medium)
- **GD** = gray thin dashed (255 segments — the long worm)

These screenshots were attached to the email reply to Prof. Kuo.

### `notebooks/10_fetch_ozp.py`

**Purpose (Session 010):** Paginated fetch of all 11,963 Hong Kong Outline Zoning Plan polygons from Esri China HK's public ArcGIS REST feature service. Saves to a cached GeoJSON file with geometries reprojected server-side from HK1980 Grid (EPSG:2326) to WGS84 (EPSG:4326).

**Service endpoint discovered via metadata-driven lookup:** `https://services3.arcgis.com/6j1KwZfY2fZrfNMR/arcgis/rest/services/ZONE/FeatureServer/0`. The discovery pattern: AGOL item ID → sharing API → service URL → service metadata → layer fields → paginated query. This is the same metadata-discovery pattern used in GCP Service Discovery / API Gateway routing.

**Output:** `data/processed/ozp_all_zones.geojson` (~120 MB, gitignored; also excluded from Docker build context via `.dockerignore` allow-list).

**Pagination strategy:** `resultOffset` + `resultRecordCount=2000` (the service's `maxRecordCount`), `orderByFields=OBJECTID` for stable ordering, 60s `timeout`. Six pages total. **Operational warning:** the last page took exactly 60s on the only run we've done, dangerously close to the timeout. Any production / scheduled-job version of this script should use a 120s timeout and add exponential-backoff retry.

**Filter rationale:** the script intentionally caches the FULL dataset (all 157 zoning categories), not just the C+CDA subset. This makes downstream filtering changes (add C/R mixed-use, add Industrial, etc.) free — no re-fetch needed.

### `notebooks/11_filter_and_union_ozp.py`

**Purpose (Session 010):** Filter the cached OZP zones to Commercial (C) and Comprehensive Development Area (CDA) categories, union them into a single MultiPolygon, save as a small standalone GeoJSON used as the feasibility region for the constrained Weber and k-median solvers.

**Output:** `data/processed/ozp_commercial_union.geojson` (~1.27 MB, gitignored locally but **baked into the Docker image as of Session 014**).

**Filter logic — the "C-prefix trap":** `ZONE_LABEL` has 157 distinct values, and several start with "C" but are not commercial-eligible: `CA` (Conservation Area), `CP` (Country Park), `CPA` (Coastal Protection Area), `C/R` (mixed Commercial/Residential). The filter explicitly disambiguates: accept only exact `C`/`CDA` or labels matching `C(N)` / `CDA(N)`. The parenthesis pattern (commercial sub-zones) cleanly separates the desired categories from the false-positive C-prefixes.

**Empirical result (committed as fact):** 590 features pass the C + CDA filter. After geometric union, the result is a 499-piece MultiPolygon totaling **10.30 km²** = 0.9% of HK's 1,106 km² land area. Hong Kong has remarkably little commercially-zoned land.

**CRS handling:** Area is computed by reprojecting briefly to HK1980 Grid (EPSG:2326, meters) since lat/lon area is mathematically meaningless. The saved geometry stays in WGS84 (EPSG:4326) so downstream solvers don't need to reproject.

### `notebooks/12_solve_constrained_ozp.py`

**Purpose (Sessions 010 + 010b):** Solve the Weber problem subject to the new realistic constraint: optimum must lie inside the C + CDA commercial union. This replaces Session 005's "must be inside the OSM Kowloon polygon" constraint with something ~5× more restrictive and 499× more topologically complex.

**Constraint form:** Same signed-distance pattern as Session 005, applied to a 499-piece MultiPolygon. $g(x) > 0$ inside, $g(x) < 0$ outside, $g(x) = 0$ on the boundary. SLSQP's `{'type':'ineq'}` convention is `fun(x) >= 0` = feasible.

**Session 010b — buffer-smoothness fix.** The union geometry is buffered by `1e-6` degrees (~10 cm on the ground) before constructing the constraint:

```python
union_geom = ozp_gdf.iloc[0].geometry.buffer(1e-6)
```

This rounds the 499 polygon corners and merges adjacent-polygon medial-axis kinks at sub-millimeter scale, giving SLSQP's finite-difference Jacobian a smooth gradient to chase. After this fix, SLSQP terminates with **Exit mode 0 in 16 iterations** (was Exit mode 9 / 200 iters in Session 010 before the buffer). Why this works without distorting the problem: the OZP polygon data itself was digitized at meter-scale precision by Lands Department, so a 10 cm round-off is well below the data's noise floor.

**Output:** `data/processed/ozp_constrained_result.csv` (1-row summary).

**Empirical result (committed as fact):**
- Optimum: **(114.16944, 22.33321)** — Shek Kip Mei, on the boundary of a small C-zoned polygon.
- Constraint value at optimum (post-010b): `g_ozp(x*) ≈ -5.3 × 10⁻¹¹` — sub-millimeter ground distance; optimum is essentially exactly on the boundary.
- Shift from unconstrained: ~474 m southwest.
- Convergence: Exit mode 0, 16 iterations, 44 function evaluations.

### `notebooks/13_visualize_ozp_constrained.py`

**Purpose (Session 010):** The OZP-constrained comparison map. Renders the demand heatmap, the 499 C+CDA polygons as a translucent teal overlay, and three optima markers: unconstrained (gold star), Kowloon-polygon constrained (red dot), OZP-commercial constrained (purple star).

**Output:** `docs/maps/05_ozp_constrained_map.html` + two committed screenshots (`ozp_constrained_wide.png`, `ozp_constrained_zoom.png`).

### `notebooks/14_solve_kmedian.py`

**Purpose (Session 011):** Multi-facility k-median solver — the "k facilities for HK" generalization of the single-facility Weber problem. Uses Lloyd's algorithm as the outer loop and Weiszfeld as the inner Weber sub-problem solver.

**Hyperparameters (committed as fact):** `K=5`, `N_RESTARTS=10`, `MAX_LLOYD_ITERS=50`, Weiszfeld inner tol `1e-7`, max 100 iters, `EPS=1e-9`, `RNG_SEED=42`.

**Algorithm structure:** Each Lloyd iteration alternates two sub-problems. **Assignment step** — vectorized argmin over an n×k distance matrix. **Update step** — Weiszfeld solve per cluster; empty clusters are skipped. Convergence: unchanged assignment vector between iterations. Multi-start: 10 weighted-random inits — keep best objective.

**Output:** `data/processed/kmedian_result.csv` (5 rows), `data/processed/kmedian_trails.csv` (~80 rows).

**Empirical results (committed as fact):**
- Best objective across 10 restarts: **274,830 weighted-units** — a **59.1% reduction** from the single-facility Weber baseline of 671,466.
- Multi-start found **≥4 distinct local minima** from 10 inits; **worst-best gap 9.3%**.
- Total runtime: **5.74s** for ~1000 Weber sub-solves.
- Final 5 facilities: F1 Tai Po area, F2 central Kowloon, F3 Tuen Mun area, F4 Tsuen Wan area, F5 Kwun Tong area.

**Key empirical finding — non-convexity is real and expensive:** 4+ distinct local minima from 10 random inits is empirical proof that the joint (facilities, assignments) problem is non-convex despite each sub-problem being convex. Multi-start isn't optional on k-median.

### `notebooks/15_visualize_kmedian.py`

**Purpose (Session 011):** Folium map of the k=5 k-median network result with Voronoi service-area polygons, convergence trails, and facility markers.

**Voronoi construction:** Uses `shapely.ops.voronoi_diagram` with an HK bounding-box envelope to produce 5 clipped Voronoi cells. **Gotcha:** the diagram's output order is implementation-defined; each output polygon is matched to its facility by a point-in-polygon containment test before rendering.

**Output:** `docs/maps/06_kmedian_map.html` plus two committed PNG screenshots (`kmedian_map_wide.png`, `kmedian_map_zoom.png`).

### `notebooks/16_solve_kmedian_ozp.py`

**Purpose (Session 012):** OZP-constrained k-median network solver. Combines Session 011's Lloyd outer loop with Session 010b's constrained Weber inner solver. Each per-cluster Weber sub-problem is now restricted to the buffered OZP commercial union $\Omega$.

**Inner-solver strategy — conditional invocation:**
1. Run unconstrained Weiszfeld on the cluster.
2. Test `commercial_union.contains(Point(x_weiszfeld))`.
3. If feasible, keep it. If infeasible, fall back to SLSQP warm-started from the Weiszfeld result.

**Empirical reality (committed as fact): SLSQP fired on ~100% of Weiszfeld calls** because Kowloon is mostly residential by area; commercial sits in narrow corridors. The conditional logic was right by design (no harm done) but wrong by empirical prediction.

**Hyperparameters:** Same as Session 011 (`K=5`, `N_RESTARTS=10`, `MAX_LLOYD_ITERS=50`, `RNG_SEED=42`). Plus: `BUFFER=1e-6`, `SLSQP_MAXITER=200`, `SLSQP_FTOL=1e-8`.

**Output:** `data/processed/kmedian_ozp_result.csv`, `kmedian_ozp_trails.csv`, `kmedian_ozp_diagnostics.csv`.

**Empirical results (committed as fact):**
- Best objective: **277,595 weighted-units** — only **+1.0% penalty** over Session 011's unconstrained 274,830.
- Translated: avg HK resident is ~4.0 km from nearest of 5 facilities (vs ~3.9 km unconstrained). OZP constraint costs ~40 m of extra travel per resident.
- Multi-start found **9 distinct local minima** from 10 inits; worst-best gap **23.1%** (constraint roughly *doubled* non-convexity).
- Total runtime: **107s** (~20× Session 011, due to ~100% SLSQP-fire rate).
- 4/10 restarts hit `MAX_LLOYD_ITERS=50` without converging, including the winner. Likely cause: assignment-vector oscillation around stable facility positions. Deferred fix.
- HK's commercial zoning is well-aligned with population distribution → +1% penalty is small.

**Imported by the API as of Session 014:** `api/solvers.py` loads this file via `importlib.util` and calls `lloyd_one_restart(demand, weights, feasible_geom, k, rng, restart_id)` directly. **Key gotcha:** file 16 has `import geopandas as gpd` at module level (used only inside `main()` for the geojson load). Importing file 16 via importlib triggers that top-level import, so the Docker image must include geopandas + pyogrio + pyproj even though the `lloyd_one_restart` function itself doesn't use them. Deferred refactor (lazy-load geopandas inside `main()`) was noted for Session 016 alongside the road-network-distance work.

### `notebooks/17_visualize_kmedian_ozp.py`

**Purpose (Session 012):** Folium map of the OZP-constrained k=5 k-median result with commercial-zone overlay, Voronoi service areas, dashed Lloyd trails, init + final facility markers.

**Layer z-order (bottom to top):** CartoDB Positron base → demand heatmap → OZP commercial union (subtle beige overlay, `#D6B36A` at 22% opacity) → 5 Voronoi service areas → dashed Lloyd trails → init markers → final facility markers → title + legend HTML overlay.

**Output:** `docs/maps/07_kmedian_ozp_map.html` plus two committed PNG screenshots (`kmedian_ozp_map_wide.png`, `kmedian_ozp_map_zoom.png`).

### `notebooks/18_ksweep_ozp.py`

**Purpose (Session 013):** k-sweep diminishing-returns solver. Wraps Session 012's `lloyd_one_restart` (from `notebooks/16_solve_kmedian_ozp.py`) in an outer k-loop, sweeping k ∈ {3, 5, 8, 10, 15, 20} with `N_RESTARTS=10` each.

**Import mechanic:** Python module names can't start with a digit, so `import notebooks.16_solve_kmedian_ozp` doesn't work. The script uses `importlib.util.spec_from_file_location` to load file 16 as a module, then calls `sess12.lloyd_one_restart(...)` directly — zero math duplication, single source of truth for the Lloyd + Weiszfeld + SLSQP machinery. **This pattern is reused by `api/solvers.py` in Session 014.**

**Reproducibility design:** Fresh `np.random.default_rng(RNG_SEED=42)` per k value. This means the k=5 run inside the sweep exactly reproduces Session 012's 277,595 — a baked-in sanity check that passed on first attempt. Crash-safe: all three summary CSVs are rewritten after each k completes, so a late crash preserves earlier k results on disk.

**Output:** `data/processed/ksweep_ozp_summary.csv` (one row per k with best/worst/mean objective, gap, convergence rate, runtime), `ksweep_ozp_all_restarts.csv` (one row per restart for distribution analysis), `ksweep_ozp_best_facilities.csv` (best facility locations at each k — input to file 20).

**Empirical results (committed as fact):**

| k  | best_obj | pct_reduction | worst_best_gap | converged |
|----|----------|---------------|----------------|-----------|
| 3  | 384,054  | 42.8%         | 3.7%           | 10/10     |
| 5  | 277,595  | 58.7%         | 23.1%          | 6/10      |
| 8  | 208,181  | 69.0%         | 17.5%          | 7/10      |
| 10 | 177,517  | 73.6%         | 13.5%          | 7/10      |
| 15 | 133,490  | 80.1%         | 27.3%          | 8/10      |
| 20 | 113,868  | 83.0%         | 40.1%          | 5/10      |

Total sweep runtime: **6.3 min** (faster than the 20-min initial estimate). Marginal gain per added facility drops from ~8pp/facility (3→5) to ~0.6pp/facility (15→20). **Elbow at k ≈ 8–10.** Convergence rate drops sharply at k=20 (5/10) — Session 012's oscillation issue amplifies with k.

**Session 014 reproducibility check:** The API's `/solve_kmedian_ozp` endpoint with `k=3, n_restarts=2` returned `best_objective=384,054.11420394183` — exact match to this table's k=3 entry. The importlib-based wrapping preserves bit-for-bit numerical equivalence.

### `notebooks/19_visualize_ksweep.py`

**Purpose (Session 013):** Two-panel landing-page chart of the diminishing-returns story. Reads `ksweep_ozp_summary.csv` and `ksweep_ozp_all_restarts.csv`.

**Top panel:** Best objective vs k as the navy line+markers, multi-start min-max range as a light blue band, median across restarts as a dotted gray line. Per-point % reduction labels (`−43%`, `−59%`, ..., `−83%`) anchored below each marker. Dashed horizontal reference line at the single-facility Weber baseline (671k weighted-units) with italic label.

**Bottom panel:** Worst-best gap (%) as purple bars, with "X/10 converged" labels above each bar. Shows non-convexity worsening with k (gap grows 3.7% → 40.1% from k=3 to k=20) alongside Lloyd's declining convergence rate (10/10 → 5/10).

**Output:** `docs/maps/08_ksweep_diminishing_returns.png` (DPI 180, ~10×9 in, landing-page hero).

### `notebooks/20_visualize_ksweep_maps.py`

**Purpose (Session 013):** 2×3 panel gallery showing the best hub network at each k value. The spatial dual of file 19's chart — chart answers "how many?", gallery answers "and where, at each scale?"

**Per-panel layering (bottom to top):** weighted demand hexbin in Greys (subtle population density background, `bins='log'`, gridsize=80, mincnt=1, alpha=0.55), OZP commercial union overlay in beige (`#D6B36A` at 22% alpha), Voronoi service areas (one color per facility from `tab20`, 28% alpha with thin matching-color edges), facility markers (navy `#1f3a5f` dots with white edges, zorder=10).

**Voronoi cell matching:** Same pattern as Sessions 011/012/017 — `shapely.ops.voronoi_diagram(MultiPoint, envelope=HK_BBOX)` returns polygons in implementation-defined order, so each cell is matched to its facility via point-in-polygon containment. `HK_BBOX = (113.82, 22.15, 114.45, 22.58)` covers HK Island + Kowloon + NT + outer islands; all six panels share this bbox so they're directly comparable.

**Output:** `docs/maps/09_ksweep_hub_locations.png` (DPI 160, 18×12 in).

**Empirical finding (committed as fact):** As k grows, marginal hubs cluster in already-dense urban cores (Kowloon, north HK Island), not in underserved NT or outer islands. The total-weighted-distance objective concentrates capacity where population is already concentrated. This is the right behavior for utilization-driven customers (EV charging operators, last-mile delivery), and the wrong behavior for equity-driven customers (public-health planning, rural service). **Different customer profiles need different objective functions** — a key data point for ROADMAP Phase 2 customer-discovery conversations.

---

## The math, frozen for reference

Math reference (objectives, gradients, Hessian, Weiszfeld, KKT, k-median, Lloyd, constrained k-median) is in **`docs/MATH.md`**. When math grounding is needed mid-session, `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md.

## The product/business plan

Product and business roadmap is in **`docs/ROADMAP.md`** (shipped at commit `57b630d`, May 22, 2026). Canonical 5-phase plan (Phase 1 GCP ship → Phase 2 customer discovery + math hardening → Phase 3 first paid pilot + React frontend → Phase 4 productize what consulting taught → Phase 5 decision gate). When business/product context is needed mid-session (pricing, vertical pick, customer discovery timing, anti-roadmap, what's in/out of scope), `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/ROADMAP.md.

---

## Tech stack

- **Language:** Python 3.14 (he upgraded between Sessions 013 and 014; `cp314` wheels exist on both Windows and Linux for all our deps)
- **Environment:** `venv` at `.venv/`, activated via `.venv\Scripts\Activate.ps1` on Windows
- **Package install:** `python -m pip install -r requirements.txt` (NOT `pip install` — Smart App Control blocks unsigned pip.exe)
- **Numerical:** NumPy (vectorized math, ~1ms per gradient evaluation on 41k points), SciPy (BFGS reference, SLSQP for constrained)
- **Geographic:** rasterio (raster I/O), osmnx (OSM fetching), shapely (polygon distance + union + `shapely.ops.voronoi_diagram` for Voronoi service areas with envelope clipping), GeoPandas (vector I/O), `requests` (raw ArcGIS REST in Session 010 — no Esri SDK)
- **Visualization:** Folium (interactive Leaflet maps) for HTML outputs; matplotlib (multi-panel static galleries with hexbin density backgrounds, GeoDataFrame overlays, and Voronoi cell fills) for landing-page PNGs
- **Tabular data:** pandas
- **Module reuse:** `importlib.util.spec_from_file_location` for loading numbered scripts (file 18 reuses file 16's solver this way; **`api/solvers.py` reuses files 08 + 16 this way as of Session 014**)
- **HTTP API (Session 014):** FastAPI 0.136.1 + Uvicorn 0.47.0 + Pydantic 2.13.4 + slowapi 0.1.9. Async endpoints use `asyncio.to_thread()` + `asyncio.wait_for()` to wrap synchronous solvers with wall-clock timeouts. CORS open via `fastapi.middleware.cors`. Global `@app.exception_handler(Exception)` for sanitized error responses with `request_id`.
- **Containerization (Session 014):** Docker Desktop 4.67.0 (Engine 29.3.1) on Windows with WSL2 backend producing linux/amd64 images. `python:3.14-slim` base, single-stage build, non-root user, `--read-only` + `--tmpfs /tmp:rw,size=64m` at runtime, `HEALTHCHECK` via Python's `urllib.request`.
- **Version control:** Git, public GitHub repo at `github.com/Kaito-ishiguro/optiloc-hk`

**Planned for ROADMAP Phase 1 (Sessions 015–018):**
- GCP: Cloud Run (serverless container hosting in `asia-east2`), Cloud Storage (data assets), Cloud Build (CI from GitHub), Artifact Registry (container image storage), IAM (service accounts) — Session 015 onward
- OSRM (self-hosted on Cloud Run) or Google Distance Matrix API — for road-network distance (Session 016, *math foundation #1* per ROADMAP)

---

## Environment specifics (Windows quirks)

Kaito is on Windows 11 with PowerShell.

- **Smart App Control was disabled** in Session 002 to allow pandas/rasterio C extensions to load.
- **PowerShell `mkdir -p` doesn't work.** Use comma-separated args or `New-Item -ItemType Directory -Force`.
- **`pip` direct calls can be blocked by SAC.** Always use `python -m pip install ...`
- **`Move-Item` with `-Force`** is needed if the destination file exists.
- **Git on Windows complains about LF→CRLF line endings.** Harmless; ignore.
- **`osmnx` creates a `cache/` folder** in the repo root. Gitignored.
- **Activate venv first** in every new PowerShell session: `cd "C:\Users\Kaito Ishiguro\Documents\optiloc-hk"` then `.venv\Scripts\Activate.ps1`. Look for `(.venv)` in the prompt.
- **Snipping Tool** (`Win+Shift+S`) for screenshots, paste into Paint, save as PNG into `docs/maps/`.
- **For PowerShell one-liner Python with `requests`:** `python -c "import requests; ..."` works fine; double quotes on the outside, single quotes inside the JSON params dict. Don't use multi-line `-c` strings; PowerShell mangles them.
- **PowerShell here-strings** (`@' ... '@`) require the closing `'@` to be at column 0 (no leading whitespace) or PowerShell errors. Single-quoted here-strings don't interpolate `$VARS` or `${VARS}` — safe for Dockerfile and Python content. Used throughout Session 014 for file writes.
- **`Invoke-RestMethod`** is the right tool for hitting HTTP endpoints from PowerShell, NOT `curl` (which is an alias for `Invoke-WebRequest` and behaves differently). For POST with JSON body: `Invoke-RestMethod -Method Post -ContentType "application/json" -Body '{"k":3}' http://...`
- **Docker Desktop on Windows** runs Linux containers via WSL2. The local image platform is `linux/amd64`, matching Cloud Run. Daemon must be running (whale icon in system tray) before `docker build` / `docker run`.

---

## Where we are right now (the immediate state)

**Session 014 is shipped.** The OptiLoc solvers now run inside a Docker container as a FastAPI HTTP service. Local validation passed (uvicorn + curl from a second PowerShell window) and container validation passed (docker run with `--read-only --tmpfs /tmp:rw,size=64m` + `Invoke-RestMethod`). All three endpoints reproduce notebook results exactly:
- `/healthz` → `{"status": "ok", "version": "0.1.0"}`
- `/solve_weber` → lon=114.17071, lat=22.33729, iterations=23 (matches Session 008)
- `/solve_kmedian_ozp` with `k=3, n_restarts=2` → best_objective=384,054.114 (exact match to Session 013's k=3 row)

**Security hardening verified working in a real container:** Pydantic-bounded inputs, slowapi rate limit (5/min/IP), `asyncio.wait_for` solver timeouts (30s Weber, 180s k-median), global exception handler with sanitized 500 + request_id, non-root `appuser`, read-only root FS, 64MB tmpfs `/tmp`, `HEALTHCHECK` firing every 30s from inside the container. The Swagger `/docs` is deliberately public — it's the DM artifact.

**Image size note:** Total build time was 248s (3.7 min in pip install for the heavy scipy/pandas/geopandas wheels, ~30s in setup + layer export). Build context just 3.69 MB thanks to `.dockerignore` allow-list pattern. No apt-get / build-essential needed — `cp314` manylinux wheels existed for every dep on Linux x86_64.

**Empirical findings worth keeping front-of-mind for Session 015:**
- The container is configured to read `PORT` from env (Cloud Run injects this; defaults to 8000 locally). `uvicorn --host 0.0.0.0 --port ${PORT}` via `sh -c` in CMD handles substitution.
- The two baked-in data assets total ~1.3 MB (demand_points.csv ~1 MB + ozp_commercial_union.geojson 1.27 MB). Trivial for Cloud Run; no need to externalize to Cloud Storage yet.
- Cold-start expectation for Cloud Run: ~5-10s including pip-installed-package import overhead + lifespan startup (loading the OZP geojson). To be measured in Session 015.

**Next up: Session 015 — first Cloud Run deploy.** Concrete steps: set up GCP project (or confirm existing), enable Artifact Registry + Cloud Run APIs, `gcloud auth login` + `gcloud auth configure-docker`, create Artifact Registry repo in `asia-east2`, tag `optiloc-hk:dev` → push, then `gcloud run deploy optiloc-api --image=... --region=asia-east2 --allow-unauthenticated --memory=1Gi --cpu=1 --concurrency=10 --max-instances=3 --read-only`. Final: hit the auto-generated `*.a.run.app` URL's `/docs` from a browser and confirm Swagger renders on the open internet. Estimated time: 1-2 hours, mostly waiting on GCP API enablement and the first push.

Subsequent ROADMAP Phase 1 sessions: 016 road-network distance integration (math foundation #1; also where we'll do the file-16 geopandas-lazy-load refactor) → 017 CI/CD via Cloud Build → 018 landing page v1.

---

## Session history (compressed)

- **Session 001 — Project genesis.** Scoped the project, picked Weber facility location, decided on logistics pivot for Phase 3.
- **Session 002 — WorldPop ingestion pipeline.** Set up Python env (with SAC fix), built the data pipeline, rendered 41k demand points.
- **Session 003 — Hand-rolled solvers.** Derived gradient + Hessian by hand. Implemented GD + Newton + BFGS. Optimum at lat 22.33729, lon 114.17071 — Sham Shui Po / Shek Kip Mei area.
- **Session 004 — Multi-start visualization.** 4 starting points × 2 methods. Added backtracking line search to Newton after singular-Hessian failure.
- **Session 005 — KKT-constrained optimization.** Hand-derived Lagrangian + 4 KKT conditions. Signed-distance constraints. Constrained optimum at (114.17323, 22.34038) — on the boundary of the OSM "Kowloon" polygon, Beacon Hill / Tai Wo Ping area. Empirical complementary slackness.
- **Session 006 — README + Phase 1 shipped.** Polished README, screenshots, LinkedIn post draft.
- **Session 007 / Integration #1 — Condition number analysis.** $\kappa$ ranges 1.24–3.25 across HK; Weber problem uniformly well-conditioned. Non-quadratic spatial variation in curvature is the real reason GD is slow, not high $\kappa$. Committed alongside Sessions 008+009.
- **CONTEXT.md added** with chat-switch protocol baked in.
- **Email from Prof. Kuo (between sessions).** Acknowledged the project, suggested ArcGIS and Weiszfeld, offered UG research collaboration.
- **Session 008+009 — Weiszfeld + four-solver visualization (commit `0503794`).** Implemented Weiszfeld in ~10 lines. 4-solver comparison; all converge to same optimum to $10^{-9}$ degrees. Weiszfeld ties Newton on wall-clock despite linear vs quadratic rate.
- **Email reply to Prof. Kuo sent (start of Session 010 chat).** Four-solver results + commitment to ArcGIS/OZP integration.
- **Session 010 — ArcGIS / OZP commercial zoning integration (commit `9d8a545`).** Fetched 11,963 OZP polygons, filtered to 590 C+CDA features, unioned into a 499-piece MultiPolygon (10.30 km², 0.9% of HK land). Constrained Weber optimum at Shek Kip Mei. SLSQP hit maxiter; deferred fix to 010b.
- **Session 010b — SLSQP buffer-smoothness fix.** Added `.buffer(1e-6)`. SLSQP terminates Exit mode 0 in 16 iterations. ~30 min.
- **Session 011 — k-median network + Voronoi visualization.** Lloyd + Weiszfeld at k=5, 10 restarts, ~5.74s. Best obj 274,830 = 59.1% reduction from single-facility. Multi-start found ≥4 distinct local minima — non-convexity proof.
- **Session 012 — Constrained k-median shipped (commit `8036089`).** Composition session. Best obj 277,595 = +1.0% penalty over unconstrained k=5. Constraint roughly *doubled* non-convexity (9 distinct local minima vs ≥4). Conditional invocation didn't save runtime as predicted (SLSQP fired ~100% of the time). **Phase 1c+ shipped.** Wrap-up also extracted math reference to `docs/MATH.md`.
- **Inter-session — 2026-05-22 — Strategic pivot & roadmap (commit `57b630d`).** Tore down the AI-drafted "OptiLoc B2B SaaS Business Plan" PDF Kaito uploaded; rebuilt as realistic 5-phase roadmap. Decided HK-only, EV charging as default vertical (flexible), math foundations non-skippable, hybrid open source, step-based not date-based. Primary goal of the build clarified: gain repeatable pitching/presenting experience with operational decision-makers; revenue is downstream. Shipped `docs/ROADMAP.md` as canonical product/business reference.
- **Session 013 — 2026-05-22 — k-sweep diminishing returns + hub-location maps (commit `0c7e830`).** Three files shipped: 18 (k-sweep solver wrapping file 16 via `importlib.util`), 19 (two-panel diminishing-returns chart with multi-start band + convergence-rate annotations), 20 (2×3 hub-location map gallery with weighted-hexbin background + OZP overlay + Voronoi cells). 6.3-min sweep over k ∈ {3, 5, 8, 10, 15, 20}, 10 restarts each, fresh RNG per k. k=5 reproduces Session 012's 277,595 exactly. **Elbow at k ≈ 8–10.** Spatial finding: marginal hubs at high k cluster in urban density, not in underserved sparse areas — total-weighted-distance objectives concentrate where population is concentrated. Different customer profiles will need different objective functions. Convergence-rate dropoff at k=20 (5/10) noted, fix deferred.
- **Session 014 — 2026-05-23 — FastAPI + Docker ship.** Eight new files: `api/__init__.py`, `api/config.py`, `api/models.py`, `api/solvers.py`, `api/main.py`, `api/requirements.txt`, `.dockerignore`, `Dockerfile`. FastAPI app exposes `/healthz` + `/solve_weber` + `/solve_kmedian_ozp` + `/docs` Swagger. Importlib reuse of files 08 + 16 (zero math duplication). Security: Pydantic-bounded inputs, slowapi rate limit, asyncio solver timeouts, sanitized errors, non-root container user, read-only root FS, 64MB tmpfs `/tmp`, HEALTHCHECK. Docker image (`optiloc-hk:dev`) built in 4 min, build context 3.69 MB. Reproducibility verified inside container: Weber returns Session 008's 23-iter optimum; k=3 k-median returns Session 013's 384,054 exactly. **Key insight: security posture should be proportional to deployment stage, not maximal.** Disabled-`/docs` and API-auth items from the generic security checklist were skipped as wrong for a Phase 1 DM artifact; kept the cheap-and-essential items. **ROADMAP Phase 1 first step shipped.**

---

## Triggers and protocols

- **"wrap up this session"** or **"log this"** → generate journal entry following the template above, THEN ask the chat-switch question.
- **"let's start session NNN"** → assume Kaito has read this context file and proceed directly into the work.
- **"don't include this in the file but tell me..."** → give thorough technical explanation outside the journal.
- **Terminal commands** → ONE step at a time, wait for "done" or error.
- **New math concept** → use the math-concept-tutor skill at `/mnt/skills/user/math-concept-tutor/SKILL.md`.
- **Empirical findings that contradict textbook predictions** → treat as the more interesting result.
- **Optimizer non-convergence or surprising results** → don't smooth them over; visualize, diagnose, and document the failure mode.
- **Real-world deployment-relevant result shipped** → before wrapping, translate the math finding into deployment terms. Add "Real-world meaning of the output" section to journal entry.
- **Math grounding needed mid-session** → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md
- **Business/product grounding needed mid-session** (pricing, vertical, customer discovery timing, phase scope, anti-roadmap) → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/ROADMAP.md
- **Kaito ready to do customer outreach** → per ROADMAP Phase 2, draft personalized DM script for the persona. He's willing to send DMs anytime; tell him when.
- **Security checklist or security question** → see "Security posture" under "How to work with Kaito". Goal is proportional security, not maximal. Cut items wrong for the current phase; keep cheap-and-essential.

---

## Files NOT in Git but referenced

- `data/raw/hkg_ppp_2020_UNadj_constrained.tif` — WorldPop GeoTIFF, ~231KB, downloaded from HDX
- `data/processed/*.csv` — all generated outputs (gitignored, regenerable), including the three Session 013 k-sweep outputs (`ksweep_ozp_summary.csv`, `ksweep_ozp_all_restarts.csv`, `ksweep_ozp_best_facilities.csv`)
- `data/processed/ozp_all_zones.geojson` — ~120 MB cached ArcGIS response (gitignored; also excluded from Docker build context via `.dockerignore`)
- `data/processed/ozp_commercial_union.geojson` — ~1.27 MB filtered + unioned constraint geometry (gitignored locally; **baked into Docker image** as of Session 014)
- `data/processed/demand_points.csv` — ~1 MB demand point CSV (gitignored locally; **baked into Docker image** as of Session 014)
- `docs/maps/*.html` — generated maps (gitignored, regenerable)
- `cache/*.json` — osmnx OpenStreetMap cache (gitignored)
- `.venv/` — Python virtual environment (gitignored)
- Docker image `optiloc-hk:dev` — built locally, lives in Docker Desktop's image store (Session 015 will push it to Artifact Registry)

Files IN Git: README.md, JOURNAL.md, CONTEXT.md, **docs/MATH.md**, **docs/ROADMAP.md**, requirements.txt, .gitignore, LICENSE, all `notebooks/*.py` (01–20), the thirteen committed screenshots in `docs/maps/*.png` (the eleven from earlier sessions plus `08_ksweep_diminishing_returns.png` and `09_ksweep_hub_locations.png` from Session 013), `data/raw/.gitkeep`, `data/processed/.gitkeep`, **and as of Session 014: `api/__init__.py`, `api/config.py`, `api/models.py`, `api/solvers.py`, `api/main.py`, `api/requirements.txt`, `.dockerignore`, `Dockerfile`.**

---

*Last updated: end of Session 014 (May 23, 2026). FastAPI + Docker shipped. Eight new files committed under `api/` and repo root. Session 015 (first Cloud Run deploy) is next per ROADMAP Phase 1. Update this file at the end of every session that meaningfully changes project state.*

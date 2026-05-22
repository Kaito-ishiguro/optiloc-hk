# OptiLoc HK — Claude Project Context

> **This file is the canonical handoff. Add it to Project knowledge so every new chat in this Project starts with full context. Update it whenever a session meaningfully changes the project state.**

---

## TL;DR for new chats

OptiLoc HK is a Hong Kong facility location optimizer being built by **Kaito Ishiguro**, a 2nd-year IELM student at HKU. It applies the math from his DASE2135 course (Mathematical Optimization, Spring 2026, Dr. Y.H. Kuo) to real HK demographic data. Public GitHub repo:

**https://github.com/Kaito-ishiguro/optiloc-hk**

**Current phase:** Phase 1 complete, plus eight extensions shipped — Integration #1 (condition number analysis), Sessions 008+009 (Weiszfeld solver + four-solver convergence visualization), Session 010 (ArcGIS / OZP commercial zoning integration), Session 010b (SLSQP buffer-smoothness fix), Session 011 (multi-facility k-median + Voronoi visualization), and **Session 012 (OZP-constrained k-median network with real-world interpretation)**. **Phase 1c+ (multi-facility network optimization, both unconstrained and OZP-constrained) is shipped.** The DASE2135 final exam was on May 11, 2026 (in the past) so no exam pressure. Prof. Kuo has emailed back acknowledging the project and offering UG research collaboration; the reply email with four-solver results was sent at the start of the Session 010 chat. **FWD Group internship starts June 8, 2026 (~2 weeks away as of Session 013 default start).** Kaito is studying for the **Google Cloud Associate Cloud Engineer (ACE) certification** and has ~HKD 2,000 (~USD 255) in free GCP trial credit.

**The immediate pending task at the start of this new chat:** pick the Session 013 direction.

- **(a) k-sweep diminishing returns — DEFAULT.** Solve OZP-constrained k-median for k ∈ {3, 5, 8, 10}, plot objective vs k. Cheap (~1 hour), the natural empirical follow-up to Session 012. Wraps `notebooks/16_solve_kmedian_ozp.py`'s main loop in an outer k-loop, saves a comparison CSV, plots a diminishing-returns curve.
- **(b) Oscillation fix.** 4/10 Session 012 restarts hit `MAX_LLOYD_ITERS=50` without converging, including the winner (restarts 6 and 9 both ended at obj ≈ 277,595 — same basin to 4 sig figs). Likely cause: assignment-vector oscillation around stable facility positions. Either bump max-iters to 100 or add "no objective improvement in N iterations" as secondary convergence. ~30 min. Tidy-up rather than new ground.
- **(c) Phase 1d Session A — Docker + FastAPI wrap.** ~2 hours. The GCP onramp that doesn't need GCP knowledge yet; containerizes the existing solvers and wraps them in an HTTP API with auto-generated Swagger docs at `/docs`. Deliverable is a portable Docker image. Full GCP phasing (see "Phase 1d" section below) puts the Cloud Run deploy at Sessions 015-016, timed for around internship start.
- **(d) Draft the Prof. Kuo follow-up email** with the +1.0% finding as headline. The OZP-constrained k=5 result combines his two suggestions (Weiszfeld + ArcGIS) into one substantive empirical result.

Recommended pick: **(a)** as Session 013, with (c) as Session 014. (b) can be merged into (a) if Kaito wants a clean k-sweep.

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
- He likes **honest engineering feedback over hype**. Tell him when an idea is harder than it looks. Tell him when his instincts are sharp (they often are). Tell him when your prior (the AI's) was wrong — Session 012 surfaced one such case (conditional-invocation runtime savings prediction was wrong).
- **The math-concept-tutor skill** at `/mnt/skills/user/math-concept-tutor/SKILL.md` is the canonical format for any new math concept he asks about. It mandates: real-world hook → visual diagram → concept explanation → vocabulary → connection. Use it. (Confirmed working in Session 011's Lloyd's walkthrough and Session 012's constrained-Weber-as-Lloyd-inner-solver explanation.)
- **Real-world interpretation matters as much as math.** Session 012 spent ~30% of chat time on "what does this map actually mean for a real logistics deployment" — that's not a detour, that's the bridge from coursework to portfolio. When shipping a new result, briefly translate it into deployment terms (avg km per resident, cost penalty in human units, what business use cases this maps to). The math is the value; the interpretation is what makes it sellable.

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

Optional bonus section: **Real-world meaning of the output** — used in Session 012's entry when the session shipped a deployment-relevant result. Include when the math output has a clear business interpretation worth capturing for future reference.

Journal lives in `JOURNAL.md` in the repo root. Source of truth for everything. Notion is just a scratchpad. Each commit message follows the pattern `Session NNN: <short description>`. Combined commits (e.g. `Sessions 010b + 011: ...`) are fine when sessions are tightly coupled, matching the 008+009 precedent.

### After-session debrief

He routinely asks **"don't include this in the file but tell me what we used, how you did it, what tool you used, so I can explain this as if I wasn't just copy-pasting from you."** When he asks this, give a thorough technical explanation outside the journal — tech stack, code architecture, design decisions, the "why this and not that" reasoning, and what specifically came from his own thinking vs scaffolded by Claude.

### Formatting preferences

- Avoid heavy bullets in conversational replies. Use prose by default.
- For structured content (project pitches, tables of options, step-by-step instructions), bullets and tables are fine.
- Math should use LaTeX inline (`$...$`) or display (`$$...$$`).
- He has Claude Pro and Gemini Pro subscriptions and is comfortable with technical detail.
- **Be concise by default.** Going long is a tool, not a default. Reserve depth for when he asks for it or when the conceptual ground genuinely needs it. (Self-correction noted end of Session 012 chat: Claude's longer answers there could have been tighter without quality loss.)

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
- **FWD Group internship** starts June 8, 2026 (~2 weeks away as of Session 013 default start)
- DASE2135 final exam done (May 11, 2026)
- **Currently studying for the Google Cloud Associate Cloud Engineer (ACE) certification** — wants to connect every concept back to OptiLoc. Has ~HKD 2,000 (~USD 255) in free GCP trial credit available.

---

## The project at a glance

OptiLoc's pipeline ingests the WorldPop population raster → derives 41,288 weighted demand points (total population 7,496,988) → solves variants of the Weber facility-location problem (unconstrained, OSM-Kowloon-polygon-constrained, OZP-commercial-constrained) → and k-median network variants (unconstrained, OZP-constrained) → visualizing each as an interactive Folium map. All scripts live in `notebooks/` (files 01–17) following the numbered ordering; each is described in the codebase reference below. Math reference (objectives, gradients, KKT, Weiszfeld, Lloyd) has moved to `docs/MATH.md` in the repo as of Session 012 — Claude can `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md when math grounding is needed mid-session.

---

## Codebase reference — file by file

Every file in `notebooks/` and what it does. Use this as ground truth.

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

**Geographic location:** The optimum is in the **Sham Shui Po / Shek Kip Mei area**, ~1.5 km north of Prince Edward MTR. (Earlier versions of this document mislabeled this as "Mong Kok / Prince Edward MTR" — corrected in Session 010 after visual inspection on a labeled OZP map.) The weighted geometric median is pulled north of urban Kowloon because the New Territories holds >50% of HK's population. This is a real geographic finding, not a bug.

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

**Geographic finding (revised in Session 010 from map inspection):** The OSM polygon labeled "Kowloon" that osmnx returned in this session has its boundary at the **Lion Rock / Beacon Hill ridge**, NOT at Boundary Street as originally documented. The polygon's actual provenance — whether it's the modern Kowloon administrative district, a particular historical boundary, or some OSM-specific tagging — wasn't pinned down at the time and warrants re-investigation. The original Session 005 commentary about "historical Kowloon south of Boundary Street, 1860 lease boundary" appears to have been an assumption that didn't get verified against a labeled map. The constraint binds because the unconstrained Weber center (Sham Shui Po / Shek Kip Mei area, lat 22.337) sits just south of the polygon's boundary, and SLSQP pushes north onto the boundary.

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

**Key insight from Session 008:** Weiszfeld *ties* Newton on wall-clock despite Newton's quadratic convergence rate (4 iterations) vs Weiszfeld's linear rate (23 iterations). Reason: Time = iterations × per-iteration cost. Newton's per-iteration cost is ~6× Weiszfeld's because it computes and factorizes the 2×2 Hessian; Weiszfeld just does one weighted average. **On 2D Weber, the per-iteration cost gap cancels the asymptotic-rate advantage.** Linear convergence with cheap iterations beats quadratic with expensive iterations on small problems. **Sessions 011 and 012 reinforced this empirically across 1000+ sub-solves with zero Weiszfeld failures.**

**Convergence criterion gotcha:** All four solvers in this file use **step-size convergence** ($\|x_{\text{new}} - x\| < \varepsilon$), not gradient-norm convergence. Newton originally hit max_iter=100 chasing floating-point noise in $\|\nabla f\|$ — switching to step-size made Newton report its real iteration count (4). Convergence criteria must be consistent across solvers for benchmarking to be honest.

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

**Output:** `data/processed/ozp_all_zones.geojson` (~120 MB, gitignored). Each feature carries `OBJECTID`, `PLAN_NO`, `ZONE_LABEL`, `DESC_ENG`, `SPUSE_ENG` attributes plus polygon geometry.

**Pagination strategy:** `resultOffset` + `resultRecordCount=2000` (the service's `maxRecordCount`), `orderByFields=OBJECTID` for stable ordering, 60s `timeout`. Six pages total. **Operational warning:** the last page took exactly 60s on the only run we've done, dangerously close to the timeout. Any production / scheduled-job version of this script should use a 120s timeout and add exponential-backoff retry.

**Filter rationale:** the script intentionally caches the FULL dataset (all 157 zoning categories), not just the C+CDA subset. This makes downstream filtering changes (add C/R mixed-use, add Industrial, etc.) free — no re-fetch needed. Mirrors the GCP "Cloud Function -> GCS bucket cache -> downstream consumers" topology.

### `notebooks/11_filter_and_union_ozp.py`

**Purpose (Session 010):** Filter the cached OZP zones to Commercial (C) and Comprehensive Development Area (CDA) categories, union them into a single MultiPolygon, save as a small standalone GeoJSON used as the feasibility region for the constrained Weber and k-median solvers.

**Output:** `data/processed/ozp_commercial_union.geojson` (~1.27 MB, gitignored).

**Filter logic — the "C-prefix trap":** `ZONE_LABEL` has 157 distinct values, and several start with "C" but are not commercial-eligible: `CA` (Conservation Area), `CP` (Country Park), `CPA` (Coastal Protection Area), `C/R` (mixed Commercial/Residential). The filter explicitly disambiguates: accept only exact `C`/`CDA` or labels matching `C(N)` / `CDA(N)`. The parenthesis pattern (commercial sub-zones) cleanly separates the desired categories from the false-positive C-prefixes.

**Empirical result (committed as fact):** 590 features pass the C + CDA filter. After geometric union, the result is a 499-piece MultiPolygon totaling **10.30 km²** = 0.9% of HK's 1,106 km² land area. Hong Kong has remarkably little commercially-zoned land.

**CRS handling:** Area is computed by reprojecting briefly to HK1980 Grid (EPSG:2326, meters) since lat/lon area is mathematically meaningless. The saved geometry stays in WGS84 (EPSG:4326) so downstream solvers don't need to reproject.

### `notebooks/12_solve_constrained_ozp.py`

**Purpose (Sessions 010 + 010b):** Solve the Weber problem subject to the new realistic constraint: optimum must lie inside the C + CDA commercial union. This replaces Session 005's "must be inside the OSM Kowloon polygon" constraint with something ~5× more restrictive and 499× more topologically complex. MTR-proximity and competitor-exclusion constraints from Session 005 are intentionally dropped here — they were inactive in Session 005 anyway (all $\mu_j = 0$), and dropping them isolates the effect of the zoning upgrade.

**Constraint form:** Same signed-distance pattern as Session 005, applied to a 499-piece MultiPolygon. $g(x) > 0$ inside, $g(x) < 0$ outside, $g(x) = 0$ on the boundary. SLSQP's `{'type':'ineq'}` convention is `fun(x) >= 0` = feasible.

**Session 010b — buffer-smoothness fix.** The union geometry is buffered by `1e-6` degrees (~10 cm on the ground) before constructing the constraint:

```python
union_geom = ozp_gdf.iloc[0].geometry.buffer(1e-6)
```

This rounds the 499 polygon corners and merges adjacent-polygon medial-axis kinks at sub-millimeter scale, giving SLSQP's finite-difference Jacobian a smooth gradient to chase. After this fix, SLSQP terminates with **Exit mode 0 in 16 iterations** (was Exit mode 9 / 200 iters in Session 010 before the buffer). Why this works without distorting the problem: the OZP polygon data itself was digitized at meter-scale precision by Lands Department, so a 10 cm round-off is well below the data's noise floor. `trust-constr` fallback was prepared but not needed.

**Output:** `data/processed/ozp_constrained_result.csv` (1-row summary).

**Empirical result (committed as fact):**
- Optimum: **(114.16944, 22.33321)** — Shek Kip Mei, on the boundary of a small C-zoned polygon.
- Constraint value at optimum (post-010b): `g_ozp(x*) ≈ -5.3 × 10⁻¹¹` — sub-millimeter ground distance; optimum is essentially exactly on the boundary.
- Shift from unconstrained: ~474 m southwest.
- Convergence: Exit mode 0, 16 iterations, 44 function evaluations.

### `notebooks/13_visualize_ozp_constrained.py`

**Purpose (Session 010):** The OZP-constrained comparison map. Renders the demand heatmap, the 499 C+CDA polygons as a translucent teal overlay, and three optima markers: unconstrained (gold star), Kowloon-polygon constrained (red dot), OZP-commercial constrained (purple star).

**Output:** `docs/maps/05_ozp_constrained_map.html` + two committed screenshots:
- `docs/maps/ozp_constrained_wide.png`
- `docs/maps/ozp_constrained_zoom.png`

### `notebooks/14_solve_kmedian.py`

**Purpose (Session 011):** Multi-facility k-median solver — the "k facilities for HK" generalization of the single-facility Weber problem from Session 003. Uses Lloyd's algorithm as the outer loop and Weiszfeld (from Session 008) as the inner Weber sub-problem solver.

**Hyperparameters (committed as fact):**
- `K = 5` facilities
- `N_RESTARTS = 10` weighted-random restarts
- `MAX_LLOYD_ITERS = 50`
- Weiszfeld inner: step-size tol `1e-7`, max 100 iters, `EPS = 1e-9` (same as Session 003/008)
- `RNG_SEED = 42` (deterministic)

**Algorithm structure:** Each Lloyd iteration alternates two sub-problems. **Assignment step** — vectorized argmin over an n×k distance matrix; each demand point goes to its nearest facility. **Update step** — Weiszfeld solve per cluster moves the facility to the cluster's weighted Weber center; empty clusters (stranded facilities) are skipped and left in place. Convergence detected when the assignment vector is unchanged between two consecutive iterations. Multi-start: 10 weighted-random inits (sample `K` demand points with probability proportional to weight) — keep the best objective.

**Output:**
- `data/processed/kmedian_result.csv` — 5 rows (final facility positions; columns `facility_id, lon, lat`)
- `data/processed/kmedian_trails.csv` — ~80 rows (winning restart's facility positions at every Lloyd iteration; columns `iter, facility_id, lon, lat`)

**Empirical results (committed as fact):**
- Best objective across 10 restarts: **274,830 weighted-units** — a **59.1% reduction** from the single-facility Weber baseline of 671,466 (Session 003).
- Multi-start found **≥4 distinct local minima** from 10 random inits; **worst-best gap 9.3%** (300,393 vs 274,830).
- Best restart converged in 15 Lloyd iterations; all 10 restarts converged in 14–35 iters (none hit `max_lloyd_iters=50`).
- Total runtime: **5.74s** for ~1000 Weber sub-solves.
- Final 5 facility locations (winning restart):
  - F1: (114.16958, 22.45553) — northern NT (Tai Po area)
  - F2: (114.17428, 22.32082) — central Kowloon
  - F3: (113.99662, 22.43110) — far western NT (Tuen Mun area)
  - F4: (114.11805, 22.36505) — NW NT (Tsuen Wan area)
  - F5: (114.23540, 22.30754) — eastern Kowloon (Kwun Tong area)

**Key empirical finding — non-convexity is real and expensive:** 4+ distinct local minima from 10 random inits is empirical proof that the joint (facilities, assignments) problem is non-convex despite each sub-problem being convex. Multi-start isn't optional on k-median; a one-restart implementation would have shipped a 9% worse answer with no detection.

### `notebooks/15_visualize_kmedian.py`

**Purpose (Session 011):** Folium map of the k=5 k-median network result with Voronoi service-area polygons, convergence trails, and facility markers.

**Voronoi construction:** Uses `shapely.ops.voronoi_diagram` with an HK bounding-box envelope `Polygon([(113.80, 22.15), (114.50, 22.15), (114.50, 22.60), (113.80, 22.60)])` to produce 5 clipped Voronoi cells. **Gotcha:** the diagram's output order is implementation-defined and not guaranteed to match input order, so each output polygon is matched to its facility by a point-in-polygon containment test before rendering. Both `Polygon` and `MultiPolygon` cell types are handled (the latter can occur near the bounding-box clip edge).

**Output:** `docs/maps/06_kmedian_map.html` plus two committed PNG screenshots (`kmedian_map_wide.png`, `kmedian_map_zoom.png`).

### `notebooks/16_solve_kmedian_ozp.py`

**Purpose (Session 012):** OZP-constrained k-median network solver. The compositional session: combines Session 011's Lloyd outer loop with Session 010b's constrained Weber inner solver. Each per-cluster Weber sub-problem is now restricted to the buffered OZP commercial union $\Omega$.

**Inner-solver strategy — conditional invocation:**
1. Run unconstrained Weiszfeld on the cluster (cheap, ~7ms).
2. Test `commercial_union.contains(Point(x_weiszfeld))`.
3. If feasible, keep it. If infeasible, fall back to SLSQP warm-started from the Weiszfeld result.

The conditional was designed to skip the expensive SLSQP call when the unconstrained Weiszfeld center naturally falls on commercial land. **Empirical reality (committed as fact): SLSQP fired on ~100% of Weiszfeld calls** because Kowloon is mostly residential by area; commercial sits in narrow corridors. The conditional logic was right by design (no harm done) but wrong by empirical prediction.

**Hyperparameters:** Same as Session 011 (`K=5`, `N_RESTARTS=10`, `MAX_LLOYD_ITERS=50`, `RNG_SEED=42`) so results are directly comparable. Plus: `BUFFER=1e-6`, `SLSQP_MAXITER=200`, `SLSQP_FTOL=1e-8`.

**Output:**
- `data/processed/kmedian_ozp_result.csv` — 5 rows (final facility positions)
- `data/processed/kmedian_ozp_trails.csv` — winning restart's per-iteration trail
- `data/processed/kmedian_ozp_diagnostics.csv` — per-restart SLSQP-call counts, runtime, convergence flag

**Empirical results (committed as fact):**
- Best objective: **277,595 weighted-units** — only **+1.0% penalty** over Session 011's unconstrained 274,830.
- Translated to ground distance: average HK resident is ~4.0 km from their nearest of 5 facilities (vs ~3.9 km unconstrained, ~9.6 km with one central facility). The OZP constraint costs the average resident about **40 meters** of extra travel.
- Multi-start found **9 distinct local minima** from 10 random inits; worst-best gap **23.1%**. The constraint roughly *doubled* non-convexity vs Session 011 (4+ minima, 9.3% gap).
- Total runtime: **107s** (~20× Session 011's 5.7s, due to ~100% SLSQP-fire rate).
- 4/10 restarts hit `MAX_LLOYD_ITERS=50` without converging, including the winner. Restarts 6 and 9 both ended at obj ≈ 277,595 (4 sig fig agreement across two independent inits — the answer is robust despite non-convergence). Likely cause: assignment-vector oscillation around stable facility positions. Deferred fix.
- Final 5 facility locations (winning restart, restart 9):
  - F1: (114.17897, 22.46065) — northern NT (Tai Po area)
  - F2: (114.11841, 22.36588) — Tsuen Wan / NW NT
  - F3: (114.22888, 22.30993) — eastern Kowloon (Kwun Tong)
  - F4: (114.00015, 22.43523) — Tuen Mun / western NT
  - F5: (114.17211, 22.32086) — central Kowloon

The five facilities are essentially in the same neighborhoods as Session 011's unconstrained answer, just snapped to the nearest commercial polygon boundary. HK's commercial zoning happens to be very well aligned with population distribution — that's what makes the +1% penalty so small.

### `notebooks/17_visualize_kmedian_ozp.py`

**Purpose (Session 012):** Folium map of the OZP-constrained k=5 k-median result with commercial-zone overlay, Voronoi service areas, dashed Lloyd trails, init + final facility markers.

**Layer z-order (bottom to top):** CartoDB Positron base → demand heatmap → OZP commercial union (subtle beige overlay, `#D6B36A` at 22% opacity) → 5 Voronoi service areas (translucent facility colors, `fill_opacity=0.16`) → dashed Lloyd trails per facility → init markers (small hollow circles, radius=6) → final facility markers (large filled circles with dark border, radius=13) → title + legend HTML overlay.

**Color scheme matched to Session 015** (purple/teal/coral/blue/amber) so the constrained and unconstrained maps can be visually cross-referenced.

**Output:** `docs/maps/07_kmedian_ozp_map.html` plus two committed PNG screenshots (`kmedian_ozp_map_wide.png`, `kmedian_ozp_map_zoom.png`).

---

## The math, frozen for reference

Math reference (objectives, gradients, Hessian, Weiszfeld, KKT, k-median, Lloyd, constrained k-median) moved to **`docs/MATH.md`** in the repo as of Session 012. When math grounding is needed mid-session, `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md (or just `view /mnt/project/docs/MATH.md` if added to Project knowledge, though intentionally not added there to keep CONTEXT.md token-efficient).

---

## Tech stack

- **Language:** Python 3
- **Environment:** `venv` at `.venv/`, activated via `.venv\Scripts\Activate.ps1` on Windows
- **Package install:** `python -m pip install -r requirements.txt` (NOT `pip install` — Smart App Control blocks unsigned pip.exe)
- **Numerical:** NumPy (vectorized math, ~1ms per gradient evaluation on 41k points), SciPy (BFGS reference, SLSQP for constrained)
- **Geographic:** rasterio (raster I/O), osmnx (OSM fetching), shapely (polygon distance + union + `shapely.ops.voronoi_diagram` for Voronoi service areas with envelope clipping), GeoPandas (vector I/O), `requests` (raw ArcGIS REST in Session 010 — no Esri SDK)
- **Visualization:** Folium (interactive Leaflet maps), with custom HTML overlays for title/legend
- **Tabular data:** pandas
- **Version control:** Git, public GitHub repo at `github.com/Kaito-ishiguro/optiloc-hk`

**Planned for Phase 1d (Sessions 014–016):**
- FastAPI (HTTP API wrapper around the solvers, with auto-generated Swagger docs at `/docs`)
- Docker (containerize the solvers + FastAPI app)
- GCP: Cloud Run (serverless container hosting in `asia-east2`), Cloud Storage (data assets), Cloud Build (CI from GitHub), Artifact Registry (container image storage), IAM (service accounts)

---

## Environment specifics (Windows quirks)

Kaito is on Windows 11 with PowerShell.

- **Smart App Control was disabled** in Session 002 to allow pandas/rasterio C extensions to load.
- **PowerShell `mkdir -p` doesn't work.** Use comma-separated args.
- **`pip` direct calls can be blocked by SAC.** Always use `python -m pip install ...`
- **`Move-Item` with `-Force`** is needed if the destination file exists.
- **Git on Windows complains about LF→CRLF line endings.** Harmless; ignore.
- **`osmnx` creates a `cache/` folder** in the repo root. Gitignored.
- **Activate venv first** in every new PowerShell session: `cd "C:\Users\Kaito Ishiguro\Documents\optiloc-hk"` then `.venv\Scripts\Activate.ps1`. Look for `(.venv)` in the prompt.
- **Snipping Tool** (`Win+Shift+S`) for screenshots, paste into Paint, save as PNG into `docs/maps/`.
- **For PowerShell one-liner Python with `requests`:** `python -c "import requests; ..."` works fine; double quotes on the outside, single quotes inside the JSON params dict. Don't use multi-line `-c` strings; PowerShell mangles them.

---

## Where we are right now (the immediate state)

**Session 012 is shipped.** Phase 1c+ (multi-facility network optimization, both unconstrained and OZP-constrained) is complete.

The Session 012 wrap-up commit (`8036089`) on `main` carries:
- `notebooks/16_solve_kmedian_ozp.py` (new) — OZP-constrained k-median solver with conditional Weiszfeld→SLSQP inner solver
- `notebooks/17_visualize_kmedian_ozp.py` (new) — Folium map renderer with commercial overlay
- `docs/maps/kmedian_ozp_map_wide.png` + `docs/maps/kmedian_ozp_map_zoom.png` (new screenshots)
- `JOURNAL.md` updated with Session 012 entry (includes the bonus "Real-world meaning of the output" section)

A follow-up commit will carry this updated CONTEXT.md and a new `docs/MATH.md` (extracted from the old CONTEXT.md's math section).

**Headline Session 012 result:** OZP-constrained k=5 k-median best objective 277,595 weighted-units — only **+1.0% penalty** over Session 011's unconstrained 274,830. Translated: restricting facilities to commercially-zoned land costs the average HK resident about 40 meters of extra travel. HK's commercial zoning happens to be very well aligned with population distribution; the constraint barely bites. The deeper finding: the 499-piece disconnected feasible region roughly *doubled* the multi-start non-convexity (9 distinct local minima, 23.1% worst-best gap vs Session 011's 4+ minima, 9.3% gap).

**Session 013 candidates (see TL;DR for full list):** Default is **(a) k-sweep diminishing returns** over k ∈ {3, 5, 8, 10} on the OZP-constrained network. Alternatives are (b) oscillation fix, (c) Phase 1d Session A (Docker + FastAPI wrap — the GCP onramp), and (d) draft the Prof. Kuo follow-up email with the +1% finding.

---

## Phase 1d — GCP deployment (queued, ACE-aligned)

Kaito is studying for the Google Cloud Associate Cloud Engineer cert and has ~HKD 2,000 (~USD 255) in free GCP trial credit. Phase 1d deploys OptiLoc as a public web service on GCP.

**Architecture:** Cloud Build (CI from GitHub) → Artifact Registry (container image storage) → Cloud Run (FastAPI service in `asia-east2`) ← Cloud Storage (demand CSV + OZP GeoJSON assets). Naming: project `optiloc-hk`, bucket `optiloc-hk-data`, Cloud Run service `optiloc-solver`, Artifact Registry repo `optiloc-images`.

**End state:** public HTTPS URL like `https://optiloc-solver-xyz.asia-east2.run.app` serving the OptiLoc solvers as a FastAPI app with auto-generated Swagger docs at `/docs`. Visit URL → interactive API page → click endpoint, tweak parameters, see JSON response with facility positions. Optional Session-017 extension: minimal HTML frontend with a Folium-map response.

**Cost reality:** essentially zero of the HKD 2,000 free trial gets consumed by OptiLoc. Cloud Run free tier (2M req/mo), Cloud Build (120 build-min/day), Artifact Registry (0.5 GB), Cloud Storage free tier all cover portfolio-scale usage. Leaves most of HKD 2,000 trial credit free for poking at other ACE-relevant services on the side (BigQuery, Cloud Functions, Pub/Sub).

**Phasing (agreed end of Session 012 chat):**

- **Session 014: Phase 1d Session A — Docker + FastAPI wrap.** ~2 hours. Containerize existing solvers, wrap in FastAPI with `/solve` endpoint, FastAPI auto-generates Swagger docs at `/docs`. Deliverable: portable Docker image. **No GCP knowledge needed yet.** This is the right "GCP onramp" because it teaches the application-side prep without depending on GCP being set up.
- **Session 015: First GCP deploy.** ~1–2 hours, ACE-aligned (containers, IAM, regions, deployment). Push image to Artifact Registry, deploy Cloud Run service in `asia-east2`, get the live URL.
- **Session 016: Cloud Build CI/CD from GitHub.** ~1–2 hours, ACE-aligned (CI/CD, IAM service accounts, Artifact Registry). Auto-build + auto-deploy on push to `main`.

Sessions 015–016 are timed for just before or during the first week of FWD internship — small focused chunks rather than a multi-session rush against the internship clock. Every concept maps directly to ACE exam topics so study and practice reinforce each other.

Session 010's ArcGIS discovery + pagination + cache pattern is the local-laptop equivalent of the planned Cloud Functions architecture: hit upstream → paginate → write to cache (will become a GCS bucket). The mental model already transfers.

---

## Phase 3 vision (long-term, for context only)

If OptiLoc becomes commercial, the wedge is **logistics network optimization for Asian last-mile players** — Lalamove, SF Express, ZA Tech, HKTVmall, EV charging operators. NOT retail site selection (Placer.ai dominates that space). The Asia wedge is real (no Placer-equivalent in HK / Singapore / Tokyo / Seoul / Bangkok). The math layer (Weber + KKT + k-median + Weiszfeld + realistic zoning constraints) is the moat for selling to ops directors who buy on math credibility. Whether or not it becomes a company, the deeper goal is to keep building OptiLoc as Kaito learns more in class and through internships, until it's a tool he'd genuinely use for HK logistics decisions.

---

## Session history (compressed)

- **Session 001 — Project genesis.** Scoped the project, picked Weber facility location, decided on logistics pivot for Phase 3.
- **Session 002 — WorldPop ingestion pipeline.** Set up Python env (with SAC fix), built the data pipeline, rendered 41k demand points.
- **Session 003 — Hand-rolled solvers.** Derived gradient + Hessian by hand. Implemented GD + Newton + BFGS. Optimum at lat 22.33729, lon 114.17071 — *geographically in the Sham Shui Po / Shek Kip Mei area* (mislabeled as "Mong Kok" in earlier versions of CONTEXT.md; corrected Session 010).
- **Session 004 — Multi-start visualization.** 4 starting points × 2 methods. Added backtracking line search to Newton after singular-Hessian failure.
- **Session 005 — KKT-constrained optimization.** Hand-derived Lagrangian + 4 KKT conditions. Signed-distance constraints. Constrained optimum at (114.17323, 22.34038) — on the boundary of the OSM "Kowloon" polygon, ~444 m **northeast** of unconstrained, at the Beacon Hill / Tai Wo Ping area. Empirical complementary slackness.
- **Session 006 — README + Phase 1 shipped.** Polished README, screenshots, LinkedIn post draft.
- **Session 007 / Integration #1 — Condition number analysis.** $\kappa$ ranges 1.24–3.25 across HK; Weber problem uniformly well-conditioned. Non-quadratic spatial variation in curvature is the real reason GD is slow, not high $\kappa$. Committed alongside Sessions 008+009.
- **CONTEXT.md added** with chat-switch protocol baked in.
- **Email from Prof. Kuo (between sessions).** Acknowledged the project, suggested ArcGIS and Weiszfeld, offered UG research collaboration.
- **Session 008+009 — Weiszfeld + four-solver visualization (commit `0503794`).** Implemented Weiszfeld in ~10 lines. 4-solver comparison; all converge to same optimum to $10^{-9}$ degrees. Weiszfeld ties Newton on wall-clock despite linear vs quadratic rate (per-iter cost dominates iteration count on this problem class). Map attached to Prof. Kuo reply.
- **Email reply to Prof. Kuo sent (start of Session 010 chat).** Four-solver results + commitment to ArcGIS/OZP integration. Note: the email used the phrase "Mong Kok optimum" which is now visibly wrong on a labeled map.
- **Session 010 — ArcGIS / OZP commercial zoning integration (commit `9d8a545`).** Discovered Esri China HK's public ArcGIS REST service via metadata-driven discovery. Fetched all 11,963 OZP polygons, filtered to 590 C + CDA features, unioned into a 499-piece MultiPolygon totaling 10.30 km² (0.9% of HK's land area). Constrained Weber optimum at Shek Kip Mei (114.16944, 22.33321), ~474 m southwest of unconstrained. SLSQP hit maxiter (Exit mode 9) due to non-smooth multi-polygon constraint Jacobian; deferred fix to Session 010b. Also caught a longstanding geographic mislabel — the optima from Sessions 003 and 005 were never in Mong Kok; they're in Sham Shui Po / Shek Kip Mei / Beacon Hill.
- **Session 010b — SLSQP buffer-smoothness fix (combined commit with Session 011).** Added `.buffer(1e-6)` to OZP union in `12_solve_constrained_ozp.py`. SLSQP now terminates with Exit mode 0 in 16 iterations. Same optimum to floating-point precision. ~30 min.
- **Session 011 — k-median network + Voronoi visualization (combined commit with 010b).** Implemented Lloyd + Weiszfeld in `notebooks/14_solve_kmedian.py` (k=5, 10 weighted-random restarts, ~5.74s). Best obj 274,830 = 59.1% reduction from single-facility baseline. Multi-start found ≥4 distinct local minima from 10 inits (9.3% worst-best gap) — empirical proof of non-convexity. `notebooks/15_visualize_kmedian.py` renders Voronoi service areas, dashed convergence trails, facility markers. **Phase 1c (multi-facility network optimization) shipped.**
- **Session 012 — Constrained k-median shipped (commit `8036089`).** Composition session: combined Session 010b's constrained Weber solver with Session 011's Lloyd outer loop. Built `notebooks/16_solve_kmedian_ozp.py` (conditional Weiszfeld→SLSQP inner solver) and `notebooks/17_visualize_kmedian_ozp.py` (commercial overlay + Voronoi map). Best objective 277,595 = **only +1.0% penalty** over unconstrained k=5 — restricting to commercially-zoned land costs the average HK resident ~40 meters of extra travel. The constraint roughly *doubled* non-convexity (9 distinct local minima vs ≥4; 23.1% worst-best gap vs 9.3%). Conditional invocation didn't save runtime as predicted — SLSQP fired on ~100% of Weiszfeld calls because Kowloon is mostly residential by area. 4/10 restarts hit `MAX_LLOYD_ITERS=50` without converging including the winner (restarts 6+9 both ended at obj ≈ 277,595 — robust despite non-convergence; assignment-oscillation hypothesis; deferred fix). Session also surfaced the real-world-interpretation workflow: 5 facilities = logistics network for HK; each is a delivery hub / EV station / retail location / government service center; +1% penalty is the headline business finding (legal commercial-zoned deployment is essentially free vs unconstrained ideal). **Phase 1c+ (constrained multi-facility network optimization) shipped.** This wrap-up commit also extracts the math reference to `docs/MATH.md` and applies the surgical CONTEXT.md trim agreed at end-of-Session-012 chat.

---

## Triggers and protocols

- **"wrap up this session"** or **"log this"** → generate journal entry following the template above, THEN ask the chat-switch question.
- **"let's start session NNN"** → assume Kaito has read this context file and proceed directly into the work.
- **"don't include this in the file but tell me..."** → give thorough technical explanation outside the journal.
- **Terminal commands** → ONE step at a time, wait for "done" or error.
- **New math concept** → use the math-concept-tutor skill at `/mnt/skills/user/math-concept-tutor/SKILL.md` (5-section format with real-world hook → visual → mechanics → vocab → connection).
- **Empirical findings that contradict textbook predictions** → treat as the more interesting result.
- **Optimizer non-convergence or surprising results** → don't smooth them over; visualize, diagnose, and document the failure mode. Sessions 010 (SLSQP maxiter), 011 (multi-start finding 4+ local minima), and 012 (assignment oscillation + ~100% SLSQP-fire rate) all surfaced this way.
- **Real-world deployment-relevant result shipped** → before wrapping, translate the math finding into deployment terms (avg km per resident, cost penalty in human units, business use cases). Add a "Real-world meaning of the output" section to the journal entry.
- **Math grounding needed mid-session** → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md rather than trying to recall from memory.

---

## Files NOT in Git but referenced

- `data/raw/hkg_ppp_2020_UNadj_constrained.tif` — WorldPop GeoTIFF, ~231KB, downloaded from HDX
- `data/processed/*.csv` — all generated outputs (gitignored, regenerable). Includes `kmedian_result.csv` (5 rows), `kmedian_trails.csv` (~80 rows), `kmedian_ozp_result.csv` (5 rows), `kmedian_ozp_trails.csv` (~250 rows for restart 9's 50-iter trail), `kmedian_ozp_diagnostics.csv` (10 rows, one per restart).
- `data/processed/ozp_all_zones.geojson` — ~120 MB cached ArcGIS response (gitignored, regenerable via `10_fetch_ozp.py`; would be rejected by GitHub's 100 MB push limit anyway)
- `data/processed/ozp_commercial_union.geojson` — ~1.27 MB filtered + unioned constraint geometry (gitignored, regenerable via `11_filter_and_union_ozp.py`)
- `docs/maps/*.html` — generated maps (gitignored, regenerable). Includes `06_kmedian_map.html` (Session 011) and `07_kmedian_ozp_map.html` (Session 012).
- `cache/*.json` — osmnx OpenStreetMap cache (gitignored, regenerable)
- `.venv/` — Python virtual environment (gitignored)

Files IN Git: README.md, JOURNAL.md, CONTEXT.md, **docs/MATH.md** (new in Session 012 wrap), requirements.txt, .gitignore, LICENSE, all `notebooks/*.py` (01–17), the eleven committed screenshots in `docs/maps/*.png` (Session 005's two, Session 006's one, Session 008+009's two, Session 010's two, Session 011's two, Session 012's two), `data/raw/.gitkeep`, `data/processed/.gitkeep`.

---

*Last updated: end of Session 012 chat (May 22, 2026). Session 012 shipped the OZP-constrained k-median network solver + visualization (+1.0% penalty headline; 9 distinct local minima from multi-start), completing Phase 1c+. This wrap-up commit also extracts math reference to `docs/MATH.md`, applies a surgical CONTEXT.md trim (ASCII tree removed, math externalized, Phase 1d rewritten with the new Sessions 014–016 GCP phasing, Phase 3 trimmed), and rephases Sessions 013–016 (k-sweep → Docker+FastAPI → GCP deploy → CI/CD). Update this file at the end of every session that meaningfully changes project state.*

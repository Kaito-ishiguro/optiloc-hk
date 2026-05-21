# OptiLoc HK — Claude Project Context

> **This file is the canonical handoff. Add it to Project knowledge so every new chat in this Project starts with full context. Update it whenever a session meaningfully changes the project state.**

---

## TL;DR for new chats

OptiLoc HK is a Hong Kong facility location optimizer being built by **Kaito Ishiguro**, a 2nd-year IELM student at HKU. It applies the math from his DASE2135 course (Mathematical Optimization, Spring 2026, Dr. Y.H. Kuo) to real HK demographic data. Public GitHub repo:

**https://github.com/Kaito-ishiguro/optiloc-hk**

**Current phase:** Phase 1 complete, plus seven extensions shipped — Integration #1 (condition number analysis), Sessions 008+009 (Weiszfeld solver + four-solver convergence visualization), Session 010 (ArcGIS / OZP commercial zoning integration), Session 010b (SLSQP buffer-smoothness fix), and Session 011 (multi-facility k-median with Lloyd's algorithm + Voronoi visualization). **Phase 1c (multi-facility network optimization) is shipped.** The DASE2135 final exam was on **May 11, 2026 (in the past)** so no exam pressure. Prof. Kuo has emailed back acknowledging the project and offering UG research collaboration; the reply email with four-solver results was sent at the start of the Session 010 chat. **FWD Group internship starts June 8, 2026 (~2.5 weeks away).**

**The immediate pending task at the start of this new chat:** pick the Session 012 direction. Three well-scoped candidates. **(a) k-sweep diminishing returns** — solve k-median for k ∈ {3, 5, 8, 10}, plot objective vs k. Cheap (~1 short session); the natural empirical follow-up to Session 011. **(b) k-commercial-hubs** — combine Sessions 010 and 011 by re-introducing the OZP commercial zoning constraint per-cluster (each Lloyd update becomes a constrained Weber sub-solve). More ambitious (~1-2 sessions); the most realistic "real logistics network" framing and the right thing to send Prof. Kuo as a follow-up. **(c) Phase 1d GCP deployment** — containerize as FastAPI, deploy to Cloud Run, tied to ACE cert study. ~3 sessions. The Session 011 journal entry queues (a) as the default; full trade-off in the "Where we are right now" section below.

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
5. Start new chat in the Project with prompt: *"Where are we and what's next?"*

---

## How to work with Kaito

These are non-negotiable working agreements built up across all prior sessions. Honor them in every new chat.

### Step-by-step rhythm for terminal work

When code or PowerShell commands are involved, **give ONE step at a time and wait for him to reply "done" (or paste any errors) before giving the next step**. He explicitly asked for this rhythm because he hits Windows-specific errors and prefers small atomic steps over big chunks of instructions.

Counter-example to avoid: don't write a long "here's everything you need to do" message with 8 numbered terminal commands. Single-step rhythm only.

### Teaching style

- He learns through **visual and interactive examples connecting math to real applications**.
- He likes **full hand-derivations** (chain rule step by step) when learning new math.
- When something fails (gradient descent overshoot, singular Hessian, Newton hitting max_iter from tolerance mismatch, SLSQP hitting maxiter on a non-smooth constraint), **treat the failure as pedagogical**. He values seeing real failure modes more than getting clean answers on the first try.
- He likes **honest engineering feedback over hype**. Tell him when an idea is harder than it looks. Tell him when his instincts are sharp (they often are).
- **The math-concept-tutor skill** at `/mnt/skills/user/math-concept-tutor/SKILL.md` is the canonical format for any new math concept he asks about. It mandates: real-world hook → visual diagram → concept explanation → vocabulary → connection. Use it. (Confirmed working in Session 011's Lloyd's algorithm walkthrough.)

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

Journal lives in `JOURNAL.md` in the repo root. Source of truth for everything. Notion is just a scratchpad. Each commit message follows the pattern `Session NNN: <short description>`. Combined commits (e.g. `Sessions 010b + 011: ...`) are fine when sessions are tightly coupled, matching the 008+009 precedent.

### After-session debrief

He routinely asks **"don't include this in the file but tell me what we used, how you did it, what tool you used, so I can explain this as if I wasn't just copy-pasting from you."** When he asks this, give a thorough technical explanation outside the journal — tech stack, code architecture, design decisions, the "why this and not that" reasoning, and what specifically came from his own thinking vs scaffolded by Claude.

### Formatting preferences

- Avoid heavy bullets in conversational replies. Use prose by default.
- For structured content (project pitches, tables of options, step-by-step instructions), bullets and tables are fine.
- Math should use LaTeX inline (`$...$`) or display (`$$...$$`).
- He has Claude Pro and Gemini Pro subscriptions and is comfortable with technical detail.

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
- **FWD Group internship** starts June 8, 2026 (~2.5 weeks away)
- DASE2135 final exam done (May 11, 2026)
- **Currently studying for the Google Cloud Associate Cloud Engineer (ACE) certification** — wants to connect every concept back to OptiLoc

---

## The project in one diagram

```
WorldPop 2020 GeoTIFF (constrained, UN-adjusted, downloaded from HDX)
       │ rasterio + NumPy mask
       ▼
data/processed/demand_points.csv  (41,288 weighted points; total pop 7,496,988)
       │
       ├─ 02_render_demand_points.py → 01_first_map.html (heatmap)
       │
       ├─ 03_solve_weber.py → solver_results.csv
       │       (Session 003: hand-rolled GD + Newton + BFGS;
       │        all 3 agree to 8 decimals at lat 22.33729, lon 114.17071;
       │        geographically in the Sham Shui Po / Shek Kip Mei area)
       │
       ├─ 03_solve_weber_multi.py → trails_multistart.csv
       │       (Session 004: same math, 4 starting points)
       │       │
       │       └─ 04_visualize_convergence.py → 02_convergence_map.html
       │
       ├─ 05_solve_constrained.py → constrained_result.csv + kkt_multipliers.csv
       │       (Session 005: SLSQP with 7 inequality constraints;
       │        optimum jumps to OSM Kowloon polygon boundary at
       │        Beacon Hill ridge, ~444m northeast of unconstrained)
       │       │
       │       └─ 06_visualize_constrained.py → 03_constrained_map.html
       │
       ├─ 07_condition_number.py  (Integration #1: Hessian analysis at 6 points)
       │       No output file; prints analysis to terminal.
       │
       ├─ 08_solve_weber_weiszfeld.py → solver_comparison.csv + four_solver_trails.csv
       │       (Session 008: Weiszfeld FONC-derived solver + 4-solver race;
       │        all 4 agree to ~7.7e-9 degrees at Shek Kip Mei area)
       │       │
       │       └─ 09_visualize_four_solvers.py → 04_four_solvers_map.html
       │              + four_solvers_wide.png + four_solvers_zoom.png
       │
       ├─ 10_fetch_ozp.py → data/processed/ozp_all_zones.geojson (119.8 MB, gitignored)
       │       (Session 010: paginated ArcGIS REST fetch of all 11,963 OZP polygons)
       │
       ├─ 11_filter_and_union_ozp.py → ozp_commercial_union.geojson (1.27 MB)
       │       (Filter to C + CDA; union 590 polygons into a 499-piece MultiPolygon)
       │
       ├─ 12_solve_constrained_ozp.py → ozp_constrained_result.csv
       │       (Sessions 010 + 010b: SLSQP with the OZP commercial union as the
       │        sole constraint; optimum at Shek Kip Mei (114.16944, 22.33321) on
       │        a C-zoned polygon boundary; .buffer(1e-6) added in 010b gives
       │        Exit mode 0 in 16 iters)
       │       │
       │       └─ 13_visualize_ozp_constrained.py → 05_ozp_constrained_map.html
       │              + ozp_constrained_wide.png + ozp_constrained_zoom.png
       │
       ├─ 14_solve_kmedian.py → kmedian_result.csv + kmedian_trails.csv
       │       (Session 011: Lloyd's algorithm + Weiszfeld inner solver, k=5,
       │        10 weighted-random restarts; best obj 274,830 = 59.1% reduction
       │        vs single-facility; multi-start found 4+ distinct local minima)
       │       │
       │       └─ 15_visualize_kmedian.py → 06_kmedian_map.html
       │              + kmedian_map_wide.png + kmedian_map_zoom.png
       │
       └─ [next: Session 012 — k-sweep, k-commercial-hubs, or Phase 1d GCP]
```

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

**Math:** Derived directly from FONC ($\nabla f = 0$) by algebraic rearrangement:

$$x = \frac{\sum_i w_i x_i / d_i}{\sum_i w_i / d_i}, \quad d_i = \|x - x_i\|$$

Iterating this fixed-point equation gives:

$$\mathbf{x}^{(k+1)} = \frac{\sum_i (w_i / d_i^{(k)}) \mathbf{x}_i}{\sum_i w_i / d_i^{(k)}}$$

**Output:** `data/processed/solver_comparison.csv` (4-row summary), `data/processed/four_solver_trails.csv` (292 trail positions across all 4 solvers).

**Empirical results on 41,288 HK demand points (committed as fact):**
- **Weiszfeld:** 23 iterations, ~7.6ms
- **Newton:** 4 iterations, ~7.2ms
- **BFGS:** 7 iterations, ~5.5ms
- **GD:** 255 iterations, ~55ms
- All four agree on the (Shek Kip Mei area) optimum to within $7.7 \times 10^{-9}$ degrees (sub-millimeter on the ground)

**Key insight from Session 008:** Weiszfeld *ties* Newton on wall-clock despite Newton's quadratic convergence rate (4 iterations) vs Weiszfeld's linear rate (23 iterations). Reason: Time = iterations × per-iteration cost. Newton's per-iteration cost is ~6× Weiszfeld's because it computes and factorizes the 2×2 Hessian; Weiszfeld just does one weighted average. **On 2D Weber, the per-iteration cost gap cancels the asymptotic-rate advantage.** Linear convergence with cheap iterations beats quadratic with expensive iterations on small problems. **Session 011 reinforced this empirically across 1000 sub-solves with zero Weiszfeld failures.**

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

**Purpose (Session 010):** Filter the cached OZP zones to Commercial (C) and Comprehensive Development Area (CDA) categories, union them into a single MultiPolygon, save as a small standalone GeoJSON used as the feasibility region for the constrained Weber solver.

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

**Session 010b also fixed two longstanding geographic mislabels** in the script's print block: "Mong Kok / Prince Edward" → "Sham Shui Po / Shek Kip Mei" (for the Session 003 reference) and "Kowloon historical boundary" → "Beacon Hill ridge (OSM Kowloon polygon)" (for the Session 005 reference). Both match the geographic findings documented in Session 010.

### `notebooks/13_visualize_ozp_constrained.py`

**Purpose (Session 010):** The OZP-constrained comparison map. Renders the demand heatmap, the 499 C+CDA polygons as a translucent teal overlay, and three optima markers: unconstrained (gold star), Kowloon-polygon constrained (red dot), OZP-commercial constrained (purple star).

**Output:** `docs/maps/05_ozp_constrained_map.html` + two committed screenshots:
- `docs/maps/ozp_constrained_wide.png` (HK-wide view showing all 499 commercial polygons + heatmap + 3 markers clustered in Kowloon)
- `docs/maps/ozp_constrained_zoom.png` (close-up showing the three markers between Sham Shui Po and Beacon Hill, with the purple star sitting cleanly on a teal commercial polygon at Shek Kip Mei)

This map was the artifact that exposed the longstanding Mong Kok / Kowloon mislabels — the labeled street view made it immediately obvious that the optima are in the Sham Shui Po / Shek Kip Mei area, not Mong Kok, and that the OSM "Kowloon" polygon's boundary is at the Lion Rock ridge, not Boundary Street.

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
- Multi-start found **≥4 distinct local minima** from 10 random inits; **worst-best gap 9.3%** (300,393 vs 274,830). Restarts 6 and 9 tied for the best basin; restarts 1, 2, 3, 5, 10 found a 280,928 basin; restarts 4, 7, 8 found three other distinct local optima.
- Best restart converged in 15 Lloyd iterations; all 10 restarts converged in 14–35 iters (none hit `max_lloyd_iters=50`).
- Total runtime: **5.74s** for ~1000 Weber sub-solves (10 restarts × ~20 Lloyd iters × 5 Weiszfeld calls).
- Final 5 facility locations (winning restart):
  - F1: (114.16958, 22.45553) — northern NT (Tai Po area)
  - F2: (114.17428, 22.32082) — central Kowloon corridor
  - F3: (113.99662, 22.43110) — far western NT (Tuen Mun area)
  - F4: (114.11805, 22.36505) — NW NT (Tsuen Wan area)
  - F5: (114.23540, 22.30754) — eastern Kowloon (Kwun Tong area)
- The 5 facilities span the territory sensibly: 2 in the dense Kowloon spine, 1 each in western/northern/eastern peripheries.

**Key empirical finding — non-convexity is real and expensive:** 4+ distinct local minima from 10 random inits is empirical proof that the joint (facilities, assignments) problem is non-convex despite each sub-problem being convex. Multi-start isn't optional on k-median; a one-restart implementation would have shipped a 9% worse answer with no detection.

**Why Weiszfeld earned its keep here:** 1000 Weber sub-solves all completed without failure. Newton's per-call speed advantage from Session 008 doesn't matter when even a 0.1% failure rate across this many calls would corrupt the multi-start budget. Linear convergence with cheap, reliable iterations beats quadratic convergence with occasional failures across many calls — exactly the reliability vs raw speed tradeoff Prof. Kuo flagged in his email.

### `notebooks/15_visualize_kmedian.py`

**Purpose (Session 011):** Folium map of the k=5 k-median network result with Voronoi service-area polygons, convergence trails, and facility markers.

**Voronoi construction:** Uses `shapely.ops.voronoi_diagram` with an HK bounding-box envelope `Polygon([(113.80, 22.15), (114.50, 22.15), (114.50, 22.60), (113.80, 22.60)])` to produce 5 clipped Voronoi cells. **Gotcha:** the diagram's output order is implementation-defined and not guaranteed to match input order, so each output polygon is matched to its facility by a point-in-polygon containment test before rendering. Both `Polygon` and `MultiPolygon` cell types are handled (the latter can occur near the bounding-box clip edge).

**Output:** `docs/maps/06_kmedian_map.html` plus two committed PNG screenshots:
- `docs/maps/kmedian_map_wide.png` (HK-wide view; all 5 service areas + full heatmap visible)
- `docs/maps/kmedian_map_zoom.png` (zoom on the dense Kowloon corridor where F2 and F4 sit closest together; shows the Voronoi boundary between them)

**Visual encoding:**
- 5 distinct hex colors: purple `#7F77DD` (F1), teal `#1D9E75` (F2), coral `#D85A30` (F3), blue `#378ADD` (F4), amber `#BA7517` (F5)
- Voronoi cells: translucent fills (`fill_opacity=0.18`) over the heatmap
- Convergence trails: dashed polylines (`dash_array="6, 4"`) from random init to final position
- Init markers: small hollow circles (radius=6)
- Final facility markers: large filled circles with dark border (radius=13)
- Title overlay + legend baked into HTML via `folium.Element`

---

## The math, frozen for reference

### Weber objective

$$f(x, y) = \sum_{i=1}^{n} w_i \cdot d_i(x, y), \quad d_i = \sqrt{(x-x_i)^2 + (y-y_i)^2}$$

### Gradient

$$\nabla f(x, y) = \sum_{i=1}^{n} \frac{w_i}{d_i} \begin{pmatrix} x - x_i \\ y - y_i \end{pmatrix}$$

### Hessian

$$\nabla^2 f(x, y) = \sum_{i=1}^{n} \frac{w_i}{d_i^3} \begin{pmatrix} (y-y_i)^2 & -(x-x_i)(y-y_i) \\ -(x-x_i)(y-y_i) & (x-x_i)^2 \end{pmatrix}$$

Convex (each term is rank-1 PSD; sum of PSD is PSD). Strict PD confirmed empirically in Integration #1.

### Weiszfeld iteration (Session 008)

Derived from FONC ($\nabla f = 0$) by algebraic rearrangement of the gradient equation. The fixed-point form:

$$\mathbf{x}^{(k+1)} = \frac{\sum_i (w_i / d_i^{(k)}) \mathbf{x}_i}{\sum_i w_i / d_i^{(k)}}$$

Each step is a weighted average of demand points using inverse-distance weights $u_i = w_i / d_i^{(k)}$. Closer points pull harder. No step size, no Hessian, no line search.

### Lagrangian + KKT (Session 005)

Standard form: $\min f(x)$ s.t. $g_j(x) \leq 0$.

$$\mathcal{L}(x, \boldsymbol{\mu}) = f(x) + \sum_j \mu_j g_j(x)$$

Four KKT conditions:
1. Stationarity: $\nabla f + \sum_j \mu_j \nabla g_j = 0$
2. Primal feasibility: $g_j(x^*) \leq 0$
3. Dual feasibility: $\mu_j^* \geq 0$
4. Complementary slackness: $\mu_j^* \cdot g_j(x^*) = 0$

In Session 005: $\mu_1 > 0$ on Kowloon polygon (active), $\mu_2 = \mu_{3,\cdot} = 0$ on MTR and competitors (inactive).

### k-median + Lloyd's algorithm (Session 011)

**k-median objective:** find $k$ facility locations $F_1, \ldots, F_k \in \mathbb{R}^2$ and a demand-to-facility assignment $a \in \{1, \ldots, k\}^n$ to minimize total weighted travel:

$$\min_{F_1,\ldots,F_k,\,a} \;\; \sum_{i=1}^{n} w_i \cdot \|x_i - F_{a_i}\|$$

Non-convex in $(F, a)$ jointly (the discrete assignment makes it combinatorial: $k^n$ possible assignments). Lloyd's algorithm decomposes the problem into two convex sub-problems and alternates.

**Assignment step:** $a_i = \arg\min_{j \in \{1, \ldots, k\}} \|x_i - F_j\|$ (vectorized argmin over the $n \times k$ distance matrix).

**Update step (per cluster $C_j = \{i : a_i = j\}$):** $F_j^{(t+1)} = $ Weiszfeld solve on $\{(x_i, w_i) : i \in C_j\}$.

Each step monotonically decreases the total objective. Convergence to a local minimum is guaranteed; the global minimum is not — hence multi-start with random inits. Empirically (Session 011, k=5, 10 weighted-random restarts): 4+ distinct local minima found, with 9.3% worst-best objective gap. **Multi-start is required, not optional.**

---

## Tech stack

- **Language:** Python 3
- **Environment:** `venv` at `.venv/`, activated via `.venv\Scripts\Activate.ps1` on Windows
- **Package install:** `python -m pip install -r requirements.txt` (NOT `pip install` — Smart App Control blocks unsigned pip.exe)
- **Numerical:** NumPy (vectorized math, ~1ms per gradient evaluation on 41k points), SciPy (BFGS reference, SLSQP for constrained)
- **Geographic:** rasterio (raster I/O), osmnx (OSM fetching), shapely (polygon distance + union + `shapely.ops.voronoi_diagram` for Session 011's Voronoi service areas with envelope clipping), GeoPandas (vector I/O), `requests` (raw ArcGIS REST in Session 010 — no Esri SDK)
- **Visualization:** Folium (interactive Leaflet maps), with custom HTML overlays for title/legend
- **Tabular data:** pandas
- **Version control:** Git, public GitHub repo at `github.com/Kaito-ishiguro/optiloc-hk`

**Future-facing (planned, not yet integrated):**
- **Cloud deployment target (GCP):** Cloud Run + Cloud Storage + Cloud Build + Artifact Registry + IAM, in region `asia-east2` (Hong Kong). This is the planned Phase 1d as Kaito's ACE study companion project. Architecture already sketched; not yet implemented. Session 010's "fetch upstream → cache → process from cache" topology is the local-laptop equivalent of the planned cloud architecture.

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

**Session 010b and Session 011 are shipped.** Phase 1c (multi-facility network optimization) is complete.

The combined wrap-up commit on `main` carries:
- `notebooks/12_solve_constrained_ozp.py` — updated with `.buffer(1e-6)` smoothness fix + two geographic label corrections in the print block
- `notebooks/14_solve_kmedian.py` (new) — Lloyd's algorithm + Weiszfeld inner solver for k-median
- `notebooks/15_visualize_kmedian.py` (new) — Voronoi map renderer for the k-median result
- `docs/maps/kmedian_map_wide.png` + `docs/maps/kmedian_map_zoom.png` (new screenshots)
- `JOURNAL.md` updated with Session 010b and Session 011 entries
- `CONTEXT.md` updated with this state (i.e., this file)

**Headline Session 011 result:** best of 10 restarts gave objective 274,830 weighted-units — a 59.1% reduction from the single-facility Weber baseline of 671,466. The 5 facilities span HK from far western NT through central and eastern Kowloon. Multi-start found ≥4 distinct local minima from 10 random inits — empirical proof of non-convexity.

**Three follow-up directions for Session 012:**

### (a) Session 012 — k-sweep diminishing returns (~1 short session)

The cheapest natural follow-up to Session 011. Solve k-median for k ∈ {3, 5, 8, 10}, plot objective vs k, see the diminishing-returns curve. Tests the "going from 1→5 cut 59%; what does 5→10 do?" intuition empirically.

**Implementation:** wrap `14_solve_kmedian.py`'s main loop in an outer loop over k values, save a comparison CSV, plot objective vs k as a line chart. Maybe ~1 hour of work + 30 min write-up.

### (b) Session 012 — k-commercial-hubs (~1-2 sessions)

The more ambitious "real logistics network" framing. Combines Sessions 010 and 011: re-introduce the OZP commercial zoning constraint per-cluster, so each of the k facilities must land on commercially-zoned land. Each Lloyd update step becomes a constrained Weber sub-solve (SLSQP with the OZP commercial union as constraint) instead of unconstrained Weiszfeld.

**Implementation considerations:** Weiszfeld-as-inner-solver becomes SLSQP-as-inner-solver — slower per call AND less reliable across many calls. With 10 restarts × ~15 Lloyd iters × 5 facilities = ~750 constrained sub-solves, even the buffer-smoothed SLSQP from Session 010b might struggle. **Mitigation:** only call SLSQP when the unconstrained Weiszfeld solution falls outside the feasible region (in dense Kowloon, most clusters' weighted centers will be on commercial land anyway). This conditional invocation keeps runtime reasonable.

**Math-wise:** each Lloyd update becomes a KKT-constrained Weber sub-problem. Active set may differ per cluster. The story for Prof. Kuo writes itself: "the OR textbook framing of k-median with linear inequality constraints, applied to HK's 10.30 km² of commercial land."

### (c) Phase 1d — GCP deployment (~3 sessions, ~7-10 hours)

Kaito's ACE study companion project. Containerize the existing solvers as a FastAPI service, deploy to Cloud Run, set up Cloud Build → Artifact Registry pipeline. Architecture already sketched below in the "Phase 1d" section. Not urgent but timely — internship starts June 8, ACE cert study is active.

**Build path:** Session A (Docker + FastAPI wrap), Session B (gcloud setup + first deploy), Session C (Cloud Build automation + custom domain). Each session lands a deployable milestone.

**Recommended pick:** (a) is the right move for one short session before the internship starts. (b) is the right move if Kaito wants to send a follow-up to Prof. Kuo with a substantive new result. (c) is the right move if ACE cert urgency is high.

---

## Phase 1d — GCP deployment (queued, tied to ACE study)

Kaito is studying for the Google Cloud Associate Cloud Engineer cert. The natural project: deploy OptiLoc as a public web service on GCP.

**Architecture (sketched, not implemented):**

```
GitHub repo
     │ (push to main)
     ▼
Cloud Build  ──►  Artifact Registry  (container image storage)
                       │
                       ▼ (deploy new revision)
                  Cloud Run  ◄─►  Cloud Storage  (demand CSV, GeoJSON constraints)
                       ▲
                       │ (HTTP request)
                  User browser  →  https://optiloc-xyz.run.app/solve?...
```

**Naming convention:** project `optiloc-hk`, bucket `optiloc-hk-data`, Cloud Run service `optiloc-solver`, Artifact Registry repo `optiloc-images`, region `asia-east2`.

**Cost:** Free tier covers portfolio-scale traffic; ~$10/year for a custom domain.

**Build path:** ~3 sessions (containerize → FastAPI wrapper → GCP deploy). Realistic 7–10 focused hours total.

**Timing:** Best done summer/fall 2026 alongside ACE study; not urgent.

**Session 010 made this easier.** The ArcGIS discovery + pagination + cache pattern from Session 010 is almost exactly the shape of a Cloud Function consumer: hit upstream → paginate → write to GCS → downstream consumers read from cache. The local `data/processed/ozp_all_zones.geojson` becomes `gs://optiloc-hk-data/raw/ozp_all_zones.geojson` in the cloud version.

---

## Phase 3 vision (long-term, for context only)

If OptiLoc becomes commercial, the wedge is **logistics network optimization for Asian last-mile players** — Lalamove, SF Express, ZA Tech, HKTVmall, EV charging operators. NOT retail site selection (Placer.ai, $1.5B unicorn, would crush a solo founder there).

The Asia wedge is real (no Placer-equivalent in HK/Singapore/Tokyo/Seoul/Bangkok). The math layer (Weber + KKT + k-median + Weiszfeld + realistic zoning constraints) is the moat for selling to ops directors who buy on math credibility, not data partnerships.

Whether or not it becomes a company, the deeper goal is: keep building OptiLoc as Kaito learns more in class and through internships, until it's a tool he'd genuinely use for HK logistics decisions.

---

## Session history (compressed)

- **Session 001 — Project genesis.** Scoped the project, picked Weber facility location, decided on logistics pivot for Phase 3.
- **Session 002 — WorldPop ingestion pipeline.** Set up Python env (with SAC fix), built the data pipeline, rendered 41k demand points.
- **Session 003 — Hand-rolled solvers.** Derived gradient + Hessian by hand. Implemented GD + Newton + BFGS. Optimum at lat 22.33729, lon 114.17071 — *geographically in the Sham Shui Po / Shek Kip Mei area* (this was mislabeled as "Mong Kok / Prince Edward MTR" in earlier versions of CONTEXT.md; the coordinates put it ~1.5 km north of Prince Edward MTR, in the dense urban band that wraps northern Kowloon).
- **Session 004 — Multi-start visualization.** 4 starting points × 2 methods. Added backtracking line search to Newton after singular-Hessian failure.
- **Session 005 — KKT-constrained optimization.** Hand-derived Lagrangian + 4 KKT conditions. Signed-distance constraints. Constrained optimum at (114.17323, 22.34038) — on the boundary of the OSM "Kowloon" polygon, ~444 m **northeast** of the unconstrained answer, geographically at the Beacon Hill / Tai Wo Ping area. Empirical complementary slackness. *Geographic correction in Session 010:* the OSM "Kowloon" polygon's boundary is at the Lion Rock ridge, well north of Boundary Street; exact provenance still warrants re-investigation.
- **Session 006 — README + Phase 1 shipped.** Polished README, screenshots, LinkedIn post draft.
- **Session 007 / Integration #1 — Condition number analysis.** $\kappa$ ranges 1.24–3.25 across HK; Weber problem uniformly well-conditioned. Non-quadratic spatial variation in curvature is the real reason GD is slow, not high $\kappa$. Script committed as commit `6b2276c`, alongside Session 008+009.
- **CONTEXT.md added** with chat-switch protocol baked in.
- **Email from Prof. Kuo (between sessions).** Acknowledged the project, suggested ArcGIS and Weiszfeld, offered UG research collaboration.
- **Session 008+009 — Weiszfeld + four-solver visualization (commit `0503794`).** Implemented Weiszfeld FONC-derived solver in ~10 lines. Built 4-solver comparison from same start; all converge to same optimum to $10^{-9}$ degrees. Key empirical finding: Weiszfeld ties Newton on wall-clock despite linear vs quadratic rate, because per-iteration cost dominates iteration count on this problem class. Built the four-color convergence map (`docs/maps/04_four_solvers_map.html`) with two committed PNG screenshots. Map was attached to the email reply to Prof. Kuo.
- **Email reply to Prof. Kuo sent (start of Session 010 chat).** Four-solver results + commitment to ArcGIS/OZP integration as Session 010. Note: the email used the phrase "Mong Kok optimum" which is now visibly wrong on a labeled map; the truthful correction (if it ever comes up) is "Sham Shui Po / Shek Kip Mei — the NT pulls the centroid north of urban Kowloon."
- **Session 010 — ArcGIS / OZP commercial zoning integration (commit `9d8a545`).** Discovered Esri China HK's public ArcGIS REST feature service via metadata-driven discovery (AGOL sharing API → service URL → layer schema → paginated query). Fetched all 11,963 OZP polygons, filtered to 590 C + CDA features, unioned into a 499-piece MultiPolygon totaling 10.30 km² (0.9% of HK's land area). Constrained Weber optimum at Shek Kip Mei (114.16944, 22.33321), on a C-zoned polygon boundary, ~474 m southwest of the unconstrained answer. SLSQP hit maxiter (Exit mode 9) due to non-smooth multi-polygon constraint Jacobian — result was correct to floating-point precision but lacked formal convergence stamp; deferred fix to Session 010b. The session also caught a longstanding geographic mislabel in CONTEXT.md — the optima from Sessions 003 and 005 were never in Mong Kok as documented; they're in the Sham Shui Po / Shek Kip Mei / Beacon Hill corridor. CONTEXT.md fixed in this wrap-up commit.
- **Session 010b — SLSQP buffer-smoothness fix (combined commit with Session 011).** Added `.buffer(1e-6)` to OZP union in `12_solve_constrained_ozp.py` to smooth the 499-piece MultiPolygon's corner kinks at sub-millimeter scale. SLSQP now terminates with Exit mode 0 in 16 iterations (was Exit mode 9 / 200 iters). Same optimum to floating-point precision; `g_ozp(x*) ≈ -5.3e-11`. Also cleaned up two geographic mislabels in the script's print block (Mong Kok → Sham Shui Po; Kowloon historical boundary → Beacon Hill ridge). ~30 min.
- **Session 011 — k-median network + Voronoi visualization (combined commit with 010b).** Implemented Lloyd's algorithm + Weiszfeld inner solver in `notebooks/14_solve_kmedian.py` (k=5, 10 weighted-random restarts, ~5.74s total). Best objective 274,830 = 59.1% reduction from single-facility baseline (671,466). Multi-start found ≥4 distinct local minima from 10 inits (9.3% worst-best gap) — empirical proof of non-convexity. Wrote `notebooks/15_visualize_kmedian.py` rendering Voronoi service areas (via `shapely.ops.voronoi_diagram`), dashed convergence trails, and facility markers as `docs/maps/06_kmedian_map.html` with two committed PNG screenshots. The 5 facilities span HK: F3 in Tuen Mun, F4 in Tsuen Wan, F1 in Tai Po, F2 in central Kowloon, F5 in Kwun Tong / eastern Kowloon — 2 in the dense spine, 1 in each peripheral region. **Phase 1c (multi-facility network optimization) shipped.** This session also validated the math-concept-tutor skill via the Lloyd's algorithm walkthrough.

---

## Triggers and protocols

- **"wrap up this session"** or **"log this"** → generate journal entry following the template above, THEN ask the chat-switch question.
- **"let's start session NNN"** → assume Kaito has read this context file and proceed directly into the work.
- **"don't include this in the file but tell me..."** → give thorough technical explanation outside the journal.
- **Terminal commands** → ONE step at a time, wait for "done" or error.
- **New math concept** → use the math-concept-tutor skill at `/mnt/skills/user/math-concept-tutor/SKILL.md` (5-section format with real-world hook → visual → mechanics → vocab → connection).
- **Empirical findings that contradict textbook predictions** → treat as the more interesting result.
- **Optimizer non-convergence or surprising results** → don't smooth them over; visualize, diagnose, and document the failure mode. Sessions 010 (SLSQP maxiter) and 011 (multi-start finding 4+ local minima) both surfaced this way.

---

## Files NOT in Git but referenced

- `data/raw/hkg_ppp_2020_UNadj_constrained.tif` — WorldPop GeoTIFF, ~231KB, downloaded from HDX
- `data/processed/*.csv` — all generated outputs (gitignored, regenerable). This includes `kmedian_result.csv` (5 rows) and `kmedian_trails.csv` (~80 rows) from Session 011.
- `data/processed/ozp_all_zones.geojson` — ~120 MB cached ArcGIS response (gitignored, regenerable via `10_fetch_ozp.py`; would be rejected by GitHub's 100 MB push limit anyway)
- `data/processed/ozp_commercial_union.geojson` — ~1.27 MB filtered + unioned constraint geometry (gitignored, regenerable via `11_filter_and_union_ozp.py`)
- `docs/maps/*.html` — generated maps (gitignored, regenerable). This includes `06_kmedian_map.html` from Session 011.
- `cache/*.json` — osmnx OpenStreetMap cache (gitignored, regenerable)
- `.venv/` — Python virtual environment (gitignored)

Files IN Git: README.md, JOURNAL.md, CONTEXT.md, requirements.txt, .gitignore, LICENSE, all `notebooks/*.py` (01–15), the nine committed screenshots in `docs/maps/*.png` (Session 005's two, Session 008+009's two, Session 010's two, Session 011's two, plus the original from Session 006), `data/raw/.gitkeep`, `data/processed/.gitkeep`.

---

*Last updated: end of Session 011 chat (May 21, 2026). Session 010b shipped the SLSQP buffer-smoothness fix; Session 011 shipped the multi-facility k-median solver + Voronoi visualization, completing Phase 1c (multi-facility network optimization). Both sessions were committed in a single combined commit, which also includes this updated CONTEXT.md. Update this file at the end of every session that meaningfully changes project state.*

# OptiLoc HK — Claude Project Context

> **This file is the canonical handoff. Add it to Project knowledge so every new chat in this Project starts with full context. Update it whenever a session meaningfully changes the project state.**

---

## TL;DR for new chats

OptiLoc HK is a Hong Kong facility location optimizer being built by **Kaito Ishiguro**, a 2nd-year IELM student at HKU. It applies the math from his DASE2135 course (Mathematical Optimization, Spring 2026, Dr. Y.H. Kuo) to real HK demographic data. The project is at the public GitHub repo:

**https://github.com/Kaito-ishiguro/optiloc-hk**

**Current phase:** Phase 1 (single-facility unconstrained + KKT-constrained) is shipped. Integration #1 (condition number analysis) is done. **We are paused mid-way through three small "study integrations" for exam prep. Sessions 002–006 + Integration #1 are committed. Integrations #2 and #3 are not yet started.**

**Exam date:** May 11, 2026. **No new math/algorithm work before that date** — only consolidation of existing material. Resume Phase 1c (multi-facility k-median) after May 11.

---

## How to work with Kaito

These are non-negotiable working agreements built up across Sessions 001–007. Honor them in every new chat.

### Step-by-step rhythm for terminal work

When code or PowerShell commands are involved, **give ONE step at a time and wait for him to reply "done" (or paste any errors) before giving the next step**. He explicitly asked for this rhythm because he hits Windows-specific errors and prefers small atomic steps over big chunks of instructions.

Counter-example to avoid: don't write a long "here's everything you need to do" message with 8 numbered terminal commands. Single-step rhythm only.

### Teaching style

- He learns through **visual and interactive examples connecting math to real applications**.
- He likes **full hand-derivations** (chain rule step by step) when learning new math. He explicitly chose this depth in Session 003 (gradient + Hessian) and Session 005 (Lagrangian + KKT).
- When something fails (gradient descent overshoot, singular Hessian, etc.), **treat the failure as pedagogical**. He values seeing real failure modes more than getting clean answers on the first try.
- He likes **honest engineering feedback over hype**. Tell him when an idea is harder than it looks. Tell him when his instincts are sharp (they often are).

### Journaling workflow

At the end of any working session that produces new code or insights, **offer to generate a `JOURNAL.md` entry**. Trigger phrases he uses: *"wrap up this session"* or *"log this"*.

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

Journal lives in `JOURNAL.md` in the repo root. Source of truth for everything. Notion is just a scratchpad. Each commit message follows the pattern `Session NNN: <short description>`.

### After-session debrief

He routinely asks **"don't include this in the file but tell me what we used, how you did it, what tool you used, so I can explain this as if I wasn't just copy-pasting from you."** When he asks this, give a thorough technical explanation outside the journal — tech stack, code architecture, design decisions, the "why this and not that" reasoning, and what specifically came from his own thinking vs scaffolded by Claude. Be honest about both.

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
- Has Claude Pro and Gemini Pro; has FWD Group internship starting June 8, 2026
- Currently taking DASE2135 (Mathematical Optimization, Dr. Y.H. Kuo)
- **Exam: May 11, 2026 (70% of grade)** — protect his study time after this point

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
       │        all 3 agree to 8 decimals at Mong Kok)
       │
       ├─ 03_solve_weber_multi.py → trails_multistart.csv
       │       (Session 004: same math, 4 starting points)
       │       │
       │       └─ 04_visualize_convergence.py → 02_convergence_map.html
       │
       ├─ 05_solve_constrained.py → constrained_result.csv + kkt_multipliers.csv
       │       (Session 005: SLSQP with 7 inequality constraints;
       │        optimum jumps to Kowloon boundary, ~427m southwest)
       │       │
       │       └─ 06_visualize_constrained.py → 03_constrained_map.html
       │
       └─ 07_condition_number.py  (Integration #1: Hessian analysis at 6 points)
              No output file; prints analysis to terminal.
```

---

## Codebase reference — file by file

Every file in `notebooks/` and what it does. Use this as ground truth.

### `notebooks/01_ingest_worldpop.py`

**Purpose:** Convert WorldPop GeoTIFF raster into a flat CSV of demand points.

**Input:** `data/raw/hkg_ppp_2020_UNadj_constrained.tif` (downloaded from HDX; not in Git, gitignored)
**Output:** `data/processed/demand_points.csv` with columns `(lat, lon, weight)`

**Key steps:**
1. `rasterio.open()` the GeoTIFF, extract band 1 (population per cell), affine transform, and CRS
2. Mask out NoData cells (-99999), zero-population cells, and NaN
3. `np.where(mask)` to get row/col indices of populated cells
4. `rasterio.transform.xy()` to convert pixel indices to lat/lon (returns pixel centers, exactly what we want as demand-point coordinates)
5. Defensive bounding-box clip to HK proper (catches any edge artifacts)
6. Save as CSV

**Expected output:** ~41,288 demand points, total weight ~7.5M

### `notebooks/02_render_demand_points.py`

**Purpose:** Visualize the demand points as a HK population heatmap.

**Input:** `data/processed/demand_points.csv`
**Output:** `docs/maps/01_first_map.html`

**Approach:** Folium with HeatMap plugin (KDE-style density) plus top-50 cells as overlay markers for sanity-checking. CartoDB Positron base tiles.

### `notebooks/03_solve_weber.py`

**Purpose:** Solve the unconstrained Weber problem from a single starting point with three methods.

**Input:** `data/processed/demand_points.csv`
**Output:** `data/processed/solver_results.csv`, `trail_gradient_descent.csv`, `trail_newton.csv`

**Three solvers, all vectorized NumPy:**
1. **Gradient descent** with `alpha=1e-9, max_iter=10_000, tol=1e-3` (Session 003 retuned from 1e-7 after divergence)
2. **Newton-Raphson** using `np.linalg.solve(H, -g)` (NOT `inv(H) @ g` — small constant factor, better numerical stability)
3. **SciPy BFGS** as cross-validation reference

**Starting point:** `(114.17, 22.32)` — Victoria Harbour area, near the answer

**Expected result:** All three converge to lon=114.17071, lat=22.33729 to 8 decimal places. Newton in 5 iterations, GD in 255, BFGS in 7.

**Math constants:** `EPS = 1e-9` inside the square root to avoid division by zero at demand points.

### `notebooks/03_solve_weber_multi.py`

**Purpose:** Same math, 4 starting points (Tung Chung, Stanley, Sai Kung, Lok Ma Chau) for the multi-start visualization.

**Input:** `data/processed/demand_points.csv`
**Output:** `data/processed/trails_multistart.csv` (long format: `[start_name, color, method, iter, lon, lat]`)

**Important: Newton uses backtracking line search** here (added in Session 004 to fix the singular-Hessian failure on Tung Chung start). The damping logic:

```python
# After computing step = np.linalg.solve(H, -g):
f_current = objective(p)
alpha = 1.0
for _ in range(30):
    p_trial = p + alpha * step
    if objective(p_trial) < f_current:
        p = p_trial
        break
    alpha *= 0.5
```

Wraps `np.linalg.solve` in `try/except LinAlgError` and breaks loop if Hessian is singular.

### `notebooks/04_visualize_convergence.py`

**Purpose:** The hero map — population heatmap + 8 convergence trails + 4 starting markers + gold optimum star + title + legend baked into HTML.

**Input:** `data/processed/demand_points.csv` + `data/processed/trails_multistart.csv`
**Output:** `docs/maps/02_convergence_map.html`

**Visual encoding decisions:**
- Color = starting point (red Tung Chung, teal Stanley, orange Sai Kung, purple Lok Ma Chau)
- Line style = algorithm (thick solid = Newton, thin dashed = GD)
- Two orthogonal channels (color + style) so the eye can read both independently

### `notebooks/05_solve_constrained.py`

**Purpose:** KKT-constrained Weber problem with 3 real-world constraints (1 Kowloon polygon + 1 MTR proximity + 5 competitor exclusion = 7 inequality constraints total).

**Input:** `data/processed/demand_points.csv`
**Output:** `data/processed/constrained_result.csv`, `constraints_geo.csv`, `kkt_multipliers.csv`

**Method:** SciPy SLSQP (Sequential Least Squares Programming). Fetches Kowloon polygon and all 624 MTR exits live from OSM via `osmnx`. 5 synthetic competitors hard-coded.

**Critical design decision (signed-distance constraints):** All constraints are continuous signed-distance functions in standard `g_j(x) <= 0` form. NOT boolean inside/outside checks. This is Kaito's own insight — he flagged it as worth journaling. Reason: boolean checks make the constraint function flat with cliffs at the boundary; signed distances give the optimizer a smooth gradient pointing toward feasibility.

**Sign convention gotcha:** Textbook math uses `g_j <= 0`. SciPy's `{"type": "ineq", "fun": ...}` expects `fun(x) >= 0`. Each constraint is negated when handed to SLSQP. Math derivations stay in textbook form; only the SciPy interface flips signs.

**Distance-unit conversion:** Constants in meters (500m MTR radius, 200m competitor exclusion) get divided by `M_PER_DEG = 107_000` since coordinates are in degrees at HK's latitude. Phase 2 should reproject to EPSG:2326 (HK 1980 Grid) for metric coordinates.

**Result:** Constrained optimum lands at `(114.17323, 22.34038)` — exactly on the Kowloon polygon boundary, ~427m southwest of the unconstrained Mong Kok answer. The Kowloon constraint is active ($\mu_1 > 0$); MTR and all 5 competitor constraints are inactive. This demonstrates complementary slackness empirically.

**Geographic finding worth remembering:** OSM's "Kowloon" polygon is the **historical** Kowloon (south of Boundary Street, 1860 lease boundary), which is smaller than colloquial modern usage. Hence the constraint binds. MTR constraint is inactive because HK has 624 exits and their 500m proximity zones cover almost all populated areas.

### `notebooks/06_visualize_constrained.py`

**Purpose:** The constrained-result map — heatmap + Kowloon polygon + 624 MTR proximity circles + 5 competitor exclusion zones + both optima + jump line + title + legend.

**Input:** `data/processed/demand_points.csv`, `constrained_result.csv`, `constraints_geo.csv`
**Output:** `docs/maps/03_constrained_map.html`

Two screenshots saved manually:
- `docs/maps/constrained_map_wide.png` (zoomed out, shows MTR network density)
- `docs/maps/constrained_map_zoom.png` (zoomed in, shows red star on Kowloon boundary)

### `notebooks/07_condition_number.py`

**Purpose (Integration #1):** Empirically measure Hessian conditioning across HK to explain *why* gradient descent was 50× slower than Newton.

**Input:** `data/processed/demand_points.csv`
**Output:** Prints analysis tables to terminal; no output file.

**Method:** Evaluate $\nabla^2 f$ at 6 points (optimum + 5 spread across HK), compute eigenvalues, $\kappa$, and $\alpha_{\text{opt}}$ at each.

**Empirical finding (committed as fact for future chats):**
- $\kappa$ ranges 1.24–3.25 across all 6 points: **the Weber problem is uniformly well-conditioned everywhere in HK.**
- $\lambda_{\max}$ varies by 3.4× across space: **the Hessian magnitude is non-constant**, signature of a non-quadratic objective.
- $\alpha_{\text{opt}}$ varies by ~4× across space: **the "right" step size depends on location**.
- Our chosen $\alpha = 10^{-9}$ was 8–45× smaller than optimal at every test point, explaining the 255+ iterations.
- **Lecture 6's textbook "high $\kappa$ ⇒ slow GD" does NOT apply here.** The real reason is non-quadratic spatial variation in curvature. Newton's $H^{-1}$ self-adapts; constant-$\alpha$ GD cannot.

This is exam-grade material. Don't lose it.

---

## The math, frozen for reference

### Weber objective

$$f(x, y) = \sum_{i=1}^{n} w_i \cdot d_i(x, y) \quad \text{where} \quad d_i = \sqrt{(x-x_i)^2 + (y-y_i)^2}$$

### Gradient (hand-derived Session 003 via chain rule)

$$\nabla f(x, y) = \sum_{i=1}^{n} \frac{w_i}{d_i} \begin{pmatrix} x - x_i \\ y - y_i \end{pmatrix}$$

**Geometric meaning:** $\nabla d_i$ is a unit vector pointing from demand point $i$ to the facility. The gradient of any distance function is unit-magnitude — only direction varies.

### Hessian (hand-derived Session 003 via quotient rule)

$$\nabla^2 f(x, y) = \sum_{i=1}^{n} \frac{w_i}{d_i^3} \begin{pmatrix} (y-y_i)^2 & -(x-x_i)(y-y_i) \\ -(x-x_i)(y-y_i) & (x-x_i)^2 \end{pmatrix}$$

**Convexity:** Each term's Hessian is rank-1 PSD (non-negative diagonal, zero determinant). Sum of positively-weighted PSD matrices is PSD. Therefore $f$ is convex. **Strict positive definiteness** confirmed empirically in Integration #1 at 6 points. Symbolic proof of strict PD = Integration #2 (pending).

### Lagrangian + KKT (Session 005)

Standard form: $\min f(x)$ s.t. $g_j(x) \leq 0$.

$$\mathcal{L}(x, \boldsymbol{\mu}) = f(x) + \sum_j \mu_j g_j(x)$$

Four KKT conditions (must all hold at optimum):
1. **Stationarity:** $\nabla f + \sum_j \mu_j \nabla g_j = 0$
2. **Primal feasibility:** $g_j(x^*) \leq 0 \;\forall j$
3. **Dual feasibility:** $\mu_j^* \geq 0 \;\forall j$
4. **Complementary slackness:** $\mu_j^* \cdot g_j(x^*) = 0 \;\forall j$

In OptiLoc: $\mu_1 > 0$ on Kowloon (active), $\mu_2 = \mu_{3,\cdot} = 0$ on MTR and competitors (inactive).

---

## Tech stack

- **Language:** Python 3
- **Environment:** `venv` at `.venv/`, activated via `.venv\Scripts\Activate.ps1` on Windows
- **Package install:** `python -m pip install -r requirements.txt` (NOT just `pip install` — Smart App Control blocks unsigned pip.exe)
- **Numerical:** NumPy (vectorized math, ~1ms per gradient evaluation on 41k points), SciPy (BFGS reference, SLSQP for constrained)
- **Geographic:** rasterio (raster I/O), osmnx (OSM fetching), shapely (polygon distance), GeoPandas (vector I/O)
- **Visualization:** Folium (interactive Leaflet maps), with custom HTML overlays for title/legend
- **Tabular data:** pandas
- **Version control:** Git, public GitHub repo at `github.com/Kaito-ishiguro/optiloc-hk`

---

## Environment specifics (Windows quirks)

Kaito is on Windows 11 with PowerShell. These are landmines hit during the project — future chats should know them.

- **Smart App Control was disabled** in Session 002 to allow pandas/rasterio C extensions to load. Cannot be re-enabled without Windows reset. This is fine and expected for dev work.
- **PowerShell `mkdir -p` doesn't work.** Use comma-separated args: `mkdir data\raw, data\processed, ...`
- **`pip` direct calls can be blocked by SAC.** Always use `python -m pip install ...`
- **`Move-Item` with `-Force`** is needed if the destination file exists; without `-Force` it raises a confusing "Cannot create file when file already exists" error.
- **Git on Windows complains about LF→CRLF line endings.** This is harmless; ignore the warnings.
- **`osmnx` creates a `cache/` folder** in the repo root. Gitignored.
- **Activate venv first** in every new PowerShell session: `cd "C:\Users\Kaito Ishiguro\Documents\optiloc-hk"` then `.venv\Scripts\Activate.ps1`. Look for `(.venv)` in the prompt.

---

## Where we are right now (the immediate state)

**Last committed:** Session 006 (README polish + Phase 1 shipped). Followed by Integration #1 (condition number analysis) — script committed to `notebooks/07_condition_number.py`. Journal entry for Integration #1 NOT yet written.

**What's pending:**

### Integration #2 — Strict convexity proof (NOT STARTED)

**Goal:** Write a short markdown proof (~1 page) in `docs/strict_convexity.md` showing that the Weber Hessian is *strictly* positive definite (not just PSD). This invokes SOSC from Lecture 4 and lets us claim a strict local minimum + global uniqueness.

**Approach:**
1. Start from the rank-1 PSD argument from Session 003 (each $\nabla^2 d_i$ is PSD)
2. Show that *the sum* is strictly PD provided the demand points are not all collinear
3. Argue collinearity is impossible for 41,288 real HK demand points
4. Conclude SOSC holds, strict local min, unique global min by convexity (Lecture 10)
5. Empirically corroborate using the Integration #1 result (both eigenvalues positive at 6 different points)

**Connects to:** Lecture 4 (SOSC), Lecture 10 (convex optimization sufficiency).

### Integration #3 — Contour plot of the objective (NOT STARTED)

**Goal:** Add `notebooks/08_contour_plot.py` that plots level sets of $f(x,y)$ over the HK bounding box. The output should be a matplotlib or Folium overlay showing concentric contours converging on Mong Kok.

**Approach:**
1. Build a 100×100 grid over HK's lat/lon range
2. Evaluate $f(x, y)$ at each grid point (vectorized — should run in seconds, not minutes)
3. Plot contour lines with matplotlib, with the optimum marked
4. Optional: overlay on HK map via Folium with PIL image conversion
5. Save as `docs/maps/04_contour_plot.png`

**Connects to:** Lecture 1 (level sets and contour visualization of multivariable functions).

### Integration #4 — Equality constraint demo (LOW PRIORITY, may skip)

Only attempt if exam prep is going well. Adds pure Lagrange's theorem (no inequalities) to round out Lecture 8 coverage.

---

## After May 11 (exam) — Phase 1c roadmap

Resume with **multi-facility k-median**. Math involves:
- Voronoi assignment (each demand point goes to its nearest facility)
- Alternating optimization (Lloyd's algorithm: assignment step + Weber sub-problem step)
- Non-convexity (joint problem has local optima; need multiple random restarts)
- Beautiful visualization (HK carved into k colored service regions)

Two sessions: Session 008 (solver) + Session 009 (Voronoi visualization). Updates README with Phase 1c results.

---

## Phase 3 vision (long-term, for context only)

If OptiLoc becomes commercial, the wedge is **logistics network optimization for Asian last-mile players** — Lalamove, SF Express, ZA Tech, HKTVmall, EV charging operators. NOT retail site selection (Placer.ai, $1.5B unicorn, would crush a solo founder there).

The Asia wedge is real (no Placer-equivalent in HK/Singapore/Tokyo/Seoul/Bangkok). The math layer (Weber + KKT) is the moat for selling to ops directors who buy on math credibility, not data partnerships.

Whether or not it becomes a company, the deeper goal is: keep building OptiLoc as Kaito learns more in class and through internships, until it's a tool he'd genuinely use for HK logistics decisions.

---

## Session history (compressed)

- **Session 001 — Project genesis.** Scoped the project, picked Weber facility location, decided on logistics pivot for Phase 3 (vs retail site selection).
- **Session 002 — WorldPop ingestion pipeline.** Set up Python env (with SAC fix), researched constrained vs unconstrained datasets, built the data pipeline, rendered 41k demand points.
- **Session 003 — Hand-rolled solvers.** Derived gradient + Hessian by hand. Implemented GD + Newton + BFGS. Found optimum at Prince Edward MTR / Mong Kok. Watched GD diverge with $\alpha = 10^{-7}$, retuned to $10^{-9}$.
- **Session 004 — Multi-start visualization.** 4 starting points × 2 methods = 8 trails, all converging to Mong Kok. Added backtracking line search to Newton after singular-Hessian failure from Tung Chung. First publication-quality artifact.
- **Session 005 — KKT-constrained optimization.** Hand-derived Lagrangian + 4 KKT conditions. Encoded 3 real-world constraints as signed-distance functions. Constrained optimum lands on Kowloon boundary; demonstrated complementary slackness empirically. Found historical-Kowloon-boundary geographic insight.
- **Session 006 — README + Phase 1 shipped.** Polished README, took 3 screenshots, embedded in GitHub. Project is now a defensible portfolio piece. LinkedIn post text drafted; CV bullets drafted.
- **Integration #1 (mid-Session 007) — Condition number analysis.** Measured $\kappa$ and $\lambda_{\max}$ at 6 points. Found "uniformly well-conditioned, magnitude varies 3.4×" — non-quadratic objective is the real reason GD is slow, not high $\kappa$. Script committed; journal entry not yet written.

---

## Triggers and protocols

- **"wrap up this session"** or **"log this"** → generate journal entry following the template above.
- **"let's start session NNN"** → assume Kaito has read this context file and proceed directly into the work.
- **"don't include this in the file but tell me..."** → give thorough technical explanation outside the journal.
- **Terminal commands** → ONE step at a time, wait for "done" or error.
- **New math derivations** → ask first whether he wants full hand-derivation or quick-summary-and-code.
- **Empirical findings that contradict textbook predictions** → treat as the more interesting result; don't paper over.

---

## Files NOT in Git but referenced

- `data/raw/hkg_ppp_2020_UNadj_constrained.tif` — WorldPop GeoTIFF, ~231KB, downloaded from HDX
- `data/processed/*.csv` — all generated outputs (gitignored, regenerable)
- `docs/maps/*.html` — generated maps (gitignored, regenerable)
- `cache/*.json` — osmnx OpenStreetMap cache (gitignored, regenerable)
- `.venv/` — Python virtual environment (gitignored)

Files IN Git: README.md, JOURNAL.md, requirements.txt, .gitignore, LICENSE, all `notebooks/*.py`, the three screenshots in `docs/maps/*.png`, `data/raw/.gitkeep`, `data/processed/.gitkeep`.

---

*Last updated: end of Integration #1 session, mid-Session 007. Update this file at the end of every session that meaningfully changes project state.*

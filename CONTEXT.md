# OptiLoc HK — Claude Project Context

> **This file is the canonical handoff. Add it to Project knowledge so every new chat in this Project starts with full context. Update it whenever a session meaningfully changes the project state.**

---

## TL;DR for new chats

OptiLoc HK is a Hong Kong facility location optimizer being built by **Kaito Ishiguro**, a 2nd-year IELM student at HKU. It applies the math from his DASE2135 course (Mathematical Optimization, Spring 2026, Dr. Y.H. Kuo) to real HK demographic data. Public GitHub repo:

**https://github.com/Kaito-ishiguro/optiloc-hk**

**Current phase:** Phase 1 complete, plus four extensions shipped — Integration #1 (condition number analysis), Sessions 008+009 (Weiszfeld solver + four-solver convergence visualization). The DASE2135 final exam was on **May 11, 2026 (now in the past)** so no time pressure on exam prep. Prof. Kuo has emailed back acknowledging the project and offering UG research collaboration.

**The immediate pending task at the start of this new chat:** reply to Prof. Kuo's email with the four-solver comparison results and a commitment to integrate ArcGIS / Outline Zoning Plans data next.

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
- When something fails (gradient descent overshoot, singular Hessian, Newton hitting max_iter from tolerance mismatch), **treat the failure as pedagogical**. He values seeing real failure modes more than getting clean answers on the first try.
- He likes **honest engineering feedback over hype**. Tell him when an idea is harder than it looks. Tell him when his instincts are sharp (they often are).
- **The math-concept-tutor skill** at `/mnt/skills/user/math-concept-tutor/SKILL.md` is the canonical format for any new math concept he asks about. It mandates: real-world hook → visual diagram → concept explanation → vocabulary → connection. Use it.

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

Journal lives in `JOURNAL.md` in the repo root. Source of truth for everything. Notion is just a scratchpad. Each commit message follows the pattern `Session NNN: <short description>`.

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
- **FWD Group internship** starts June 8, 2026 (~3 weeks away)
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
       ├─ 07_condition_number.py  (Integration #1: Hessian analysis at 6 points)
       │       No output file; prints analysis to terminal.
       │
       ├─ 08_solve_weber_weiszfeld.py → solver_comparison.csv + four_solver_trails.csv
       │       (Session 008: Weiszfeld FONC-derived solver + 4-solver race;
       │        all 4 agree to ~7.7e-9 degrees at Mong Kok)
       │       │
       │       └─ 09_visualize_four_solvers.py → 04_four_solvers_map.html
       │              + four_solvers_wide.png + four_solvers_zoom.png
       │
       └─ [next: 10_visualize_ozp.py or similar — ArcGIS / OZP land use integration]
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

**Math constants:** `EPS = 1e-9` inside the square root to avoid division by zero at demand points.

### `notebooks/03_solve_weber_multi.py`

**Purpose:** Same math, 4 starting points (Tung Chung, Stanley, Sai Kung, Lok Ma Chau) for the multi-start visualization. Newton uses backtracking line search here (added in Session 004 to fix singular-Hessian failure from Tung Chung start).

### `notebooks/04_visualize_convergence.py`

**Purpose:** The Session 004 hero map — population heatmap + 8 convergence trails + 4 starting markers + gold optimum star + title + legend baked into HTML.

**Output:** `docs/maps/02_convergence_map.html`

### `notebooks/05_solve_constrained.py`

**Purpose:** KKT-constrained Weber problem with 7 inequality constraints (1 Kowloon polygon + 1 MTR proximity + 5 competitor exclusion).

**Output:** `data/processed/constrained_result.csv`, `constraints_geo.csv`, `kkt_multipliers.csv`

**Method:** SciPy SLSQP. Fetches Kowloon polygon and all 624 MTR exits live from OSM via `osmnx`.

**Critical design decision (signed-distance constraints):** All constraints are continuous signed-distance functions in standard `g_j(x) <= 0` form. NOT boolean inside/outside checks. Boolean checks make the constraint function flat with cliffs at the boundary; signed distances give the optimizer a smooth gradient pointing toward feasibility.

**Sign convention gotcha:** Textbook math uses `g_j <= 0`. SciPy's `{"type": "ineq", "fun": ...}` expects `fun(x) >= 0`. Each constraint is negated when handed to SLSQP.

**Result:** Constrained optimum at `(114.17323, 22.34038)` — exactly on the Kowloon polygon boundary, ~427m southwest of unconstrained Mong Kok answer. Kowloon constraint active ($\mu_1 > 0$); MTR and 5 competitor constraints inactive. Empirical demo of complementary slackness.

**Geographic finding:** OSM's "Kowloon" polygon is the **historical** Kowloon (south of Boundary Street, 1860 lease boundary), smaller than colloquial modern usage. Hence the constraint binds.

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
- All four agree on the Mong Kok optimum to within $7.7 \times 10^{-9}$ degrees (sub-millimeter on the ground)

**Key insight from Session 008:** Weiszfeld *ties* Newton on wall-clock despite Newton's quadratic convergence rate (4 iterations) vs Weiszfeld's linear rate (23 iterations). Reason: Time = iterations × per-iteration cost. Newton's per-iteration cost is ~6× Weiszfeld's because it computes and factorizes the 2×2 Hessian; Weiszfeld just does one weighted average. **On 2D Weber, the per-iteration cost gap cancels the asymptotic-rate advantage.** Linear convergence with cheap iterations beats quadratic with expensive iterations on small problems.

**Convergence criterion gotcha:** All four solvers in this file use **step-size convergence** ($\|x_{\text{new}} - x\| < \varepsilon$), not gradient-norm convergence. Newton originally hit max_iter=100 chasing floating-point noise in $\|\nabla f\|$ — switching to step-size made Newton report its real iteration count (4). Convergence criteria must be consistent across solvers for benchmarking to be honest.

### `notebooks/09_visualize_four_solvers.py`

**Purpose (Session 009):** The four-solver convergence map. Reads `four_solver_trails.csv` and renders a Folium map with all four convergence trails color-coded.

**Output:** `docs/maps/04_four_solvers_map.html` + two committed screenshots:
- `docs/maps/four_solvers_wide.png` (zoomed out, shows journey from Victoria Harbour to Mong Kok with all 4 trails)
- `docs/maps/four_solvers_zoom.png` (zoomed in on Mong Kok, shows all 4 trails converging to gold star)

**Visual encoding:**
- **Weiszfeld** = purple thick solid (the star of the show)
- **Newton** = red thin solid (only 4 segments — short)
- **BFGS** = teal dashed (7 segments — medium)
- **GD** = gray thin dashed (255 segments — the long worm)

These screenshots are the artifact going to Prof. Kuo in the email reply.

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

In OptiLoc: $\mu_1 > 0$ on Kowloon (active), $\mu_2 = \mu_{3,\cdot} = 0$ on MTR and competitors (inactive).

---

## Tech stack

- **Language:** Python 3
- **Environment:** `venv` at `.venv/`, activated via `.venv\Scripts\Activate.ps1` on Windows
- **Package install:** `python -m pip install -r requirements.txt` (NOT `pip install` — Smart App Control blocks unsigned pip.exe)
- **Numerical:** NumPy (vectorized math, ~1ms per gradient evaluation on 41k points), SciPy (BFGS reference, SLSQP for constrained)
- **Geographic:** rasterio (raster I/O), osmnx (OSM fetching), shapely (polygon distance), GeoPandas (vector I/O)
- **Visualization:** Folium (interactive Leaflet maps), with custom HTML overlays for title/legend
- **Tabular data:** pandas
- **Version control:** Git, public GitHub repo at `github.com/Kaito-ishiguro/optiloc-hk`

**Future-facing (planned, not yet integrated):**
- **Cloud deployment target (GCP):** Cloud Run + Cloud Storage + Cloud Build + Artifact Registry + IAM, in region `asia-east2` (Hong Kong). This is the planned Phase 1d as Kaito's ACE study companion project. Architecture already sketched; not yet implemented.

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

---

## Where we are right now (the immediate state)

**Last committed and pushed:**
- Commit `0503794` — Session 008+009: Weiszfeld + four-solver visualization (4 files: 2 Python scripts, 2 PNG screenshots)
- Commit `6b2276c` — Integration #1: condition number script (belated commit from Session 007)
- Plus the JOURNAL.md entry for Session 008+009 should have been committed at the very end of the previous chat — verify with `git log --oneline -5` if uncertain.

**The pending action at the start of the new chat: reply to Prof. Kuo's email.**

### Prof. Kuo's email (full text, for context)

> Dear Kaito, Sorry for the late reply. Have been busy with the semester. Glad to know that you used some ideas and materials from the course. :)
>
> Not sure if you have explored GIS systems, such as ArcGIS: https://opendata.esrichina.hk/maps/fd2bb4e9132446ee8b06dae1f4e35d2e? These are useful tools for your research.
>
> Regarding the specific Weber's problem you considered, actually there is an algorithm, Weiszfeld Algorithm, to solve it: https://medium.com/@himanshu.sharma.for.work/optimal-geometric-location-using-the-weiszfeld-algorithm-d7fd6229da7c. Interestingly, this algorithm was developed based on the first-order necessary condition (FONC) you learned in DASE 2135.
>
> Am happy to work with UG students. The only condition is that I need the UG student to be self-motivated and very committed. Not sure if how much time you can allocation to research? I do not some UG students to help with GIS systems and location optimization models.
>
> Thanks.

### Three things in that email worth keeping straight

1. **A research offer is on the table.** Filter is "self-motivated and very committed." The fact that Weiszfeld is implemented + visualized + committed *before* the reply is itself the demonstration of the trait.
2. **The Weiszfeld suggestion is now done.** Reply with real numbers: 23 iterations, 7.6ms, agreement to $10^{-9}$ degrees, four-solver comparison table, two screenshots.
3. **The ArcGIS / OZP suggestion is queued as Session 010** — promise it in the reply, don't claim it's done yet. The specific dataset he linked is "Hong Kong Outline Zoning Plans Land Use Zonings" — broad categories (Commercial, Residential, Open Space, GIC, etc.). Plan is to download the OZP shapefile, filter to Commercial (C) + Comprehensive Development Area (CDA), use union of those polygons as the constraint instead of the coarse Kowloon polygon.

### Draft email reply (built up in prior chat — adapt to Kaito's voice)

```
Dear Dr. Kuo,

Thank you for getting back, and no worries about the timing.

Both pointers were genuinely valuable, so I wanted to act on them
before replying rather than just acknowledging.

The Weiszfeld algorithm was a real gap in my project — I had built
gradient descent, Newton-Raphson, and BFGS for the Weber problem
in March, but somehow missed the classical FONC-derived method.
I derived it from ∇f = 0 (rearranging into the fixed-point form
x = Σ(w_i x_i / d_i) / Σ(w_i / d_i)), implemented it, and ran a
four-solver comparison from the same Victoria Harbour starting
point on all 41,288 HK demand points.

Results:
- Weiszfeld:  23 iterations,  ~7.6ms
- Newton:      4 iterations,  ~7.2ms
- BFGS:        7 iterations,  ~5.5ms
- GD:        255 iterations,  ~55ms

All four converge to the same Mong Kok optimum to within 1e-9
degrees (sub-millimeter on the ground). What was unexpected:
Weiszfeld ties Newton on wall-clock despite Newton's quadratic
convergence rate, because Weiszfeld's per-iteration cost (one
weighted average) is ~6× cheaper than Newton's (Hessian solve).
Linear convergence with cheap iterations beats quadratic
convergence with expensive iterations on this 2D problem.

I've attached two screenshots showing all four convergence trails
on the HK heatmap. The script is at notebooks/08_solve_weber_weiszfeld.py
in my repo, and the four-solver map at notebooks/09_visualize_four_solvers.py.

I also opened the Esri China HK link. The Outline Zoning Plans
dataset is exactly what my current KKT formulation is missing —
my "must be inside Kowloon polygon" constraint is too coarse to be
realistic, since a facility actually needs commercially-zoned land
specifically. I'm planning to integrate the OZP shapefile as my
next step (Session 010), filtering to Commercial (C) and
Comprehensive Development Area (CDA) zones, so the constraint
becomes "must be in C or CDA zoning." That should produce a much
more meaningful constrained optimum than my current historical-
Kowloon-polygon version.

Regarding the UG research offer — I'm genuinely interested. Two
things worth being upfront about on time:

- Summer 2026 (from June 8): I'll be at a full-time FWD Group
  internship, so research bandwidth during the summer will be
  limited.
- Fall 2026 onward (start of my 3rd year): I can commit roughly
  10–15 hours per week to research alongside coursework.

If that profile fits, I'd love to chat about what projects you
have in mind. Location optimization is the obvious overlap with
what I'm already doing, but I'd be glad to hear what else is on
your roadmap.

The updated repo is here if you'd like to see what I've been
working on:
https://github.com/Kaito-ishiguro/optiloc-hk

Happy to come by office hours once finals are settled, or to meet
over Zoom if that's easier.

Thank you again,

Kaito Ishiguro
BEng IELM, HKU Class of 2028
```

### What to attach to the email

- `docs/maps/four_solvers_wide.png`
- `docs/maps/four_solvers_zoom.png`

---

## Session 010 — ArcGIS / OZP integration (queued)

Once the professor email is sent, the natural next session is integrating the Esri China HK Outline Zoning Plans dataset.

**Goal:** Replace the coarse "must be inside Kowloon polygon" constraint with the realistic "must be in commercially-zoned land" constraint.

**Approach:**
1. Download the OZP shapefile (or query via ArcGIS REST API) from Esri China HK
2. Load with `geopandas.read_file()`
3. Filter to zoning codes for Commercial (C), Comprehensive Development Area (CDA), and possibly Industrial (I) depending on facility type
4. Union into a single MultiPolygon
5. Use as drop-in replacement for the Kowloon polygon in `05_solve_constrained.py`
6. Re-render the constrained map showing OZP zones underneath
7. Compare new constrained optimum to old (Mong Kok boundary)

**Connects to:** Lecture 8 (constrained optimization), and lays the groundwork for the GCP-deployed version where these constraints would be stored as GeoJSON in Cloud Storage.

**Realistic time:** 4–6 hours. Most of the time is data wrangling, not math.

---

## After Session 010 — Phase 1c roadmap (multi-facility k-median)

Exam is done; Phase 1c is now unblocked. Multi-facility k-median involves:
- Voronoi assignment (each demand point goes to its nearest facility)
- Alternating optimization (Lloyd's algorithm: assignment + Weber sub-problem per facility)
- Non-convexity (joint problem has local optima; need multiple random restarts)
- **This is where Weiszfeld earns its keep.** In a 500-solve loop (k=10 facilities × 50 iterations), Newton's occasional failures would compound. Weiszfeld has no failure modes; it's the natural choice.

Two sessions: solver (Session 011) + Voronoi visualization (Session 012).

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

---

## Phase 3 vision (long-term, for context only)

If OptiLoc becomes commercial, the wedge is **logistics network optimization for Asian last-mile players** — Lalamove, SF Express, ZA Tech, HKTVmall, EV charging operators. NOT retail site selection (Placer.ai, $1.5B unicorn, would crush a solo founder there).

The Asia wedge is real (no Placer-equivalent in HK/Singapore/Tokyo/Seoul/Bangkok). The math layer (Weber + KKT + k-median + Weiszfeld) is the moat for selling to ops directors who buy on math credibility, not data partnerships.

Whether or not it becomes a company, the deeper goal is: keep building OptiLoc as Kaito learns more in class and through internships, until it's a tool he'd genuinely use for HK logistics decisions.

---

## Session history (compressed)

- **Session 001 — Project genesis.** Scoped the project, picked Weber facility location, decided on logistics pivot for Phase 3.
- **Session 002 — WorldPop ingestion pipeline.** Set up Python env (with SAC fix), built the data pipeline, rendered 41k demand points.
- **Session 003 — Hand-rolled solvers.** Derived gradient + Hessian by hand. Implemented GD + Newton + BFGS. Optimum at Prince Edward MTR / Mong Kok.
- **Session 004 — Multi-start visualization.** 4 starting points × 2 methods. Added backtracking line search to Newton after singular-Hessian failure.
- **Session 005 — KKT-constrained optimization.** Hand-derived Lagrangian + 4 KKT conditions. Signed-distance constraints. Constrained optimum on Kowloon boundary; empirical complementary slackness.
- **Session 006 — README + Phase 1 shipped.** Polished README, screenshots, LinkedIn post draft.
- **Session 007 / Integration #1 — Condition number analysis.** $\kappa$ ranges 1.24–3.25 across HK; Weber problem uniformly well-conditioned. Non-quadratic spatial variation in curvature is the real reason GD is slow, not high $\kappa$. Script committed (eventually as commit `6b2276c`, alongside Session 008+009).
- **CONTEXT.md added** with chat-switch protocol baked in.
- **Email from Prof. Kuo (between sessions).** Acknowledged the project, suggested ArcGIS and Weiszfeld, offered UG research collaboration.
- **Session 008+009 — Weiszfeld + four-solver visualization (commit `0503794`).** Implemented Weiszfeld FONC-derived solver in ~10 lines. Built 4-solver comparison from same start; all converge to same optimum to $10^{-9}$ degrees. Key empirical finding: Weiszfeld ties Newton on wall-clock despite linear vs quadratic rate, because per-iteration cost dominates iteration count on this problem class. Built the four-color convergence map (`docs/maps/04_four_solvers_map.html`) with two committed PNG screenshots. Map is the artifact going to Prof. Kuo.
- **CONTEXT.md updated mid-Session 010** to capture Session 008+009 state and the pending email reply.

---

## Triggers and protocols

- **"wrap up this session"** or **"log this"** → generate journal entry following the template above, THEN ask the chat-switch question.
- **"let's start session NNN"** → assume Kaito has read this context file and proceed directly into the work.
- **"don't include this in the file but tell me..."** → give thorough technical explanation outside the journal.
- **Terminal commands** → ONE step at a time, wait for "done" or error.
- **New math concept** → use the math-concept-tutor skill at `/mnt/skills/user/math-concept-tutor/SKILL.md` (5-section format with real-world hook → visual → mechanics → vocab → connection).
- **Empirical findings that contradict textbook predictions** → treat as the more interesting result.

---

## Files NOT in Git but referenced

- `data/raw/hkg_ppp_2020_UNadj_constrained.tif` — WorldPop GeoTIFF, ~231KB, downloaded from HDX
- `data/processed/*.csv` — all generated outputs (gitignored, regenerable)
- `docs/maps/*.html` — generated maps (gitignored, regenerable)
- `cache/*.json` — osmnx OpenStreetMap cache (gitignored, regenerable)
- `.venv/` — Python virtual environment (gitignored)

Files IN Git: README.md, JOURNAL.md, CONTEXT.md, requirements.txt, .gitignore, LICENSE, all `notebooks/*.py` (now includes 07, 08, 09), the five committed screenshots in `docs/maps/*.png` (Session 005's two, Session 009's two, plus the original from Session 006), `data/raw/.gitkeep`, `data/processed/.gitkeep`.

---

*Last updated: end of Session 008+009 chat (May 20, 2026). Update this file at the end of every session that meaningfully changes project state.*
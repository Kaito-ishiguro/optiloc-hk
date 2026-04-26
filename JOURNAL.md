# OptiLoc HK — Build Journal

A dated log of what I built, what I learned, what I got stuck on, and what I'm doing next. Written for myself, kept public so I can't quietly rewrite history.

---

## Session 001 — 2026-04-26 — Project Genesis & Strategic Positioning

**What I built / learned**

- Selected the Phase 1 project: **OptiLoc HK** — an interactive Weber facility location optimizer for Hong Kong, applying multivariable optimization theory from DASE2135 to a real urban logistics problem.
- Mapped every concept from the current syllabus (multivariable functions, partial derivatives, unconstrained NLP, gradient descent, Newton-Raphson, KKT conditions for the constrained version) onto a single objective function:

  $$f(x, y) = \sum_{i=1}^{n} w_i \cdot \sqrt{(x - x_i)^2 + (y - y_i)^2}$$

  Plan: derive the gradient and Hessian by hand, implement gradient descent and Newton-Raphson from scratch, benchmark them against `scipy.optimize`, then add equality and inequality constraints to flex KKT.
- Confirmed full data feasibility on free sources only: HK Census 2021 at Tertiary Planning Unit (TPU) level for demand weights from `data.gov.hk`, OpenStreetMap via `osmnx` for road network and POIs, HK GeoData Store for forbidden-zone polygons (parks, water).
- Decided the tech stack: NumPy + SciPy for solvers, Pandas for data wrangling, Folium for the HK map visualization, Streamlit (or React/TypeScript later) for the frontend.

**Key insight or aha moment**

The biggest reframe wasn't technical — it was about positioning. I initially imagined Phase 3 as "Placer.ai for Asia" — a retail site selection SaaS. A competitive analysis killed that cleanly: Placer.ai is a $1.5B unicorn with $268M raised and 50+ data partnerships. A solo undergraduate cannot win that fight head-on. The smarter pivot keeps the same Weber/KKT math but changes the wedge — **logistics network optimization for Asian last-mile players (Lalamove, SF Express), micro-fulfillment placement, EV charging station siting**. These markets align with my IELM degree, have weaker incumbents, and customers buy on math credibility rather than data partnerships I can't get. Phase 1 build stays identical; only the Phase 3 narrative shifted.

Second insight: most "location intelligence" tools are dashboards (foot traffic + demographics) and let humans pick. They are not optimizers. The mathematical optimization angle is genuinely underserved — but the reason isn't that nobody thought of it. It's that real customers want messy decision support, not clean coordinates. Useful constraint to remember when designing the product.

**What I got stuck on**

I pushed back hard on whether the data layer was achievable for a solo student. Initial worry: population density, real estate prices, and foot traffic feeds would all require paid APIs or partnerships. Resolution after some research: Phase 1 only needs *demand weights + 2D geometry*, both of which are completely free from `data.gov.hk` and OpenStreetMap. Real estate prices and foot traffic are deferred to Phase 3, where they become the moat anyway, not blockers. The lesson: I had confused Phase 3's data requirements with Phase 1's. Worth remembering — every time I think the project is impossible, it's probably because I'm scoping the wrong phase.

**Next session's first move**

Set up the public GitHub repo `optiloc-hk` with this `JOURNAL.md` and the `README.md` skeleton committed. Then pull the HK Census 2021 TPU population data + boundary shapefile from `data.gov.hk`. Goal by end of next session: ~300 weighted demand points plotted on a Folium map of HK. Once I see the dots, the project becomes real.

**Time spent / mood**

~1.5hrs of strategic conversation with Claude, no code yet. Ended energised — went from "vague cool idea" to "specific, scoped plan with a defensible Phase 3 pivot." The competitive analysis was bracing but useful: better to know now than after building the wrong thing.

---
## Session 002 — 2026-04-26 — WorldPop Ingestion Pipeline

**What I built / learned**

- Set up the full Python data-science toolchain on Windows: virtual environment (`.venv`), `requirements.txt` with pinned versions, `pip` install of GeoPandas, Folium, Rasterio, NumPy, Pandas, and Shapely. Resolved Windows 11 Smart App Control blocking the unsigned `pip.exe` and pandas C-extension DLLs by disabling SAC (one-way trade-off worth understanding for a Windows dev environment).
- Built a two-stage data pipeline: `01_ingest_worldpop.py` reads a 100m gridded GeoTIFF raster and produces a flat `demand_points.csv` of `(lat, lon, weight)` tuples; `02_render_demand_points.py` renders that CSV as an interactive Folium heatmap of HK with the top-50 most populated cells overlaid as markers.
- Used `rasterio` to load the GeoTIFF, mask out NoData and zero-population cells, convert pixel row/col indices to lat/lon centroids using `rasterio.transform.xy`, and output a clean dataframe.
- Final result: 41,288 weighted demand points covering populated areas of HK, total population 7,496,988 — within rounding of HK's actual 2020 figure, which validates the entire pipeline.

**Key insight or aha moment**

The biggest learning was about data methodology, not code. Initially planned to use HK Census 2021 Tertiary Planning Unit centroids (211 polygons, one weight per polygon), but research surfaced the **centroid trap**: collapsing a 5km² zone with 50,000 people into one coordinate creates massive spatial distortion, especially in HK where TPU centroids often fall on hilltops or in water due to irregular polygon shapes.

Switched to WorldPop 100m gridded data — but the deeper choice was between **unconstrained** and **constrained** versions. WorldPop's algorithm disaggregates census totals across satellite-derived covariates. Unconstrained spreads small fractional populations across every pixel including parks and mountains; constrained applies a hard mask that zeroes out non-built-up pixels before disaggregation. For HK specifically — where ~40% of land area is country parks — constrained is dramatically more correct. Used `hkg_ppp_2020_UNadj_constrained.tif`: constrained mask + UN-adjusted total. The interview answer: "Constrained because 40% of HK is country parks; UN-adjusted so my total matches the official 7.5M figure."

The map confirms it visually: the central country park belt, Lantau interior, and Victoria Peak area are completely dark on the heatmap. Hot spots correctly cluster in Mong Kok / Sham Shui Po / Kwun Tong / Tin Shui Wai — not in Central, because Central is offices, not housing. The data is reflecting HK's real demographic geography.

**What I got stuck on**

- **Windows Smart App Control** blocked freshly installed `pip.exe` (unsigned executable). Workaround was `python -m pip install` (calls signed `python.exe` which loads pip as a module). Then SAC blocked pandas C-extension DLL load on import. Resolved by disabling SAC entirely — irreversible without a Windows reset, but standard for dev environments.
- **PowerShell vs Unix mkdir syntax** — `mkdir -p` doesn't work on Windows; PowerShell uses comma-separated arguments and backslashes. Small but cost time to figure out.
- **Wrong dataset variant downloaded twice** — first grabbed unconstrained, then realized the methodological argument required constrained. HDX has four variants of the HK file (with/without UN-adjustment × constrained/unconstrained); easy to grab the wrong one if not paying attention. The naming convention `hkg_ppp_2020_<UNadj_>?<constrained_>?.tif` is now memorized.
- **`pip install -r requirements.txt` didn't install rasterio silently** — likely because it failed during a previous attempt and pip cached the failure. Direct `python -m pip install rasterio` worked fine.

**Next session's first move**

Start Session 003: derive the gradient and Hessian of the Weber objective $f(x,y) = \sum w_i \sqrt{(x-x_i)^2 + (y-y_i)^2}$ by hand, then implement gradient descent from scratch on the 41,288 demand points. First milestone: see the algorithm converge from a random starting point to a sensible optimum — should land somewhere in the West Kowloon / Mong Kok area since that's the population center of mass of HK. Compare convergence speed against `scipy.optimize.minimize` with BFGS as a sanity baseline.

**Time spent / mood**

~3 hours including environment setup, debugging SAC blocks, dataset research, and final visualization. Mood: high. The map is the first visual artifact of the project that looks like a real engineering output. Going from "vague optimization idea" to "41,288 verified weighted demand points covering all of populated HK" in two sessions feels like genuine momentum.

---
## Session 003 — 2026-04-26 — Hand-Rolled Solvers Land on Mong Kok

**What I built / learned**

- Derived the gradient $\nabla f$ and Hessian $\nabla^2 f$ of the Weber objective $f(x,y) = \sum_i w_i \sqrt{(x-x_i)^2 + (y-y_i)^2}$ by hand, using the chain rule on the square root and the quotient rule on the resulting fractions. Proved $f$ is convex by showing each term's Hessian is positive semi-definite (rank 1, non-negative diagonal, zero determinant), which guarantees a unique global minimum.
- Implemented three solvers from scratch in NumPy on the 41,288 demand points: gradient descent ($\mathbf{x}_{k+1} = \mathbf{x}_k - \alpha \nabla f$), Newton-Raphson (solving $\nabla^2 f \cdot \mathbf{p} = -\nabla f$ for the step), and a SciPy BFGS reference for cross-validation. All three converged to the same optimum to 8 decimal places.
- Used `np.linalg.solve(H, -g)` instead of computing $H^{-1}$ explicitly. For 2×2 the saving is negligible, but the constant factor is 2-3× smaller, the result is more numerically stable (LU decomposition with pivoting handles ill-conditioning), and the habit transfers to Phase 3 where multi-facility k-median problems will have hundreds-by-hundreds Hessians and the choice will start mattering.
- **The optimum: lon=114.17071, lat=22.33729 — Prince Edward MTR / Mong Kok East.** The densest residential corridor in Kowloon. Total weighted distance at this point: 670,587 (degree units), roughly 74 million person-kilometers. This is the absolute lower bound on average travel distance for any single-facility placement serving HK's 7.5M population.
- Vectorized every operation. No Python loops over the 41,288 demand points — all gradient and Hessian sums are NumPy array operations. Function evaluation runs in ~1 ms instead of the ~30 seconds a naive loop would take.

**Key insight or aha moment**

Two big ones, and they happened in opposite directions.

The first was **mathematical**. After deriving $\nabla d_i = (1/d_i) \cdot (x - x_i, y - y_i)$, I noticed it's always a unit vector pointing from the demand point toward the facility. The gradient of any distance function is unit-magnitude — only the direction varies. That single fact reframed the entire problem geometrically: gradient descent is literally summing unit vectors away from each demand point, scaled by population weight, and walking against the result. It's not just symbol manipulation, it's a vector field.

The second was **computational and humbling**. First run of gradient descent with $\alpha = 10^{-7}$ blew up — overshot the optimum, walked off the map into the Pearl River estuary at lon=113.95, lat=22.04, and hit the 10,000-iteration cap without converging. Newton-Raphson on the same starting point with the same gradient code converged in 5 iterations. This is the **textbook step-size failure mode** Dr. Kuo lectured about in DASE2135 — "too large $\alpha$ → overshoot, oscillate, possibly diverge" — playing out in front of me on real HK data.

The fix was retuning to $\alpha = 10^{-9}$ (two orders of magnitude smaller), which made gradient descent converge in 255 iterations to the same answer Newton found in 5. **The 51× iteration ratio is exactly why second-order methods exist:** Newton uses the Hessian to fit a local quadratic and jump to its minimum; gradient descent only knows the slope and crawls down it blindly. Same problem, same correct math, two completely different convergence speeds.

The deepest insight wasn't the math itself but watching it work. The optimum coordinate (114.17071, 22.33729) sits almost exactly on Prince Edward MTR Station — which every Hong Konger already knows is the densest residential corridor in Kowloon. My equations independently rediscovered something obvious from lived experience. The fact that hand-derived calculus on a public-domain population dataset reproduced local common knowledge is the moment the project became real to me. Math isn't an exercise anymore. It's a tool I trust.

**What I got stuck on**

- Initial gradient descent step size $\alpha = 10^{-7}$ caused divergence as described above. The fix took 30 seconds (one-line edit, re-run) but the diagnostic process — looking at the failed final coordinate, recognizing it was off the map, connecting it to the lecture material on overshoot — was where the actual learning happened. Worth more than getting it right on the first try.
- The "warning" output saying solvers disagreed by 27 km was misleading on first glance. Reading it more carefully revealed Newton-Raphson and SciPy BFGS agreed to 5 decimal places; gradient descent's failed answer was the only outlier. Lesson: always read what the cross-validation is actually telling you, not just whether it printed "warning" or "ok."
- The numerical $\varepsilon = 10^{-9}$ inside `sqrt(dx² + dy² + EPS)` to guard against division-by-zero at demand points. Subtle but important — without it, if a solver step ever lands exactly on a demand point, the gradient explodes. Defensive coding for math edge cases.

**Next session's first move**

Session 004: visualize the convergence trails on a Folium map of HK. Plot the population heatmap from Session 002 as the background, overlay both algorithm trails — gradient descent's 255-step path snaking down through HK, Newton-Raphson's 5-step direct jump to Mong Kok — and add a marker at the final optimum. The side-by-side comparison is the GIF/screenshot for the README and CV. Once that exists, Phase 1a is complete and we move to Phase 1b: KKT-constrained optimization (must be within a district, must be near MTR, etc.).

**Time spent / mood**

~3 hours. Heaviest math session yet — full chain rule + quotient rule derivation, then implementation, then debugging the step-size failure. Mood: very high. Watching three independently-implemented solvers all land on Mong Kok to 8 decimal places is the most satisfying moment of the project so far. Especially because I derived the gradient and Hessian myself — there's a real "I built this from first principles" feeling that copy-pasting `scipy.minimize` would never give.

---

<!--
Template for future sessions — copy-paste below this line:

## Session NNN — YYYY-MM-DD — [3-word title]

**What I built / learned**

- 

**Key insight or aha moment**



**What I got stuck on**



**Next session's first move**



**Time spent / mood**


-->

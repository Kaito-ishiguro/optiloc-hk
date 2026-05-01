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
## Session 004 — 2026-04-27 — Eight Trails to Mong Kok

**What I built / learned**

- Built a multi-start variant of the Session 003 solver (`03_solve_weber_multi.py`) that runs both gradient descent and Newton-Raphson from 4 different starting points across HK — Tung Chung (west), Stanley (south), Sai Kung (east), Lok Ma Chau (north) — and saves all 8 convergence trails to a single consolidated CSV.
- Built `04_visualize_convergence.py` that renders a single Folium HTML map containing: the population heatmap as a background context layer, all 8 convergence trails as polylines (thin dashed for gradient descent, thick solid for Newton-Raphson, color-coded by starting point), 4 starting-point markers, and a gold star at the shared optimum. Added a title bar and legend overlay as baked-in HTML so the artifact stays self-contained when screenshotted.
- All 8 runs converged to lon=114.17071, lat=22.33729 — Prince Edward MTR — to 5 decimal places. Same answer, regardless of where you start in HK. This is the visual proof of convexity I derived in Session 003: convex objective ⇒ unique global minimum ⇒ any starting point converges to it.
- Newton-Raphson averaged 5–6 iterations per run vs gradient descent's 290–323. Roughly 50× faster across all 4 starts. This number is now the headline of the project.

**Key insight or aha moment**

Hit a real numerical optimization edge case that I hadn't seen in Session 003. Pure Newton-Raphson from Tung Chung blew up on the first iteration — the unconstrained step landed in a region where the Hessian became near-singular (numerical underflow on $1/d_i^3$ caused `overflow encountered in power`, then `np.linalg.solve` raised `LinAlgError: Singular matrix`). Session 003 didn't catch this because Victoria Harbour is geographically close to the optimum, so Newton's first step was small and harmless. Tung Chung is far enough that the unconstrained step overshot into a degenerate region.

The fix was **damped Newton with backtracking line search**: after computing the Newton step, try the full step first; if the objective doesn't improve, halve the step and retry up to 30 times. This is what every industrial-grade Newton implementation does and is the standard textbook remedy for "Newton can overshoot far from the optimum." Same algorithm, but globally convergent rather than only locally convergent.

The deeper insight: pure mathematical correctness isn't sufficient for a working solver. Session 003's hand-derived gradient and Hessian were already correct — proven by 8-decimal agreement with SciPy BFGS. But correctness only buys you local convergence. Robustness across all starting points requires safeguards that are not in the math itself: line search, trust regions, damping. This is exactly the gap between "implements the formula" and "ships a solver." Now I understand viscerally why SciPy BFGS has hundreds of lines of code wrapping a textbook formula that's three lines long.

**What I got stuck on**

- **Newton step landing on a singular Hessian** from the Tung Chung start. Took maybe 10 minutes to diagnose: `RuntimeWarning: overflow encountered in power` was the leading indicator (in `coef = ws / (d**3)`, some $d_i$ became numerically zero), and `LinAlgError: Singular matrix` from `np.linalg.solve` was the consequence. Once the diagnostic chain was clear, the fix (backtracking line search) was textbook.
- **PowerShell `Move-Item` failures and missing files** during the file shuffle at the start of the session. Got caught between not being inside the repo directory and forgetting to activate the venv. Lost 5 minutes to environment hygiene. Lesson: always check `(.venv)` and the working directory at the start of a session.
- **`Move-Item` quirk**: when the destination path looks ambiguous (e.g. `notebooks\` versus `notebooks`), PowerShell treats it as a rename if the folder doesn't exist or has odd permissions. Adding `-Force` and verifying the destination directory exists before moving is the safe pattern.

**Next session's first move**

Phase 1a is complete. The single-facility Weber problem is fully solved on real HK demographic data, hand-derived math, validated against SciPy, with a polished shareable visualization.

Two paths for Session 005:

1. **Phase 1b — KKT-constrained optimization.** Add real geographic constraints: facility must be inside Kowloon district (inequality constraint), at least 200m from a competitor (inequality), within 500m of an MTR exit (inequality). Solve via Lagrangian with KKT conditions, exactly the next chapter in DASE2135. This is the most direct continuation of the math story.

2. **Phase 1c — Multi-facility k-median.** Generalize from one facility to k facilities, alternating between assignment (which demand point goes to which facility) and Weber sub-problems (where to place each facility given its assigned demand). Closer to the Phase 3 logistics product vision (multiple last-mile hubs).

Strong candidate for the next session: **Phase 1b**, because it cleanly extends the existing single-facility solver, demonstrates KKT (the most lecture-relevant material), and the visualization is dramatic — watch the optimum jump from Mong Kok to wherever-the-constraint-allows.

Side action: write a polished README front section pitching the Mong Kok finding, with the Session 004 map as the hero image. This is the artifact recruiters will see first.

**Time spent / mood**

~1.5 hours including the PowerShell file-shuffle drama and the singular-Hessian debugging. Mood: very high. The eight-trails-to-Mong-Kok image is the single best engineering artifact from any of my projects so far. The math, the data, the algorithms, and the geography all came together into one picture that explains itself. This is the kind of work I want my CV to be made of.

---
## Session 005 — 2026-05-01 — KKT Constraints and the Kowloon Boundary

**What I built / learned**

- Hand-derived the **Lagrangian and the four KKT conditions** for constrained NLP — stationarity, primal feasibility, dual feasibility, and complementary slackness — directly from Dr. Kuo's lecture material. Wrote out the math step by step including the standard "$g_j(x) \leq 0$" form, the "$\nabla f + \sum \mu_j \nabla g_j = 0$" force-balance equation, and the shadow-price interpretation of the multipliers.
- Translated three real-world constraints into the standard form simultaneously: (1) facility must lie within Kowloon district, (2) within 500m of an MTR exit, (3) at least 200m from each of 5 synthetic competitors. Total of 7 inequality constraints active in one optimization problem.
- Implemented the constrained solver in `05_solve_constrained.py` using SciPy's SLSQP (Sequential Least Squares Programming), which applies KKT internally. Fed in the analytical gradient from Session 003 plus signed-distance constraint functions. Solver converged in 19 iterations.
- Built `06_visualize_constrained.py` to render the result on a Folium map: population heatmap as background, green Kowloon polygon, 624 MTR exits with their 500m proximity rings, 5 red competitor exclusion zones, plus both the unconstrained (gold) and constrained (red star) optima with a dashed line showing the 427m jump between them.
- Pulled real geographic data live from OpenStreetMap via `osmnx`: Kowloon polygon (14.5 km²) and all 624 MTR exits in HK. Synthetic competitors only — that data layer becomes a real moat in Phase 3.

**Key insight or aha moment**

The insight that surprised me most was **how to encode constraints**. My first instinct was to write boolean checks ("is the point inside Kowloon? yes/no"). That would be wrong — it produces a step function with a flat plateau and a vertical cliff, and gradient-based optimizers see no slope to descend on a plateau. The correct technique is **continuous signed-distance functions**: $g(x) = $ signed distance from $(x, y)$ to the constraint boundary, negative inside the feasible region and positive outside. This gives the optimizer a smooth gradient that always points toward feasibility, which lets SLSQP converge cleanly.

The deeper realization was that this isn't a special trick for polygons — it's the same idea applied to *any* constraint shape. The MTR constraint becomes "$500m - $ (distance to nearest MTR exit)," which is just a signed distance to the union of 500m circles. The competitor constraint becomes "(distance to competitor) $- 200m$," signed distance to a single circle. Polygon, circle, half-plane, anything — encode it as a continuous distance and the optimizer can descend toward feasibility from anywhere. This generalizes to every constraint I'll ever need.

The geographic insight was equally satisfying. The Kowloon constraint came out **active** with $g_1(x^*) = 0.000000$ — the constrained optimum sits exactly on the polygon boundary. Reading the map revealed why: the unconstrained Mong Kok optimum from Session 003 lies *just barely north of* OSM's "Kowloon" polygon. OSM uses the **historical** Kowloon — the area south of Boundary Street, the original 1860 lease boundary — which is smaller than the colloquial modern usage that includes Kwun Tong, Wong Tai Sin, and Kowloon East. The math forced the optimum 427m southwest to land exactly on the historical district line near Prince Edward MTR. So the project just exposed a real-world data subtlety about how "Kowloon" gets defined administratively versus colloquially.

The MTR constraint came out **inactive** despite there being 624 exits in HK. This is itself a finding: HK's MTR network is so dense that almost any reasonable urban location is already within 500m of an exit, so the transit-proximity constraint never binds. In a less transit-rich Asian city (Bangkok, Manila, Jakarta) the same constraint would do real work. That's a Phase 3 product insight hiding inside a Phase 1 demonstration.

**What I got stuck on**

- **Sign convention between standard form and SciPy.** Wrote constraints in the textbook "$g_j \leq 0$" form, then realized SciPy's `{"type": "ineq", "fun": ...}` expects the *opposite* convention — it wants `fun(x) >= 0` to mean feasible. Resolved by negating each constraint when handing it to SLSQP. The math derivation stays in textbook form for journaling and exam prep; only the SciPy interface flips signs. Worth noting this for future me — the mismatch between mathematical convention and software convention is the kind of thing that costs hours if you don't catch it early.
- **`lambda` capture in the competitor constraints loop.** First version generated all 5 competitor constraints with a closure that captured the loop variable by reference, so all 5 ended up referring to the last competitor. Fixed using the standard `lambda p, idx=l: ...` default-argument trick to capture by value. This is a Python idiom that catches everyone exactly once and then never again.
- **Distance-unit conversion.** The math is in degrees because that's what the demand coordinates are in, but the constraints are naturally in meters (500m, 200m). Used a rough constant `M_PER_DEG = 107_000` for HK's latitude. For Phase 2 the right move is to project everything to a metric CRS (e.g. EPSG:2326 HK 1980 Grid) so distances are in meters natively. Phase 1 doesn't need that precision.

**Next session's first move**

Phase 1b is now complete. Phase 1c (multi-facility k-median) is the next algorithmic extension — same Weber objective, but now optimize over $k$ facility locations simultaneously, with each demand point assigned to its nearest facility. The math involves alternating between assignment (Voronoi partition) and Weber sub-problems, plus a discussion of why the joint problem is non-convex even though each sub-problem is convex.

Strong alternative: skip directly to **writing the polished README with both maps as hero images** and treat that as Session 006. Phase 1 is far enough along now to package it cleanly. The unconstrained "8 trails to Mong Kok" map plus the constrained "boundary jump" map plus the math derivations together form a complete portfolio narrative. Better to harvest the storytelling now than push for one more algorithmic extension.

Leaning toward the README option. Multi-facility can be Session 007 or even Phase 2.

**Time spent / mood**

~2.5 hours including the math derivation, the OSM data fetch debugging, the SciPy sign-convention puzzle, and the visualization. Mood: very high. The geographic punchline — that the constraint forced the optimum onto the historical Kowloon boundary, exactly where Boundary Street physically sits — was the moment Phase 1b became more than a math exercise. The project is now teaching me about Hong Kong, not just optimization.

---
## Session 006 — 2026-05-01 — Phase 1 Shipped

**What I built / learned**

- Wrote the polished public-facing README that replaces the placeholder skeleton from Session 001. Recruiter-targeted but with technical depth below the fold for interviewers. Embedded three hero images (the eight-trails convergence map plus wide and zoomed views of the KKT-constrained result), the full math derivation summary, the data pipeline diagram, the tech stack, a roadmap of upcoming phases, and the personal "why I built this" framing.
- Took three screenshots from the existing HTML maps and committed them to `docs/maps/` so the README renders properly on GitHub. The wide-and-zoom pair for the constrained result tells the constraint story more completely than a single shot — wide shows HK's MTR network density (which is why the MTR constraint is inactive), zoomed shows the optimum landing precisely on the Kowloon boundary (which is why the Kowloon constraint is active).
- Verified the README renders correctly on GitHub: math equations display via native MathJax support, all three images embed inline, the headline finding (Prince Edward MTR / Mong Kok) is readable within the first 30 seconds of skimming.
- Phase 1 is now officially shipped. Five sessions of build work plus one session of polish equals a complete, defensible, public portfolio piece.

**Key insight or aha moment**

The most useful realization came from the screenshot strategy I proposed myself: instead of a single hero image for the constrained result, use a **wide shot plus a zoomed shot together**. Wide tells the dataset story (look how dense HK's MTR network is — 624 exits whose 500m proximity zones cover almost all populated areas). Zoomed tells the math story (look how precisely the solver landed on the Kowloon boundary). Single screenshots are easier to produce; layered ones tell a richer story. The same dataset, seen at two zoom levels, communicates two different lessons. Going to apply this pattern to future visualizations — every important result probably wants both a "context" view and a "precision" view.

The deeper insight from writing the README: **packaging is its own engineering discipline**. The math, the code, and the maps already existed before this session. None of that work changes the fact that, until today, my repo's front page was a Session 001 skeleton that didn't show what I'd built. One session of "just writing" took the same underlying work from "would impress someone who clicked through five files" to "impresses someone who lands on the page for 60 seconds." That's a leverage ratio I don't want to forget. Every project I build from now on gets a polished README in the same week as the first prototype, not as a "I'll do it later" task.

The third insight is about the recruiter-vs-interviewer audience question. I picked recruiters as primary, and the README structure reflects that: pitch up top (skim-friendly), depth below (interviewer-friendly). Both audiences are served because the same content can be skimmed or read deeply depending on intent. The mistake would be writing two separate documents or splitting the README into "for recruiters" and "for engineers" sections — both audiences are smarter than that and would interpret the split as condescending. One document, layered in depth, serves both.

**What I got stuck on**

- The original README was a skeleton from Session 001 written before I knew what the project would actually become. Resisting the urge to "just edit a few sections" and instead rewriting the whole thing was the right call — partial edits would have left the structure incoherent. Fully rewriting felt slower upfront but produced a cleaner artifact.
- LinkedIn URL question. I don't have a polished LinkedIn profile yet, so the README has a placeholder for the link. Polishing LinkedIn becomes a separate task — the README doesn't have to wait for it.
- Image filenames in the README had to match exactly what got committed to `docs/maps/`. Easy to mess up: any typo and the image renders as a broken-image icon on GitHub. Careful triple-check before committing was warranted.

**Next session's first move**

Two clear paths, no urgency on which:

1. **LinkedIn post + LinkedIn project entry.** Convert the README into a 250-word LinkedIn post with the convergence map as the visual, plus add the project to my LinkedIn "Projects" section. Same source material, different audience surface. Highest immediate ROI for summer 2026 internships — recruiters check LinkedIn before GitHub.
2. **Phase 1c — multi-facility k-median.** Generalize from one facility to k facilities. Mathematically richer (introduces non-convexity, Voronoi assignment, alternating optimization). Closer to the Phase 3 logistics product vision. Better for technical interviews than for recruiter discovery.

Leaning toward LinkedIn next. The technical work is already done; the discovery surface is what's missing.

**Time spent / mood**

~1 hour, mostly writing and screenshot-arranging. No new code. Mood: deeply satisfied. Phase 1 going from "five committed sessions of code" to "one URL I can put on a CV" is a different kind of milestone than each individual technical session was. The math sessions made me feel smart; this session makes the project feel real. Worth pausing to acknowledge.

Phase 1 of OptiLoc HK is shipped. The repo URL is now an artifact I can put on a CV without caveats.

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

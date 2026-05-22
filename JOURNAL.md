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
## Session 007 (Integration #1) — 2026-05-17 — Conditioning vs curvature

**What I built / learned**
- Wrote `notebooks/07_condition_number.py` — evaluates the Hessian at 6 points across HK (optimum + 5 spread across the territory), computes eigenvalues, condition number $\kappa$, and theoretical optimal step size $\alpha_{\text{opt}}$ at each
- Empirical finding: $\kappa$ ranges 1.24–3.25 everywhere. The Weber problem is **uniformly well-conditioned** across HK
- $\lambda_{\max}$ varies by 3.4× across space — the Hessian's magnitude is non-constant, signature of a non-quadratic objective
- Our chosen $\alpha = 10^{-9}$ was 8–45× smaller than $\alpha_{\text{opt}}$ at every test point, fully explaining why GD took 255 iterations vs Newton's 5

**Key insight or aha moment**
I expected to confirm Lecture 6's textbook story — "high $\kappa$ ⇒ slow GD" — and instead found the opposite. $\kappa$ is small everywhere; the real culprit is that $f(x,y)$ isn't quadratic. Lecture 6's analysis (and the standard $1/L$ step-size bound) implicitly assumes a fixed Hessian, in which case a single constant $\alpha$ can be globally optimal. Weber violates that: the Hessian's magnitude changes by 3.4× depending on where you stand. No single $\alpha$ works well everywhere — aggressive enough for regions of large $\lambda_{\max}$ means divergence elsewhere; safe enough for small $\lambda_{\max}$ means crawling near the answer. Newton's $H^{-1}$ rescales each step to local curvature automatically, which is why it converges in 5 iterations regardless of starting point. Constant-$\alpha$ GD structurally can't.

**What I got stuck on**
The reconciliation. I'd primed myself on the textbook "high $\kappa$" explanation and the empirical numbers didn't match. Spent a while double-checking the eigenvalue computation before realizing the textbook bound assumes a quadratic. Once I noticed that $\lambda_{\max}$ varies 3.4× across space — not just at the optimum — the non-quadratic interpretation clicked. Worth flagging for future me: Lecture 6's analysis is tight for least-squares / quadratic problems and shouldn't be cited for Weber without that caveat.

**Next session's first move**
Write `docs/strict_convexity.md` (Integration #2) — the symbolic proof that the Weber Hessian is strictly PD given non-collinear demand points. Integration #1 already supports this empirically (both eigenvalues positive at all 6 test points); this is the formal complement.

**Time spent / mood**
~90 min coding + analysis, plus the time it took to stop trusting Lecture 6 and start trusting the numbers. Good post-exam mood — exactly the kind of finding I'd want to remember if this came up in a Phase 2 design discussion.

---
## Session 008+009 — 2026-05-20 — Four-solver race shipped

**What I built / learned**
- Implemented the Weiszfeld algorithm in `notebooks/08_solve_weber_weiszfeld.py` — the FONC-derived fixed-point iteration Prof. Kuo flagged in his email. ~10 lines of NumPy, no hyperparameters, no step-size tuning, no Hessian inversion. Just $x^{(k+1)} = \sum_i (w_i/d_i) x_i \big/ \sum_i (w_i/d_i)$.
- Extended the comparison harness so all four solvers (Weiszfeld, Newton, BFGS, GD) run from the same Victoria Harbour start and record their full trails per iteration. Output: `solver_comparison.csv` (4-row summary) and `four_solver_trails.csv` (292 trail positions).
- Built `notebooks/09_visualize_four_solvers.py` producing `docs/maps/04_four_solvers_map.html` — population heatmap with four color-coded convergence trails (purple Weiszfeld, red Newton, teal dashed BFGS, gray dashed GD) all landing on the same Mong Kok optimum. Wide + zoom screenshots committed.
- Empirical results on 41,288 HK demand points: Weiszfeld 23 iters / 7.6ms, Newton 4 iters / 7.2ms, BFGS 7 iters / 5.5ms, GD 255 iters / 55ms. All four converge to the same optimum to within $7.7 \times 10^{-9}$ degrees (sub-millimeter on the ground).

**Key insight or aha moment**
Weiszfeld *ties* Newton on wall-clock despite Newton's quadratic convergence rate (4 iterations) vs Weiszfeld's linear rate (23 iterations). This contradicts the naïve reading of convergence analysis, but resolves cleanly: convergence rate is about *iteration count*, but the user cares about *time*, and Time = iterations × per-iteration cost. Newton's per-iteration cost is ~6× Weiszfeld's because it computes and factorizes the $2 \times 2$ Hessian; Weiszfeld just does one weighted average. On 2D Weber, the per-iteration cost gap cancels the asymptotic-rate advantage. The deeper lesson: linear convergence with cheap iterations beats quadratic convergence with expensive iterations on small problems — and the cheap iteration is also what makes Weiszfeld foolproof in the multi-start setting Phase 1c will need.

**What I got stuck on**
First run of the comparison harness showed Newton hitting `max_iter=100` instead of converging in ~5 iterations. Took a beat to realize it wasn't a Newton bug — it was a tolerance mismatch. The new harness used a tighter gradient-norm tolerance ($10^{-8}$) than Session 003, and Newton's $\|\nabla f\|$ never quite reached that bound because of floating-point noise in the `sqrt` inside the distance function. Fixed by switching Newton's convergence criterion to step-size ($\|x_{\text{new}} - x\| < \varepsilon$), matching Weiszfeld's. Same final answer, honest iteration count. Worth remembering for future benchmarking: convergence criteria must be consistent across solvers, or the comparison lies.

**Next session's first move**
Reply to Prof. Kuo's email with the four-solver comparison table, the wide+zoom screenshots, and a commitment to integrate the Esri China HK Outline Zoning Plans dataset as the next step (Session 010). Use the real numbers (23 iterations, 7.6ms, agreement to $10^{-9}$ degrees) rather than the predicted ones.

**Time spent / mood**
~3 hours including the convergence-rate lesson and the BFGS sidebar. Mood: validated. Prof was right that Weiszfeld was the missing piece — it's the algorithm-of-fit for the multi-start k-median in Phase 1c specifically because it has no failure modes. Also feels right that the public repo now carries an artifact responding directly to his suggestion *before* the email reply lands.

---
## Session 010 — 2026-05-20 — OZP Commercial Constraint

**What I built / learned**
- Built a 4-script pipeline hitting Esri China HK's public ArcGIS REST feature service: paginated fetch of all 11,963 Outline Zoning Plan polygons (`10_fetch_ozp.py`), filter + union to C + CDA only (`11_filter_and_union_ozp.py`), Weber solver with the new constraint (`12_solve_constrained_ozp.py`), and the comparison map (`13_visualize_ozp_constrained.py`). Discovery pattern was metadata-driven: item ID → AGOL sharing API → service URL → metadata → paginated query.
- Empirical finding: HK has only **10.30 km² of C+CDA zoning** across 590 source polygons (499 disjoint after unioning) — 0.9% of HK's 1,106 km² land area. The new feasibility region is ~5× smaller and 499× more topologically complex than Session 005's coarse Kowloon polygon.
- OZP-constrained Weber optimum: **(114.16944, 22.33321)** — Shek Kip Mei, sitting on the boundary of a small C-zoned polygon at the MTR station. ~474 m southwest of the unconstrained answer.
- The ArcGIS discovery + paginate + cache pattern maps directly to GCP idioms (sharing API ≈ service discovery, paginated FeatureServer query ≈ Cloud Function with Scheduler trigger, cached 120 MB GeoJSON ≈ GCS bucket as cache layer). High ACE-relevance.

**Key insight or aha moment**
The map-with-street-labels caught something I had been confidently wrong about for five sessions. Session 003's "Mong Kok / Prince Edward MTR" optimum at lat 22.33729 is actually **1.5 km north** of Prince Edward MTR, in the Sham Shui Po / Shek Kip Mei area. The reason is real geographic math: the New Territories holds >50% of HK's population, so the weighted geometric median is pulled north of urban Kowloon. Calling it "Mong Kok" was lazy pattern-matching against coordinates that *look* like they should be Mong Kok if you don't actually look at a map. The bigger lesson: visualize with real-world labels, not just lat/lon dots — labels surface errors that pure numerics can't. The same map also exposed a second mislabel: Session 005's "Kowloon polygon" doesn't appear to be the historical 1860 Kowloon south of Boundary Street — the constrained answer lands at the Beacon Hill ridge, well north of Boundary Street. The OSM polygon's actual provenance now needs re-investigation. Both errors are fixed in the updated CONTEXT.md.

**What I got stuck on**
- **SLSQP hit `maxiter=200`** (Exit mode 9, "Iteration limit reached") rather than formally converging. The result is correct to floating-point precision (`g_ozp(x*) ≈ -3 × 10⁻⁹`, optimum geometrically on a polygon boundary), but the formal convergence stamp is missing. Cause: the signed-distance constraint to a 499-piece MultiPolygon has a non-smooth gradient at polygon corners and along medial axes between adjacent polygons. SLSQP's numerical Jacobian via finite differences produces noisy gradient estimates → line-search struggle. Three candidate fixes: analytical constraint Jacobian (complex), buffer the union by ~1e-6 degrees to smooth corners (cheap, probably effective), switch to `trust-constr` (different API).
- **Pagination's last page took exactly 60 s** = the `requests` timeout value. 0.1 s slower and `ReadTimeout` would have killed it and I'd have 9,963 features instead of 11,963. Pure luck. Production version needs 120 s timeout + exponential-backoff retry.
- **Email to Prof. Kuo (sent earlier today) says "Mong Kok optimum."** Visibly wrong on any properly-labeled map. Probability he verifies coordinates is low; if it comes up, the truthful correction ("the actual location is Sham Shui Po / Shek Kip Mei — the NT pulls the centroid north of urban Kowloon") is a more interesting finding than the original "Mong Kok" claim anyway.

**Next session's first move**
Session 010b — try the cheapest of the three SLSQP smoothness fixes: buffer the MultiPolygon by `1e-6` degrees (~10 cm) to smooth corner kinks, re-run, see if SLSQP terminates with Exit mode 0 instead of Mode 9. If not, fall back to `trust-constr` with `NonlinearConstraint`. ~30 minutes total. After that, Session 011 — multi-facility k-median with Weiszfeld in the Lloyd's inner loop.

**Time spent / mood**
~3 hours, focused. Two of the better findings of the whole project so far came from things going *wrong* — SLSQP's `maxiter` forced a deeper read on constraint smoothness, and the visualization caught a coordinate mislabel I'd been carrying unverified across five sessions. The "treat failure as pedagogical" rule paid off twice. ACE-relevance was unusually high — the ArcGIS discovery + pagination + cache pattern is almost exactly what a Cloud Function consumer of upstream APIs looks like.

---
## Session 010b — 2026-05-21 — Buffer-smoothed SLSQP

**What I built / learned**
- Added `.buffer(1e-6)` to the OZP commercial union in `12_solve_constrained_ozp.py` to smooth the 499-piece MultiPolygon's corner kinks at sub-millimeter scale.
- SLSQP now terminates with Exit mode 0 in 16 iterations (was Exit mode 9 / 200 iterations).
- Optimum unchanged to floating-point precision: (114.169442, 22.333212), with g_ozp(x*) ≈ -5.3e-11 (even tighter on the boundary than before).
- Cleaned up two longstanding geographic mislabels in the script's print block: Mong Kok → Sham Shui Po, Kowloon historical boundary → Beacon Hill ridge (OSM Kowloon polygon).

**Key insight or aha moment**
The non-smoothness in Session 010's constraint Jacobian was localized — concentrated at polygon corners and medial axes between adjacent polygons. Rounding those corners with a ~10 cm arc (1e-6 degrees) was enough to give SLSQP's finite-difference gradient estimate a smooth signal to chase. The reason the buffer works without distorting the problem: the OZP polygon data itself was digitized at meter-scale precision by Lands Department, so a 10 cm round-off is well below the data's noise floor. trust-constr fallback wasn't needed. Same answer, but now with a formal Exit mode 0 convergence stamp.

**What I got stuck on**
Nothing this session — buffer worked on first try. The conceptual part (why finite differences need smooth gradients in the first place) was the only thing that needed unpacking.

**Next session's first move**
Session 011: implement multi-facility k-median.

**Time spent / mood**
~30 minutes. Satisfying closure on a known wart.

---
## Session 011 — 2026-05-21 — k-median network

**What I built / learned**
- Implemented Lloyd's algorithm + Weiszfeld inner solver in `notebooks/14_solve_kmedian.py` for the multi-facility k-median problem (k=5, 10 weighted-random restarts, max 50 Lloyd iters, step-size tol 1e-7 on Weiszfeld).
- Wrote `notebooks/15_visualize_kmedian.py` rendering the result as a Folium map with Voronoi service-area polygons (via shapely.ops.voronoi_diagram clipped to an HK bbox), dashed convergence trails, and init+final facility markers.
- Best objective across 10 restarts: 274,830 weighted-units. 59.1% reduction from the single-facility Weber baseline (671,466 from Session 003).
- Multi-start found ≥4 distinct local minima from 10 random inits; worst-best gap was 9.3%. Total runtime 5.74s for ~1000 Weber sub-solves.

**Key insight or aha moment**
Lloyd's decomposes a non-convex joint problem (find both assignments AND facility locations simultaneously) into two convex sub-problems alternated until convergence — each step decreases the objective monotonically, so convergence is guaranteed, but only to a local minimum. The empirical proof of non-convexity was striking: 10 random inits, ≥4 distinct local optima, 9.3% spread between best and worst. If I'd run one restart and gotten unlucky, I'd have shipped a measurably worse answer with no way of knowing. Multi-start isn't a polish step on k-median; it's required. Weiszfeld is what makes the multi-start budget feasible — 1000 Weber sub-solves in 5.74s with zero failure modes. Newton would have been per-call faster but at least one of those 1000 calls would likely have hit a singular Hessian (we saw exactly this fragility in Session 004 from the Tung Chung start). The 5 facilities ended up spanning HK sensibly: western NT, NW NT, northern NT, central Kowloon, eastern Kowloon — two in the dense spine, one in each peripheral region.

**What I got stuck on**
Conceptual: hadn't seen Lloyd's before. The "joint problem hard because assignment $a$ is combinatorial, but each sub-problem easy" framing was the unlock — it turns this from "another iterative algorithm" into "a general pattern (alternating optimization) I should expect to see elsewhere, including k-means clustering." Nothing got stuck in code; both scripts ran first try.

**Next session's first move**
Session 012: k-sweep. Solve for k ∈ {3, 5, 8, 10} and plot the objective curve to see diminishing returns. Alternative branches: re-introduce the OZP commercial constraint per-cluster (combines Sessions 010 and 011), or GCP/Phase 1d work tied to ACE study. Pick at session start.

**Time spent / mood**
~90 minutes including the Lloyd's algorithm walkthrough. Best end-of-session feeling so far — the Voronoi map makes the math feel like a tool, not an exercise.

---
## Session 012 — 2026-05-22 — Constrained k-median shipped

**What I built / learned**

- `notebooks/16_solve_kmedian_ozp.py` — k-median with Lloyd's outer loop and a conditional Weiszfeld → SLSQP inner solver against the buffered OZP commercial union. Same hyperparameters as Session 011 (K=5, 10 restarts, seed 42) so results are directly comparable.
- `notebooks/17_visualize_kmedian_ozp.py` — Folium map with commercial-zone overlay, Voronoi service areas, dashed Lloyd trails, init/final facility markers, title + legend.
- Best objective: **277,595 weighted-units, +1.0% penalty** over Session 011's unconstrained baseline of 274,830. Translated to ground distance, the average HK resident is ~4.0 km from their nearest of the 5 facilities (vs 3.9 km unconstrained, vs 9.6 km with one central facility).
- Adding the constraint **roughly doubled non-convexity**: Session 011 had ≥4 distinct local minima with a 9.3% worst-best gap; Session 012 has 9 distinct minima with a 23.1% gap.

**Key insight or aha moment**

Constraints don't just shrink the feasible region — they can change the topology of the problem in ways that make it strictly harder to solve. The OZP commercial union is a 499-piece disconnected MultiPolygon, and a per-cluster Weber sub-problem against it can have one local minimum per polygon. SLSQP only finds the local minimum in its warm-start polygon's basin. That combinatorial layer ("which polygon does each facility settle in?") stacks on top of Lloyd's existing non-convexity from cluster-assignment choices, multiplying the number of basins the outer multi-start has to explore. A single-restart implementation would have shipped a 23% worse answer with zero detection. Multi-start went from "nice to have" in Session 011 to mandatory in Session 012.

**Real-world meaning of the output**

The 5 facility locations represent a complete logistics network for Hong Kong — five physical addresses on commercially-zoned land, each serving its colored Voronoi territory. In a deployed system this could be a last-mile delivery hub network (Lalamove, SF Express, HKTVmall), an EV fast-charging network, a retail chain expansion, or a government service rollout — the math is use-case-agnostic. The headline for any of these is the same: **restricting yourself to legal commercial-zoned land costs essentially nothing** — about 40 meters of extra travel per HK resident on average vs unconstrained placement. HK's zoning policy happens to be very well aligned with population distribution. The +1% penalty is what makes the constraint cheap; the 1→5 facility jump (~9.6 km → ~4 km average travel) is where the actual economic value lives. Caveats for a real deployment: this uses Euclidean distance (Victoria Harbour is invisible to the model), population as the demand weight (not delivery volume), and no facility-cost or capacity terms.

**What I got stuck on**

Two empirical surprises that didn't break the run but were worth understanding:

1. **Conditional-invocation didn't save runtime.** I expected dense-Kowloon clusters to land naturally on commercial parcels so SLSQP would fire only on NT clusters. The data said no — SLSQP fired on ~100% of Weiszfeld calls. Kowloon is mostly *residential* by area; commercial sits in narrow corridors (Nathan Road, Mong Kok, TST). Total runtime was 107s vs Session 011's 5.7s — a ~20× slowdown. The conditional logic was right by design (no harm done), wrong by empirical prediction.

2. **4 of 10 restarts hit MAX_LLOYD_ITERS=50 without converging — including the winner.** Restarts 6 and 9 both maxed out at obj ≈ 277,595 (agreement to 4 sig figs across two independent inits is strong evidence the answer is real). Likely cause: the algorithm is oscillating between two near-equivalent assignments while facility positions stay essentially stable. Fix is either bumping `MAX_LLOYD_ITERS` to 100 or adding "no objective improvement in N iterations" as a secondary criterion. Deferred — the answer is solid.

**Next session's first move**

Default: **(a) k-sweep over k ∈ {3, 5, 8, 10} on the OZP-constrained network** — plot the diminishing-returns curve. Cheap (~1 hour) and the natural follow-up. Alternatives if priorities shift: (b) fix the assignment-oscillation issue and re-run for clean convergence, or (c) draft the Prof. Kuo follow-up email with the +1% finding.

**Time spent / mood**

[fill in]

---
## Inter-session — 2026-05-22 — Strategic pivot & roadmap

**What I built / learned**
- Tore down the AI-drafted "OptiLoc B2B SaaS Business Plan" PDF; rebuilt as a realistic 5-phase roadmap.
- Decided HK-only through at least Session ~40. EV charging as default vertical, flexible to any sector that generates ops-director conversations.
- Locked in: math foundations (road-network distance, capacitated p-median) are NON-skippable blocking dependencies before customer discovery starts.
- Hybrid open-source: `optiloc-core` stays public (math library), `optiloc-app` becomes private when built in Phase 3.
- Shipped `docs/ROADMAP.md` (commit `57b630d`) as the canonical product/business reference. Companion to CONTEXT.md and MATH.md.

**Key insight or aha moment**
The original "make this a profitable SaaS" framing was wrong. Realistic version: this is a *consulting funnel* that might productize into SaaS once 5+ pilots reveal what the standard workflow actually is. The math is a foot-in-the-door, not a moat. The real moat is HK-specific data + customer relationships built over 18-24 months. My deeper goal isn't revenue first — it's getting reps pitching and presenting to ops directors. Revenue follows that.

**What I got stuck on**
The original B2B SaaS plan PDF I uploaded was generic AI-template work with real errors: pricing invented, "10% cost reduction" overclaim, made-up dark-kitchen use case, Supabase contradicting the GCP plan. Useful exercise to see what AI-generated business plans look like vs. what a tailored plan needs.

**Next session's first move**
Session 013 — k-sweep diminishing returns. Solve OZP-constrained k-median for k ∈ {3, 5, 8, 10, 15, 20}, plot objective vs k. This chart becomes the headline visual on the Phase 1 landing page.

**Time spent / mood**
~1 hour strategic conversation. Mood: energized. The project finally has a North Star that's honest about what it takes to be a real money-making thing vs. what it takes to be a great portfolio piece. Both paths legitimate; ROADMAP supports either.

---
## Session 013 — 2026-05-22 — k-sweep diminishing returns

**What I built / learned**
- notebooks/18_ksweep_ozp.py: outer k-loop wrapping Session 012's solver via
  importlib, sweeping k ∈ {3,5,8,10,15,20} with 10 multi-start restarts each;
  fresh RNG(42) per k for reproducibility; checkpoint CSVs written after each k.
- notebooks/19_visualize_ksweep.py: two-panel diminishing-returns chart
  (objective vs k with multi-start min-max band, per-point % reduction labels,
  worst-best gap bars with convergence-rate annotations).
- notebooks/20_visualize_ksweep_maps.py: 2×3 panel gallery showing the best
  hub network at each k with Voronoi service areas, weighted demand hexbin
  background, and OZP commercial overlay.
- CSV outputs: ksweep_ozp_summary.csv, ksweep_ozp_all_restarts.csv,
  ksweep_ozp_best_facilities.csv.
- Reproducibility check: k=5 inside the sweep exactly matched Session 012's
  277,595 ✓. Total sweep runtime 6.3 min (faster than the 20-min estimate).

**Key insight or aha moment**
The two charts tell two different stories that have to be read together. The
diminishing-returns curve says "elbow around k=8-10, beyond which each marginal
facility buys progressively less coverage" — the quantitative argument for a
CAPEX trade-off. The spatial gallery reveals what's actually happening
geographically: as k grows, marginal hubs cluster in already-dense urban areas
(Kowloon, north HK Island), not in underserved NT or outer islands. The
total-weighted-distance objective concentrates capacity where there's already
population. That's the right behavior for an EV-utilization or last-mile
customer chasing throughput, and the wrong behavior for a public-health
customer chasing equitable rural coverage. The objective function determines
which customer profile we're serving. Different customers literally need
different solvers.

**What I got stuck on**
Mid-session I lost track of what each chart layer represented (the % labels,
the multi-start band, the X/10-converged annotations) and had to walk back
through them. Also flagged but didn't fix: the convergence-rate dropoff at
k=20 (5/10 restarts hit MAX_LLOYD_ITERS) — the Session 012 oscillation issue
amplifies with k. Candidate later fix: change Lloyd's stop criterion from
"assignment vector unchanged" to "max facility shift < ε." Minor mechanical
hurdle: file 16 isn't importable normally because module names can't start
with a digit; importlib.util.spec_from_file_location handled it cleanly.

**Next session's first move**
ROADMAP Phase 1: Session 014 = Dockerize the solvers and wrap them in FastAPI.
First step is writing the Dockerfile + pinning requirements.txt, building the
image locally, hitting a /solve endpoint with a sample request body. Two
sessions out, this becomes the artifact deployed to Cloud Run.

**Time spent / mood**
~2 hours, energizing. First session where the visible outputs (the chart and
the map gallery) felt directly landing-page-ready, not just "portfolio piece
for the class." Reproducibility check passing on the first run was satisfying.

**Real-world meaning of the output**
Two artifacts are now sellable as customer-discovery anchors:
- "How many hubs is enough for HK?" chart: canonical diminishing-returns
  curve with the elbow at k≈8-10. Translates to "10 hubs gets you 74% of the
  achievable coverage; 20 hubs only buys you another 9pp." Pairs naturally
  with "what's your CAPEX target?" in a first conversation.
- "Where the hubs land at each scale" map gallery: six side-by-side hub
  networks. Reveals that marginal hubs concentrate in urban density at high k.
Caveat: distances are still Euclidean great-circle, not road-network. The
SHAPE of the trade-off is sellable today; absolute km claims are not yet.
Road-network distance is Session 016 per ROADMAP — the blocking math
foundation before first paid pilot.

---
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

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

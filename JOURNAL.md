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

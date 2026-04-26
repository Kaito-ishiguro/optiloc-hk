# OptiLoc HK

> *Where in Hong Kong should you put a thing so the people who use it walk the least?*

An interactive facility location optimizer for Hong Kong. Given a set of weighted demand points (population by district, transit ridership, customer locations), it computes the mathematically optimal coordinate for placing a new facility — a delivery hub, a retail store, a charging station, a clinic — under realistic geographic and competitive constraints.

**Status:** 🟡 Phase 1 — in early build (started April 2026). See [`JOURNAL.md`](./JOURNAL.md) for the full build log.

---

## The Problem

Site selection in Hong Kong is currently a gut-feel decision made by real estate agents with spreadsheets. Big global tools (Placer.ai, Esri, Carto) are dashboards — they show you data and let a human pick. None actually solve the optimization problem.

OptiLoc HK does. It treats site selection as a **constrained nonlinear optimization problem** and returns the provably optimal coordinate plus a visualization of how the algorithm got there.

## The Math (Phase 1)

The core objective is the classical **Weber problem**:

$$f(x, y) = \sum_{i=1}^{n} w_i \cdot \sqrt{(x - x_i)^2 + (y - y_i)^2}$$

minimizing the weighted sum of Euclidean distances from a candidate facility $(x, y)$ to $n$ demand points. Phase 1 implements:

- **Gradient descent** — first-order method, hand-derived $\nabla f$
- **Newton-Raphson** — second-order method, hand-derived Hessian $\nabla^2 f$
- **Weiszfeld's algorithm** — the classical fixed-point iteration for this exact objective
- **SciPy benchmarks** — `BFGS` for unconstrained, `SLSQP` / `trust-constr` for the KKT-constrained version
- **KKT conditions** — added in Phase 1b for "must lie within X district," "must be ≥ 200m from competitor Y," "must be within 500m of an MTR exit" constraints

This project applies coursework from HKU's **DASE2135 Mathematical Optimisation** (Spring 2026, Dr. Y.H. Kuo).

## Tech Stack

- **Python** — NumPy, SciPy, Pandas
- **Geo** — Folium for HK map rendering, `osmnx` for OpenStreetMap data, GeoPandas for shapefiles
- **Frontend** — Streamlit (initial) → React/TypeScript (Phase 2)
- **Data** — `data.gov.hk` Census 2021 TPU population, OpenStreetMap, HK GeoData Store

## Roadmap

- **Phase 1a** — Single-facility unconstrained Weber problem with HK Census demand data, gradient descent vs. Newton vs. Weiszfeld convergence comparison
- **Phase 1b** — Add real geographic constraints (water, country parks, MTR-corridor zones) via KKT formulation
- **Phase 1c** — Multi-facility extension (k-median problem)
- **Phase 2** — Polished web app with shareable map outputs, scenario presets for HK common cases
- **Phase 3** — Pivot the application layer toward Asian logistics network optimization (last-mile hub placement, micro-fulfillment center siting, EV charging station rollout)

## Repository Layout

```
optiloc-hk/
├── README.md           ← you are here
├── JOURNAL.md          ← dated build log
├── data/               ← raw + processed HK data (gitignored where appropriate)
├── src/                ← optimization algorithms and data pipeline
├── notebooks/          ← exploratory Jupyter notebooks
├── docs/               ← math derivations, design notes
└── tests/              ← unit tests for solvers
```

## About

Built by Kaito, second-year IELM (Industrial Engineering and Logistics Management) student at HKU, as a portfolio project applying optimization theory to a real Hong Kong problem. Started April 2026.

Read the full build log in [`JOURNAL.md`](./JOURNAL.md) — every session, dated, with what I learned and what I got stuck on.

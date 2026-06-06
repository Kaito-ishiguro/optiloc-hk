# OptiLoc HK — Solver Mathematics

This document describes the mathematical formulation and algorithm behind each
solver endpoint. The intended reader is a technical reviewer familiar with
combinatorial optimization: a hiring engineer, a teaching assistant, or a
research collaborator.

---

## Data model

**Demand points.** The raw demand layer is 41,288 weighted points derived from
WorldPop raster data (7,496,988 residents). Each point carries a weight
$w_i > 0$ (population). For road-network solvers these points are aggregated to
their nearest road-graph nodes, yielding $N$ distinct aggregated demand nodes
$\{p_1, \ldots, p_N\}$ with weights $\{w_1, \ldots, w_N\}$.

**Road graph.** Hong Kong's road network is loaded from OpenStreetMap via
osmnx: 18,820 nodes, 35,848 directed edges. All road-network solvers use the
undirected version with `weight="length"` (metres). Dijkstra is the only
distance primitive — no Euclidean approximation, no straight-line shortcuts.
The harbour is a natural barrier: two nodes that look close on a map may be
3–11 km apart by road.

**Notation.**
- $V$ — set of all road-graph nodes
- $d(u, v)$ — shortest-path road distance in metres between nodes $u, v \in V$
- $\phi(u)$ — the aggregated demand node obtained by snapping a point to its
  nearest road node

---

## 1. Weber problem / 1-median (`POST /solve_weber_road`)

### Formulation

Find a single facility location $x^* \in V$ minimising the total
population-weighted road distance to all demand nodes:

$$\min_{x \in V} \; F(x) = \sum_{i=1}^{N} w_i \cdot d(x, p_i)$$

This is the **discrete 1-median** on a road graph. Because $x$ must lie on a
graph node, the feasible set is finite ($|V| = 18{,}820$) but brute-force
enumeration is too slow: each candidate evaluation requires one full Dijkstra
($O((|E| + |V|) \log |V|)$).

### Algorithm: Maranzana local search

The solver uses hill-climbing on the graph neighbourhood (Maranzana 1964):

1. Start from a seed node $x_0 \in V$.
2. Evaluate $F(v)$ for every graph-neighbour $v \in \mathcal{N}(x_0)$.
3. Move to the best-improving neighbour. Repeat until no neighbour improves,
   or 500 steps.

Each step requires one Dijkstra from the current node.

**Multi-seed restarts.** The algorithm is non-convex — local optima exist.
Three seeds are used in parallel, and the best result is kept:

| Seed | Rationale |
|------|-----------|
| Nearest road node to the Euclidean Weber optimum | Warm start from a continuous-domain approximation |
| Highest-weight aggregated demand node | High-density areas are natural median candidates |
| 10th-highest-weight demand node | Diversification in case the top node is in a local basin |

**What it does not guarantee.** Maranzana local search finds a local optimum,
not the global optimum. The gap is empirically small on the HK road graph
(benchmark: all three seeds converge to the same result for $k=1$), but
optimality is not certified.

### Output metric

The primary output is `per_resident_m` $= F(x^*) / \sum w_i$: mean road
distance (metres) from a randomly chosen resident to the optimal facility.

---

## 2. k-median (`POST /solve_kmedian_road`)

### Formulation

Generalise the 1-median to $k$ facilities. Given $k$ open facility nodes
$S = \{x_1, \ldots, x_k\} \subset V$, each demand node is served by its
nearest open facility. Minimise total weighted distance:

$$\min_{S \subset V,\, |S|=k} \; \sum_{i=1}^{N} w_i \cdot \min_{j \in \{1,\ldots,k\}} d(x_j, p_i)$$

This is NP-hard in general. The solver uses a multi-start Lloyd's heuristic.

### Algorithm: Lloyd's (assign-then-relocate)

Each restart:

1. **Seed.** Draw $k$ facility nodes at random from the aggregated demand nodes
   (without replacement).

2. **Assignment step.** Run one Dijkstra from each facility node $x_j$. Assign
   each demand node $p_i$ to its closest facility:
   $$z(i) = \arg\min_{j} \; d(x_j, p_i)$$

3. **Location-update step.** For each cluster $C_j = \{i : z(i) = j\}$,
   compute the population-weighted centroid in geographic coordinates and snap
   it to the nearest road node:
   $$\hat{x}_j = \phi\!\left(\frac{\sum_{i \in C_j} w_i \cdot p_i}{\sum_{i \in C_j} w_i}\right)$$

4. Repeat steps 2–3 until assignments $z$ do not change, or the iteration cap
   is reached.

**Multi-start.** Steps 1–4 run for `n_restarts` independent random seeds. The
restart with the lowest final objective is returned. The `worst_best_gap_pct`
field in the response reports how much the worst restart exceeds the best,
indicating landscape flatness.

**Centroid snap.** The location update computes an exact weighted centroid in
latitude/longitude space, then calls `ox.nearest_nodes` to project it onto the
graph. The snapped node may not be in the demand set — it is any road node.
This is a deliberate approximation: the true discrete location update (finding
the Voronoi 1-median within each cluster) would require $O(|C_j|)$ additional
Dijkstras per cluster per iteration.

### Baseline-aware audit (`POST /analyze_network`)

The `/analyze_network` endpoint wraps the k-median solver with a comparison
against an operator's existing network:

$$\text{improvement} = \frac{F(\text{existing}) - F^*(k)}{F(\text{existing})} \times 100\%$$

where $F(\text{existing})$ is the total weighted distance under the operator's
current facility locations (snapped to road nodes), and $F^*(k)$ is the
k-median optimum. This is the source of the published 42.97% improvement
statistic for Hong Kong's self-storage sector at $k=2$.

---

## 3. MCLP — Maximal Coverage Location Problem (`POST /solve_mclp_road`)

### Formulation

Rather than minimising mean distance, MCLP maximises the demand covered within
a radius $r$. Two objective modes are implemented.

**Binary mode** (Church & ReVelle 1974):

$$\max_{S \subset V,\, |S|=k} \; \sum_{i=1}^{N} w_i \cdot \mathbf{1}\!\left[\min_j d(x_j, p_i) \le r\right]$$

A demand node is either covered (within $r$ metres of the nearest facility) or
not — there is no partial credit.

**Decay mode:**

$$\max_{S \subset V,\, |S|=k} \; \sum_{i=1}^{N} w_i \cdot \exp\!\left(-\frac{\min_j d(x_j, p_i)}{\lambda}\right)$$

where $\lambda$ (metres) is the decay constant. Every demand node receives
fractional credit that decreases exponentially with distance. At $d = \lambda$
the credit is $e^{-1} \approx 0.37$; at $d = 3\lambda$ it is about 5%.

The two modes represent different assumptions about accessibility: binary
captures hard service boundaries (e.g. a coverage mandate within $r$), while
decay models how willingness-to-travel degrades continuously with distance.

`coverage_pct` is always reported in binary terms regardless of mode — it is
the fraction of total weighted demand within $r$ of the nearest facility.

### Algorithm: greedy interchange

Each restart proceeds as follows:

1. **Seed.** Draw $k$ facility nodes at random from the demand nodes.

2. **Build distance matrix.** Run one Dijkstra per facility:
   - Binary mode: cutoff at $r$ (Dijkstra stops at the coverage boundary,
     substantially reducing runtime).
   - Decay mode: full-graph Dijkstra (all distances needed for the sum).

3. **Greedy interchange loop.** For each facility $j$ in turn:
   - Compute `nearest_excl_j`: for each demand node, the distance to the
     nearest *other* open facility (pure array operation, no Dijkstra).
   - Build a candidate set: demand nodes not currently covered when $j$ is
     excluded (`nearest_excl_j > r`), ranked by their own weight, capped at
     200 candidates (see below).
   - For each candidate, run one Dijkstra and compute the new objective if $j$
     were swapped for that candidate. Accept the first improving swap and
     restart the facility loop.
   - Repeat until no swap improves the objective or the iteration cap (50) is
     reached.

**Candidate cap.** With $N \approx 18{,}800$ aggregated demand nodes, a full
scan over all non-facility nodes per interchange step would require $O(N)$
Dijkstras per facility per pass — prohibitively slow. The implementation
restricts the candidate pool to the top 200 uncovered nodes ranked by demand
weight. This is a standard accepted heuristic for large MCLP instances
(Church & ReVelle 1974 explicitly discuss candidate-set restriction), not a
silent degradation — it is logged so the caller can inspect how many candidates
were tried.

**Multi-start.** The interchange loop runs for `n_restarts` independent seeds;
the best result is kept.

---

## 4. Rent-aware k-median (`POST /solve_kmedian_rent_road`)

### Motivation

The standard k-median minimises mean distance regardless of facility rent.
A self-storage operator cares about both — a site one kilometre farther away
in a low-rent district may have a better combined outcome than the pure-distance
optimum in Wan Chai. The rent-aware solver trades off these two objectives.

### Formulation

$$\min_{S} \; \underbrace{\frac{\sum_i w_i \cdot d(x_{z(i)}, p_i)}{\sum_i w_i}}_{\text{mean distance (m)}} + \; \rho \cdot \underbrace{\frac{1}{k} \sum_{j=1}^{k} \hat{r}_j}_{\text{rent penalty (m)}}$$

where $\rho$ is `rent_weight` (default 0) and $\hat{r}_j$ is the normalised
rent at facility $j$, converted to metres for dimensional consistency:

$$\hat{r}_j = \frac{r_j - r_{\min}}{r_{\max} - r_{\min}} \cdot D_{\text{ref}}$$

$r_j$ is the regional flatted-factory rent (HKD/sqm/month, from RVD Q4 2025
data), and $D_{\text{ref}} = 10{,}000\,\text{m}$ is a reference distance that
places the rent penalty on the same scale as road distances.

At $\rho = 0$ the objective reduces exactly to the standard k-median
(`solve_kmedian_road`) and the results match.

**Rental data.** Three regions with observed industrial vacancy: Hong Kong
Island (HK\$186/sqm), Kowloon (HK\$218/sqm), New Territories (HK\$164/sqm).
Excluded districts (Wan Chai, Sha Tin, Islands) have zero industrial stock/
vacancy in the RVD data; they receive $r_{\max}$ as a penalty so the solver
never prefers them as facility locations.

### Algorithm

Lloyd's assign-then-relocate, identical in structure to Section 2, with three
modifications:

1. **Eligible seed set.** Seeds are drawn only from demand nodes in districts
   with observed rental data.

2. **Low-rent seeding bias.** When $\rho > 0$, seeds are drawn from a
   probability distribution proportional to $(r_{\max} - r_j)$, with a uniform
   floor so every eligible node remains reachable. This ensures NT solutions
   are explored even with a small `n_restarts`.

3. **Restart selection.** The best restart is selected by the combined objective
   (distance + rent penalty), not pure distance.

---

## 5. Competitor coverage (`POST /competitor_coverage`)

### Formulation

Given an operator network $A = \{a_1, \ldots, a_m\}$ and a competitor network
$B = \{b_1, \ldots, b_n\}$, classify each demand node by proximity:

$$\text{zone}(i) = \begin{cases}
\texttt{operator\_wins} & \text{if } d(A, p_i) \le d(B, p_i) \\
\texttt{competitor\_wins} & \text{if } d(B, p_i) < d(A, p_i) \\
\texttt{neither} & \text{if both distances are } \infty
\end{cases}$$

where $d(S, p_i) = \min_{s \in S} d(s, p_i)$ is the shortest road distance
from any facility in set $S$ to demand node $p_i$.

Equidistant nodes (ties) are assigned to the operator.

**At-risk demand** is the total weighted demand in `competitor_wins` zones —
residents for whom the competitor is strictly closer.

### Algorithm: multi-source Dijkstra

Computing $d(A, p_i)$ for all $i$ naively would require one Dijkstra per
facility in $A$, then taking the minimum. Instead, the solver uses
`nx.multi_source_dijkstra_path_length` with all of $A$ as simultaneous sources:
a single modified Dijkstra pass initialises the priority queue with all source
nodes at distance 0, and the result is equivalent to $\min_{a \in A} d(a, v)$
for every node $v \in V$. This runs in $O((|E| + |V|) \log |V|)$ regardless of
$|A|$. One pass for $A$, one pass for $B$.

### At-risk 1-median

When `recommend_site=true`, the solver runs a road-network 1-median on the
at-risk demand subset only (Maranzana local search, identical to Section 1):

$$x^*_{\text{risk}} = \arg\min_{x \in V} \sum_{i : \text{zone}(i) = \texttt{competitor\_wins}} w_i \cdot d(x, p_i)$$

Seeds are the top `n_restarts` highest-weight at-risk nodes. The recommended
site minimises mean road distance to at-risk residents — it is the best
single new location to recover demand currently closer to the competitor.

**What this does not model.** The zone boundary is determined purely by road
distance; it does not account for facility attractiveness, pricing, capacity,
or brand. Two facilities equidistant by road are treated identically regardless
of size or offering.

---

## Summary table

| Endpoint | Objective | Algorithm | Guarantees |
|---|---|---|---|
| `/solve_weber_road` | Minimise $\sum w_i d(x, p_i)$ | Maranzana local search, 3 seeds | Local optimum |
| `/solve_kmedian_road` | Minimise $\sum w_i \min_j d(x_j, p_i)$ | Lloyd's multi-start | Local optimum |
| `/analyze_network` | Improvement vs operator baseline | k-median + baseline Dijkstra | Local optimum |
| `/solve_mclp_road` | Maximise covered demand | Greedy interchange, candidate cap 200 | Local optimum |
| `/solve_kmedian_rent_road` | Minimise distance + rent penalty | Lloyd's with rent-weighted seeding | Local optimum |
| `/competitor_coverage` | Zone classification + at-risk site | Multi-source Dijkstra + 1-median | Exact classification; local 1-median |

All road-network distance computations use Dijkstra on the HK OSM road graph.
No solver falls back to Euclidean or centroid approximations.

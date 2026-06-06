# Centroid-snap vs. true 1-median: coverage-audit interpretation

Benchmark: `benchmarks/centroid_vs_median.py`. Both solvers share init, assignment, convergence test, and scoring (the production `_road_objective`, via scipy validated bit-identical to networkx). The ONLY difference is the Lloyd location step: production's population-weighted **centroid snap** (a k-means update) vs the true graph **1-median** (Maranzana's heuristic).

Instance: 12,513 aggregated demand nodes, total weight 7,496,988. Sweep: k in [1, 2, 3, 5], 10 seeds, 5 restarts (best-of), both methods.

## 1. Where centroid-snap is worse, and by how much

`gap_pct = (centroid_obj - median_obj) / median_obj * 100`. Positive means the true median is better (lower total weighted road distance).

| k | mean gap | std (seeds) | min | max | negative gaps | centroid m/res | median m/res |
|---|---|---|---|---|---|---|---|
| 1 | +11.06% | 0.00 | +11.06% | +11.06% | 0/10 | 13,991 | 12,597 |
| 2 | +5.58% | 0.00 | +5.58% | +5.58% | 0/10 | 9,015 | 8,539 |
| 3 | +4.15% | 1.19 | +1.57% | +5.99% | 0/10 | 7,584 | 7,282 |
| 5 | +6.92% | 2.50 | +1.69% | +10.93% | 0/10 | 5,851 | 5,473 |

The true median is better at **every k and every seed** (no negative gaps in the best-of sweep). Mean improvement ranges from +4.15% to +11.06%.

**Production default flipped (Session 046):** the centroid-snap location step in `solve_kmedian_road` and `solve_kmedian_rent_road` has been replaced with post-Lloyd Maranzana refinement. The published headline is now **~46% improvement / 8,539 m/resident** (k=2 true median vs baseline 15,809 m/resident). The old centroid figure (9,015 m/resident / 42.97%) is retained in the benchmark table above as a historical reference only.

## 2. Stability across seeds

k=1 and k=2 are deterministic (std 0): k=1 has a single cluster with one 1-median; at k=2 best-of-5 finds the same optimum from every seed. k=3 and k=5 show modest spread (std 1.19 and 2.50) but never flip sign. A single restart is NOT enough: in the smoke run (1 restart) the k=3/seed-42 gap was **-6.51%** (median stalled at a worse local optimum). Best-of-5 turns that same point positive, which is why the headline uses best-of-restarts averaged over seeds.

### Restart-sensitivity check (k=3, seed=42)

| restarts | gap_pct |
|---|---|
| 3 | +4.17% |
| 5 | +4.17% |
| 10 | +4.17% |

The gap stays positive and close across restart budgets, so 5 restarts is not cherry-picked.

## 3. Runtime tradeoff

The centroid step is a weighted mean + one nearest-node snap (negligible). The median step scores every candidate with its own Dijkstra, so one pass costs ~N Dijkstra. Measured per-(k,seed) wall time, best-of-5:

| k | centroid (s) | median (s) | slowdown |
|---|---|---|---|
| 1 | 0.2 | 129 | 676x |
| 2 | 3.0 | 700 | 234x |
| 3 | 3.5 | 681 | 192x |
| 5 | 7.6 | 721 | 95x |

The median is accurate but scales far worse. For a real-time endpoint that matters; for a one-off audit run once, minutes-to-hours is irrelevant.

## 4. Approximation bound (probe 1)

On the heaviest cluster of the k=3 median solution (6799 demand nodes, weight 5,299,046), the demand-node-restricted median and the exact full-vertex (all 18,820 graph nodes) median are different nodes. Restricted per-resident = 7,267.3 m vs full-vertex 7,263.4 m: an objective gap of **0.053%**, with the two optima 21 m apart on the road network. So restricting candidates to demand nodes (the tractable shortcut over Hakimi's full-vertex scan) costs essentially nothing here -- the demand nodes are dense enough on the road graph to contain the true optimum or a near-tie.

## 5. Barrier failure mode (probe 2)

**Whole-territory case (k=1).** The single facility serves all of HK, so its cluster straddles Victoria Harbour. The population-weighted centroid snaps to (22.3496, 114.1539) and serves residents at 13,991 m each; the true median sits at (22.3270, 114.1781) -- nearer the cross-harbour road crossings -- at 12,597 m, a **11.06%** (1,394 m/resident) improvement. The centroid minimises straight-line spread and ignores that the harbour forces every cross-water trip through a handful of tunnels.

**Worst cluster found (k=2, cluster 1, 5220 nodes).** Centroid-snap at (22.4350, 114.0465): 12,771 m/resident. True median at (22.4438, 114.0160): 11,238 m/resident. Penalty **13.64%** (1,533 m/resident).

## 6. Recommendation

**Tolerance for a one-off coverage audit: 1%.** Justification: an audit is run once and is a deliverable whose credibility rests on reporting the true optimum, so runtime (minutes to a few hours, once) is nearly free and accuracy dominates. 1% sits below the demand-aggregation error and the seed-to-seed spread, so chasing below it would be false precision; above it, the reported coverage number is materially wrong.

**Observed gap (mean 4.15-11.06% across k) exceeds the 1% tolerance at every k.** Recommendation: **switch the audit's location step to the true graph 1-median (Maranzana).** It is the correct minimiser of the stated objective, it improves the reported per-resident coverage at every k (including the headline k=2 by ~5.6%), and the runtime cost is acceptable for a one-off run. This recommendation is scoped to the AUDIT deliverable; the real-time API endpoint is a separate decision (there the 95-676x slowdown is a real constraint) and production code is left unchanged pending explicit approval.

## What I should be ready to explain

- **Squared vs unsquared.** The centroid (mean) is the point that minimises the sum of *squared* distances -- it is the k-MEANS optimum and the solution to a least-squares problem. A k-MEDIAN minimises the sum of *unsquared* weighted distances, whose minimiser is the (geometric / graph) median, not the mean. Using the centroid inside k-median optimises the wrong loss; squaring over-weights far points, pulling the facility toward outliers instead of toward where most demand actually is.

- **Harbour, one sentence.** Because Victoria Harbour forces every cross-water trip onto a few tunnels, the straight-line centroid lands away from those crossings and serves the far shore badly, while the road-aware 1-median sits near a crossing.

- **Negative gaps / non-convexity.** Lloyd-type methods are local-optimum heuristics on a non-convex objective, so from a single shared start the median can converge to a worse local optimum than the centroid (we saw -6.51% at one init). That is initialisation luck, not evidence the centroid is better; averaging best-of-restarts over many seeds removes it, and then the median wins everywhere.

- **Lineage.** *Weiszfeld (1937)*: iterative algorithm for the continuous 1-median (Weber problem). *Hakimi (1964)*: on a network the 1-median (and p-median) optimum always lies at a vertex, so a discrete vertex search suffices -- we restrict candidates to demand-node vertices and bound that in probe 1. *Maranzana (1964)*: alternate location-allocation -- assign to nearest facility, relocate each to its cluster's 1-median, repeat; that is exactly our corrected solver. *Lloyd (1957/1982)*: the same alternation but with the centroid (mean) relocation -- k-means -- which is the production shortcut under audit.

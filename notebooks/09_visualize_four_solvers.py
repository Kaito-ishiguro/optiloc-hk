"""
Session 009 — Four-solver convergence visualization.

Reads the trails CSV produced by 08_solve_weber_weiszfeld.py and renders
a Folium map showing:
  - HK population heatmap (background context)
  - 4 convergence trails, one per solver, color-coded
  - Starting marker at Victoria Harbour
  - Gold star at the converged Mong Kok optimum
  - Title and legend baked into the HTML

The visual story: all four algorithms solve the same FONC equation
(grad f = 0) but take different paths and different step counts to get
there. Weiszfeld's trail is the elegant FONC-derived fixed-point;
Newton overshoots and corrects in 4 big steps; BFGS does 7 medium
steps; GD crawls in 255 tiny steps.
"""

import folium
import pandas as pd
from folium.plugins import HeatMap


# Visual encoding: each solver gets a distinct color + line style
SOLVER_STYLES = {
    "Weiszfeld": {"color": "#7F77DD", "weight": 4, "dash": None,    "label": "Weiszfeld (23 iters)"},
    "Newton":    {"color": "#E24B4A", "weight": 3, "dash": None,    "label": "Newton (4 iters)"},
    "BFGS":      {"color": "#1D9E75", "weight": 3, "dash": "8, 6",  "label": "BFGS (7 iters)"},
    "GD":        {"color": "#5F5E5A", "weight": 2, "dash": "4, 4",  "label": "GD (255 iters)"},
}


def main():
    print("Loading demand points and trails...")
    demand = pd.read_csv("data/processed/demand_points.csv")
    trails = pd.read_csv("data/processed/four_solver_trails.csv")
    summary = pd.read_csv("data/processed/solver_comparison.csv")
    print(f"  {len(demand):,} demand points, {len(trails):,} trail positions")

    # Center the map on Mong Kok (the optimum), tight zoom
    optimum = summary.iloc[0][["lon", "lat"]].to_numpy()
    start = trails[trails["iter"] == 0].iloc[0][["lon", "lat"]].to_numpy()

    m = folium.Map(
        location=[optimum[1], optimum[0]],
        zoom_start=13,
        tiles="CartoDB positron",
    )

    # Population heatmap layer (subtle, for context)
    heat_data = demand[["lat", "lon", "weight"]].to_numpy().tolist()
    HeatMap(
        heat_data,
        radius=8,
        blur=10,
        min_opacity=0.25,
        max_zoom=14,
    ).add_to(m)

    # One trail per solver
    for method, style in SOLVER_STYLES.items():
        trail = trails[trails["method"] == method].sort_values("iter")
        coords = trail[["lat", "lon"]].to_numpy().tolist()

        folium.PolyLine(
            locations=coords,
            color=style["color"],
            weight=style["weight"],
            opacity=0.85,
            dash_array=style["dash"],
            tooltip=style["label"],
        ).add_to(m)

        # Small dots at each iteration so the step count is visible
        for lat, lon in coords[1:-1]:
            folium.CircleMarker(
                location=[lat, lon],
                radius=2,
                color=style["color"],
                fill=True,
                fill_opacity=0.6,
                weight=0,
            ).add_to(m)

    # Starting marker
    folium.Marker(
        location=[start[1], start[0]],
        icon=folium.Icon(color="blue", icon="play", prefix="fa"),
        tooltip="Start: Victoria Harbour (114.17, 22.32)",
    ).add_to(m)

    # Gold star at the converged optimum
    folium.Marker(
        location=[optimum[1], optimum[0]],
        icon=folium.Icon(color="orange", icon="star", prefix="fa"),
        tooltip=f"Optimum: Mong Kok ({optimum[0]:.5f}, {optimum[1]:.5f})",
    ).add_to(m)

    # Title bar
    title_html = """
    <div style="
        position: fixed; top: 12px; left: 50%; transform: translateX(-50%);
        z-index: 9999; background: white; padding: 10px 18px;
        border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        font-family: -apple-system, sans-serif; font-size: 15px;
        font-weight: 500; color: #222; max-width: 600px; text-align: center;">
        Four solvers, one optimum &mdash; OptiLoc HK
        <div style="font-size: 12px; font-weight: 400; color: #666; margin-top: 4px;">
            Weiszfeld vs Newton vs BFGS vs Gradient Descent on the Weber problem (41,288 demand points)
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # Legend
    legend_rows = "".join(
        f'<div style="display:flex; align-items:center; margin: 4px 0;">'
        f'  <div style="width: 28px; height: 3px; background: {s["color"]}; '
        f'              margin-right: 8px; '
        + (f'background-image: linear-gradient(to right, {s["color"]} 60%, transparent 60%); background-size: 8px 3px;'
           if s["dash"] else "")
        + f'"></div>'
        f'  <span style="font-size: 12px; color: #222;">{s["label"]}</span>'
        f'</div>'
        for s in SOLVER_STYLES.values()
    )
    legend_html = f"""
    <div style="
        position: fixed; bottom: 24px; left: 12px; z-index: 9999;
        background: white; padding: 10px 14px; border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        font-family: -apple-system, sans-serif;">
        <div style="font-size: 13px; font-weight: 500; margin-bottom: 6px; color: #222;">
            Convergence trails
        </div>
        {legend_rows}
        <div style="margin-top: 8px; font-size: 11px; color: #666;">
            Start: Victoria Harbour &middot; Optimum: Mong Kok
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    out_path = "docs/maps/04_four_solvers_map.html"
    m.save(out_path)
    print(f"\nSaved {out_path}")
    print("Open it in a browser to inspect.")


if __name__ == "__main__":
    main()
"""
notebooks/13_visualize_ozp_constrained.py

Render the Session 010 comparison map on Folium:
    - HK demand-population heatmap (base)
    - 499 C + CDA zoning polygons as a translucent overlay
    - Three optima:
        gold star    Unconstrained (Mong Kok, Session 003)
        red dot      Kowloon-polygon constrained (Session 005)
        purple star  OZP-commercial constrained (Session 010)

Output: docs/maps/05_ozp_constrained_map.html
"""

import json
from pathlib import Path

import pandas as pd
import folium
from folium.plugins import HeatMap

ROOT = Path(__file__).parent.parent
DEMAND_PATH = ROOT / "data" / "processed" / "demand_points.csv"
UNION_PATH  = ROOT / "data" / "processed" / "ozp_commercial_union.geojson"
RESULT_PATH = ROOT / "data" / "processed" / "ozp_constrained_result.csv"
OUTPUT_PATH = ROOT / "docs" / "maps" / "05_ozp_constrained_map.html"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Known optima from prior sessions
UNCONSTRAINED = (114.17071, 22.33729)   # Session 003
KOWLOON_CONS  = (114.17323, 22.34038)   # Session 005


def main():
    print("Loading demand points ...")
    demand = pd.read_csv(DEMAND_PATH)
    print(f"  {len(demand):,} points")

    print("Loading OZP commercial union ...")
    with open(UNION_PATH, "r", encoding="utf-8") as f:
        ozp_geojson = json.load(f)

    print("Loading OZP-constrained result ...")
    res = pd.read_csv(RESULT_PATH).iloc[0]
    OZP_OPT = (float(res["lon"]), float(res["lat"]))
    print(f"  OZP optimum: lon={OZP_OPT[0]:.5f}, lat={OZP_OPT[1]:.5f}")

    # Center the map between the three optima so all are visible at zoom_start=13
    m = folium.Map(
        location=[22.335, 114.170],
        zoom_start=13,
        tiles="CartoDB positron",
    )

    # Heatmap
    print("Adding heatmap ...")
    HeatMap(
        data=demand[["lat", "lon", "weight"]].values.tolist(),
        radius=10,
        blur=15,
        min_opacity=0.3,
        max_zoom=14,
    ).add_to(m)

    # OZP commercial overlay (rendered above the heatmap so the feasible region is visible)
    print("Adding OZP commercial overlay ...")
    folium.GeoJson(
        ozp_geojson,
        name="Commercial / CDA zones",
        style_function=lambda _: {
            "fillColor": "#0ea5e9",
            "color":     "#0369a1",
            "weight":    0.5,
            "fillOpacity": 0.35,
        },
        tooltip="Commercial or CDA zoning (feasible region)",
    ).add_to(m)

    # Markers
    print("Adding optima markers ...")
    folium.Marker(
        location=[UNCONSTRAINED[1], UNCONSTRAINED[0]],
        icon=folium.Icon(color="orange", icon="star", prefix="fa"),
        popup="Unconstrained (Session 003)<br>Mong Kok / Prince Edward MTR",
        tooltip="Unconstrained optimum",
    ).add_to(m)

    folium.CircleMarker(
        location=[KOWLOON_CONS[1], KOWLOON_CONS[0]],
        radius=8,
        color="#dc2626",
        fill=True,
        fillColor="#dc2626",
        fillOpacity=0.9,
        popup="Kowloon-polygon constrained (Session 005)<br>Historical Kowloon boundary",
        tooltip="Kowloon-constrained optimum",
    ).add_to(m)

    folium.Marker(
        location=[OZP_OPT[1], OZP_OPT[0]],
        icon=folium.Icon(color="purple", icon="star", prefix="fa"),
        popup=(f"OZP-commercial constrained (Session 010)<br>"
               f"lon={OZP_OPT[0]:.5f}, lat={OZP_OPT[1]:.5f}"),
        tooltip="OZP-constrained optimum",
    ).add_to(m)

    # Title + legend overlays
    title_html = """
    <div style="position: fixed; top: 12px; left: 60px; z-index: 9999;
        background: rgba(255,255,255,0.92); padding: 10px 14px;
        border: 1px solid #cbd5e1; border-radius: 6px;
        font-family: 'Helvetica Neue', sans-serif; font-size: 13px;
        max-width: 420px;">
      <div style="font-weight: 700; font-size: 15px; margin-bottom: 4px;">
        OptiLoc HK &middot; Session 010
      </div>
      <div>Weber facility location with realistic zoning constraints
      (Outline Zoning Plans &mdash; C + CDA only, 10.3 km<sup>2</sup>,
      499 disjoint polygons).</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    legend_html = """
    <div style="position: fixed; bottom: 24px; left: 24px; z-index: 9999;
        background: rgba(255,255,255,0.95); padding: 10px 14px;
        border: 1px solid #cbd5e1; border-radius: 6px;
        font-family: 'Helvetica Neue', sans-serif; font-size: 12px;">
      <div style="font-weight: 700; margin-bottom: 6px;">Optima</div>
      <div style="margin-bottom: 4px;">
        <span style="color: #ea580c; font-size:14px;">&#9733;</span>
        Unconstrained (Mong Kok, Session 003)
      </div>
      <div style="margin-bottom: 4px;">
        <span style="color: #dc2626; font-size:14px;">&#9679;</span>
        Kowloon polygon (Session 005)
      </div>
      <div style="margin-bottom: 8px;">
        <span style="color: #7c3aed; font-size:14px;">&#9733;</span>
        OZP commercial (Session 010)
      </div>
      <div style="border-top: 1px solid #cbd5e1; padding-top: 6px;">
        <span style="display:inline-block; width:14px; height:10px;
            background:#0ea5e9; opacity:0.4;
            border:1px solid #0369a1; vertical-align:middle;"></span>
        C + CDA zones
      </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    print(f"\nSaving to {OUTPUT_PATH} ...")
    m.save(str(OUTPUT_PATH))
    print("Done. Open the HTML in a browser to view.")


if __name__ == "__main__":
    main()
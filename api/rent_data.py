# RVD Private Flatted Factories — Average Rents
# Source: http://www.rvd.gov.hk/datagovhk/4.1Q(from_99).csv
# Quarter: Q4 2025 (10-12/2025), confirmed non-preliminary
# Unit: HK$/sqm/month
# Granularity: 3 macro-regions only (RVD does not publish district-level rent)

REGIONAL_RENT = {
    "Hong Kong": 186,   # HK Island
    "Kowloon": 218,
    "New Territories": 164,
}

# District → region mapping
DISTRICT_REGION = {
    "Central & Western": "Hong Kong",
    "Eastern": "Hong Kong",
    "Southern": "Hong Kong",
    "Wan Chai": None,           # EXCLUDED — zero industrial stock (RVD 2024)
    "Yau Tsim Mong": "Kowloon",
    "Sham Shui Po": "Kowloon",
    "Kowloon City": "Kowloon",
    "Wong Tai Sin": "Kowloon",
    "Kwun Tong": "Kowloon",
    "Kwai Tsing": "New Territories",
    "Tsuen Wan": "New Territories",
    "Tuen Mun": "New Territories",
    "Yuen Long": "New Territories",
    "North": "New Territories",
    "Tai Po": "New Territories",
    "Sha Tin": None,             # EXCLUDED — zero vacancy despite 1M+ sqm stock (RVD 2024)
    "Sai Kung": "New Territories",
    "Islands": None,             # EXCLUDED — near-zero stock, zero vacancy (RVD 2024)
}

D_REF_M = 10_000  # reference scale for normalisation: ~HK-wide baseline mean distance

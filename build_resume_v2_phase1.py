#!/usr/bin/env python3
"""Phase 1: Delete the 5 paragraphs we don't need in v2."""

import json, subprocess, sys

DOC_ID = "1qwi152UWdKt_EFZ5_8wihsLG-ibbwsNkcjbnE2xrAew"

# Deletions ordered highest-to-lowest startIndex
deletions = [
    (1894, 2032),   # Company 2 bullet 3
    (1127, 1333),   # Company 1 bullet 5
    (979, 1127),    # Company 1 bullet 4
    (889, 979),     # Company 1 bullet 3
    (191, 223),     # Second title line (Lead Business Analyst)
]

requests = []
for start, end in deletions:
    requests.append({
        "deleteContentRange": {
            "range": {
                "startIndex": start,
                "endIndex": end
            }
        }
    })

batch = {"requests": requests}
with open("/tmp/v2_phase1_batch.json", "w") as f:
    json.dump(batch, f, indent=2)

print(f"Generated {len(requests)} deletion requests")
print("Ranges (highest to lowest):")
for s, e in deletions:
    print(f"  [{s}-{e}] (removes {e-s} chars)")

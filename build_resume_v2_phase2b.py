#!/usr/bin/env python3
"""
Phase 2b: Insert Droneconia CTO station and M.Sc. degree line.
Operations ordered: M.Sc. first (higher index 2158), Droneconia second (lower index 1432).
"""

import json

DOC_ID = "1qwi152UWdKt_EFZ5_8wihsLG-ibbwsNkcjbnE2xrAew"

TAB_STOPS = [
    {"alignment": "START", "offset": {"magnitude": 56.7, "unit": "PT"}},
    {"alignment": "END",   "offset": {"magnitude": 525.15, "unit": "PT"}}
]

def para_style_with_tabs():
    # tabStops cannot be set via updateParagraphStyle fields mask;
    # inserted paragraphs inherit tab stops from surrounding paragraphs.
    return {
        "namedStyleType": "NORMAL_TEXT"
    }

def text_style(bold=False, italic=False, small_caps=False, size_pt=11):
    s = {"fontSize": {"magnitude": size_pt, "unit": "PT"}}
    if bold is not None:     s["bold"] = bold
    if italic:               s["italic"] = True
    if small_caps:           s["smallCaps"] = True
    return s

def range_(s, e):
    return {"startIndex": s, "endIndex": e}

requests = []

# ── M.SC. LINE INSERTION (at index 2158, before education bullet) ──────────
# Text: "Master of Science in Mechanical Engineering\t2018\n" = 49 chars
# After insertion: [2158-2207)
MSC_TEXT = "Master of Science in Mechanical Engineering\t2018\n"
MSC_START = 2158
MSC_END   = MSC_START + len(MSC_TEXT)   # 2207

# Character breakdown (relative to MSC_START):
# [0-43)  = "Master of Science in Mechanical Engineering"  (43 chars)
# [43-44) = "\t"
# [44-48) = "2018"
# [48-49) = "\n"
MSC_DEGREE_END = MSC_START + 43   # 2201
MSC_TAB_END    = MSC_START + 44   # 2202
MSC_DATE_END   = MSC_START + 48   # 2206

requests += [
    # 1. Insert M.Sc. text
    {"insertText": {
        "location": {"index": MSC_START},
        "text": MSC_TEXT
    }},
    # 2. Remove any inherited bullet
    {"deleteParagraphBullets": {
        "range": range_(MSC_START, MSC_END)
    }},
    # 3. Apply paragraph style (tab stops, no indentation)
    {"updateParagraphStyle": {
        "range": range_(MSC_START, MSC_END),
        "paragraphStyle": para_style_with_tabs(),
        "fields": "namedStyleType,indentFirstLine,indentStart"
    }},
    # 4. Text style: degree name — bold + italic + 11pt
    {"updateTextStyle": {
        "range": range_(MSC_START, MSC_DEGREE_END),
        "textStyle": text_style(bold=True, italic=True),
        "fields": "bold,italic,fontSize,smallCaps"
    }},
    # 5. Text style: \t — bold + smallCaps + 11pt
    {"updateTextStyle": {
        "range": range_(MSC_DEGREE_END, MSC_TAB_END),
        "textStyle": text_style(bold=True, small_caps=True),
        "fields": "bold,fontSize,smallCaps"
    }},
    # 6. Text style: date "2018" — bold + 11pt
    {"updateTextStyle": {
        "range": range_(MSC_TAB_END, MSC_DATE_END),
        "textStyle": text_style(bold=True),
        "fields": "bold,italic,fontSize,smallCaps"
    }},
]

# ── DRONECONIA CTO STATION INSERTION (at index 1432) ──────────────────────
# Full text breakdown (321 chars total):
#   Line 1: "DRONECONIA LLC (NOW MULTI AI)\tAustin, TX\n"  = 41 chars
#   Line 2: "Co-Founder & CTO\tNov 2021\u2013Sep 2022\n"   = 35 chars
#   Line 3: "\n"                                           =  1 char (2pt spacer)
#   Line 4: <bullet 1>\n                                   = 106 chars
#   Line 5: <bullet 2>\n                                   = 137 chars
#   Line 6: "\n"                                           =  1 char (8pt spacer)

B1 = ("Designed and implemented the initial multi-agent AI architecture "
      "for autonomous UAV/UGV mission planning.")
B2 = ("Secured and delivered an Air Force SBIR Phase I contract from "
      "AFWERX Agility Prime for decision-support AI under adversarial "
      "conditions.")

DRONE_TEXT = (
    "DRONECONIA LLC (NOW MULTI AI)\tAustin, TX\n"
    "Co-Founder & CTO\tNov 2021\u2013Sep 2022\n"
    "\n"
    + B1 + "\n"
    + B2 + "\n"
    "\n"
)

# Verify lengths
header_line = "DRONECONIA LLC (NOW MULTI AI)\tAustin, TX\n"
title_line  = "Co-Founder & CTO\tNov 2021\u2013Sep 2022\n"
spacer1     = "\n"
b1_line     = B1 + "\n"
b2_line     = B2 + "\n"
spacer2     = "\n"

assert len(DRONE_TEXT) == (len(header_line) + len(title_line) +
                            len(spacer1) + len(b1_line) + len(b2_line) + len(spacer2)), \
    f"Length mismatch: {len(DRONE_TEXT)}"

print(f"Droneconia text length: {len(DRONE_TEXT)} chars")
print(f"  Header line: {len(header_line)}")
print(f"  Title line:  {len(title_line)}")
print(f"  Bullet 1:    {len(b1_line)}")
print(f"  Bullet 2:    {len(b2_line)}")

DS = 1432  # Droneconia insert start

# Cumulative offsets
h_end  = DS + len(header_line)          # end of header para
t_end  = h_end + len(title_line)        # end of title para
s1_end = t_end + 1                      # end of 2pt spacer
b1_end = s1_end + len(b1_line)          # end of bullet 1 para
b2_end = b1_end + len(b2_line)          # end of bullet 2 para
s2_end = b2_end + 1                     # end of 8pt spacer (= DS + len(DRONE_TEXT))

print(f"  Paragraphs after insertion:")
print(f"    Header:   [{DS}-{h_end})")
print(f"    Title:    [{h_end}-{t_end})")
print(f"    2pt spac: [{t_end}-{s1_end})")
print(f"    Bullet1:  [{s1_end}-{b1_end})")
print(f"    Bullet2:  [{b1_end}-{b2_end})")
print(f"    8pt spac: [{b2_end}-{s2_end})")

# Sub-ranges within header line
# "DRONECONIA LLC (NOW MULTI AI)\t" = 30 chars
# "Austin, TX"                       = 10 chars
# "\n"                               = 1 char
company_tab_end = DS + 30      # end of "DRONECONIA LLC (NOW MULTI AI)\t"
location_end    = DS + 40      # end of "Austin, TX"

# Sub-ranges within title line (starts at h_end)
# "Co-Founder & CTO" = 16 chars
# "\t"               = 1 char
# "Nov 2021–Sep 2022" = 17 chars
# "\n"               = 1 char
t_name_end  = h_end + 16
t_tab_end   = h_end + 17
t_date_end  = h_end + 34
t_nl_end    = h_end + 35   # = t_end

requests += [
    # 7. Insert Droneconia text
    {"insertText": {
        "location": {"index": DS},
        "text": DRONE_TEXT
    }},
    # 8. Paragraph style: header (tab stops)
    {"updateParagraphStyle": {
        "range": range_(DS, h_end),
        "paragraphStyle": para_style_with_tabs(),
        "fields": "namedStyleType"
    }},
    # 9. Paragraph style: title (tab stops)
    {"updateParagraphStyle": {
        "range": range_(h_end, t_end),
        "paragraphStyle": para_style_with_tabs(),
        "fields": "namedStyleType"
    }},
    # 10. Text style: company+tab — bold + smallCaps + 11pt
    {"updateTextStyle": {
        "range": range_(DS, company_tab_end),
        "textStyle": text_style(bold=True, small_caps=True),
        "fields": "bold,fontSize,smallCaps,italic"
    }},
    # 11. Text style: location "Austin, TX" — bold + 11pt
    {"updateTextStyle": {
        "range": range_(company_tab_end, location_end),
        "textStyle": text_style(bold=True),
        "fields": "bold,fontSize,smallCaps,italic"
    }},
    # 12. Text style: title name "Co-Founder & CTO" — bold + 11pt
    {"updateTextStyle": {
        "range": range_(h_end, t_name_end),
        "textStyle": text_style(bold=True),
        "fields": "bold,fontSize,smallCaps,italic"
    }},
    # 13. Text style: \t in title — bold + smallCaps + 11pt
    {"updateTextStyle": {
        "range": range_(t_name_end, t_tab_end),
        "textStyle": text_style(bold=True, small_caps=True),
        "fields": "bold,fontSize,smallCaps"
    }},
    # 14. Text style: date "Nov 2021–Sep 2022" — bold + 11pt
    {"updateTextStyle": {
        "range": range_(t_tab_end, t_date_end),
        "textStyle": text_style(bold=True),
        "fields": "bold,fontSize,smallCaps,italic"
    }},
    # 15. Text style: 2pt spacer \n
    {"updateTextStyle": {
        "range": range_(t_end, s1_end),
        "textStyle": {"fontSize": {"magnitude": 2, "unit": "PT"}},
        "fields": "fontSize,bold"
    }},
    # 16. Paragraph style for both bullets: indentation + spacingMode
    {"updateParagraphStyle": {
        "range": range_(s1_end, b2_end),
        "paragraphStyle": {
            "indentFirstLine": {"magnitude": 18, "unit": "PT"},
            "indentStart":     {"magnitude": 36, "unit": "PT"},
            "spacingMode": "NEVER_COLLAPSE"
        },
        "fields": "indentFirstLine,indentStart,spacingMode"
    }},
    # 17. Create bullet list for both bullets
    {"createParagraphBullets": {
        "range": range_(s1_end, b2_end),
        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
    }},
    # 18. Text style: 8pt spacer \n
    {"updateTextStyle": {
        "range": range_(b2_end, s2_end),
        "textStyle": {"fontSize": {"magnitude": 8, "unit": "PT"}},
        "fields": "fontSize,bold"
    }},
]

batch = {"requests": requests}
with open("/tmp/v2_phase2b_batch.json", "w", encoding="utf-8") as f:
    json.dump(batch, f, ensure_ascii=False, indent=2)

print(f"\nTotal requests: {len(requests)}")

#!/usr/bin/env python3
"""Build Alexander Nettekoven's resume matching the ResumeWorded template style."""
import subprocess, json

# ── gws helpers ────────────────────────────────────────────────────────────────

def gws_call(args):
    r = subprocess.run(['gws'] + args, capture_output=True, text=True)
    out = '\n'.join(l for l in r.stdout.splitlines() if 'keyring' not in l.lower())
    if r.returncode != 0:
        raise RuntimeError(f"gws error:\n{r.stderr}")
    return json.loads(out) if out.strip() else {}

def batch_update(doc_id, requests):
    return gws_call(['docs', 'documents', 'batchUpdate',
                     '--params', json.dumps({"documentId": doc_id}),
                     '--json', json.dumps({"requests": requests})])

# ── Paragraph builders ─────────────────────────────────────────────────────────
# Template observations:
#   - All sa=0, sb=0 (no paragraph spacing anywhere)
#   - Default font: Times New Roman (from named style)
#   - Tab stops on org/title/edu lines: START@56.7, END@525.15 (right-aligns date/location)
#   - Bullet indent: 36pt
#   - Section headers: bold, border-bottom (width=0.75)
#   - Name: 16pt bold, centered
#   - Contact: 11pt, centered

BORDER_BOTTOM = {
    "color": {"color": {"rgbColor": {}}},  # black
    "dashStyle": "SOLID",
    "width": {"magnitude": 0.75, "unit": "PT"},
    "padding": {"magnitude": 1, "unit": "PT"},
}

def p(segs, align=None, indent=0, border=False, size=None):
    """Define a paragraph."""
    return {"segs": segs, "align": align, "indent": indent,
            "border": border, "size": size}

T  = lambda t: (t, False, False)
B  = lambda t: (t, True,  False)
I_ = lambda t: (t, False, True)
BI = lambda t: (t, True,  True)

# ── Resume paragraphs ──────────────────────────────────────────────────────────

PARAGRAPHS = [
    # Header
    p([B("Dr. Alexander Nettekoven")],
      align="CENTER", size=16),
    p([T("Austin, TX  •  alexkoven.inquiry@gmail.com  •  "
         "linkedin.com/in/alexander-nettekoven  •  github.com/alexkoven")],
      align="CENTER", size=11),

    # ── Research Experience ────────────────────────────────────────────────────
    p([B("PROFESSIONAL EXPERIENCE")], border=True),

    # Postdoc
    p([B("UNIVERSITY OF TEXAS AT AUSTIN"), B("  •  Austin, TX")]),
    p([B("Postdoctoral Fellow, Center for Autonomy"), B("  •  Jun 2025 – Present")]),
    p([T("Robot learning and real-world deployment; investigating sim-to-real "
         "transfer gap for general-purpose manipulation robots.")]),
    p([T("Benchmarked state-of-the-art VLA and World Action Model foundations "
         "(NVIDIA DreamZero 14B WAM vs. Physical Intelligence π0.5) for zero-shot "
         "deployment across 12 tasks in DROID/Isaac Sim/Lab")], indent=36),
    p([T("Investigating failure modes of current foundation models on low-cost "
         "household manipulation hardware; active research in sim-to-real gap")], indent=36),
    p([T("Affiliated with Texas Robotics; peer reviewer for ICRA, IROS, IEEE RA-L")], indent=36),

    # CEO
    p([B("MULTI AI, INC."), B("  •  San Francisco, CA / Austin, TX")]),
    p([B("CEO & Co-founder"), B("  •  Sep 2022 – Jun 2025")]),
    p([T("Built and led a defense AI startup from SBIR Phase I to seven-figure "
         "Pentagon contracts, developing multi-agent AI for autonomous vehicle coordination.")]),
    p([T("Built multi-agent coordination platform combining decentralized MCTS and "
         "generative AI for theater-scale military logistics; 38% improvement in "
         "resource delivery under disrupted scenarios in field tests")], indent=36),
    p([T("Secured $1M+ in government contracts: Air Force Phase II/III SBIR, "
         "AFWERX TACFI, and Pentagon sole-source wargaming contract (OUSD A&S)")], indent=36),
    p([T("Grew company from SBIR startup to Pentagon partnership within 2 years; "
         "led technical roadmap, fundraising, and engineering team")], indent=36),

    # CTO
    p([B("DRONECONIA LLC  (→ Multi AI, Inc.)"), B("  •  Austin, TX")]),
    p([B("CTO & Co-founder"), B("  •  Nov 2021 – Sep 2022")]),
    p([T("Architected autonomous mission-planning AI for unmanned aerial and ground "
         "vehicles; won Air Force SBIR Phase I award from Air Force Agility Prime")], indent=36),

    # PhD
    p([B("UNIVERSITY OF TEXAS AT AUSTIN"), B("  •  Austin, TX")]),
    p([B("PhD Researcher, Autonomous Systems Group"), B("  •  Jan 2019 – Dec 2022")]),
    p([T("NSF-funded robotics researcher; developed the world's first aerial 3D printing "
         "system and novel navigation methods for autonomous robots.")]),
    p([T("Developed the world's first 3D printing hexacopter capable of in-flight "
         "thermoplastic (FDM) deposition; positioning accuracy exceeded ~50% of "
         "ground-based large-scale 3D printers")], indent=36),
    p([T("Designed and commissioned the Texas Robotics Motion Capture Space; "
         "led summer research program for 17 undergraduates; mentored 7 undergraduate RAs")], indent=36),
    p([T("Published 7 peer-reviewed papers at ICUAS, IROS, ICMLA, IEEE CDC, "
         "SFF Symposium (2018–2022)")], indent=36),

    # ── Education ─────────────────────────────────────────────────────────────
    p([B("EDUCATION")], border=True),

    p([B("UNIVERSITY OF TEXAS AT AUSTIN"), B("  •  Austin, TX")]),
    p([BI("Ph.D., Mechanical Engineering (Robotics)"), B("  •  2019–2022")]),

    p([B("UNIVERSITY OF TEXAS AT AUSTIN"), B("  •  Austin, TX")]),
    p([BI("M.Sc., Mechanical Engineering"), B("  •  2016–2018")]),

    p([B("RWTH AACHEN UNIVERSITY"), B("  •  Aachen, Germany")]),
    p([BI("B.Sc., Mechanical Engineering"), B("  •  2011–2016")]),

    # ── Additional Information ─────────────────────────────────────────────────
    p([B("ADDITIONAL INFORMATION")], border=True),
    p([T("Technical Skills: Python, ROS, Isaac Sim/Lab, PyTorch, C++, MATLAB")], indent=36),
    p([T("Research Areas: Vision-Language-Action (VLA) Models, World Action Models, "
         "Sim-to-Real Transfer, Robot Manipulation")], indent=36),
    p([T("Awards: Air Force TACFI (7-fig.), Pentagon Wargaming Contract, Phase II/III SBIR, "
         "GAIN ME Dept. Award, NSF CPS Researcher")], indent=36),
    p([T("Publications: 7 peer-reviewed papers (ICUAS, IROS, ICMLA, IEEE CDC, SFF); "
         "Reviewer: ICRA, IROS, IEEE RA-L")], indent=36),
    p([T("Languages: German (native), English (fluent)")], indent=36),
]

# ── Build full text ────────────────────────────────────────────────────────────

def para_text(para):
    return "".join(t for t, *_ in para["segs"]) + "\n"

full_text = "".join(para_text(p) for p in PARAGRAPHS)

# ── Create doc and insert text ─────────────────────────────────────────────────

print("Creating document...")
doc = gws_call(['docs', 'documents', 'create',
                '--json', '{"title": "Alexander Nettekoven — Resume"}'])
doc_id = doc['documentId']
print(f"  Doc ID: {doc_id}")

print("Inserting text...")
batch_update(doc_id, [{"insertText": {"location": {"index": 1}, "text": full_text}}])

# ── Build formatting requests ──────────────────────────────────────────────────

fmt = []

# 1. Document margins (match template: top/bottom=27, left/right=43.2)
fmt.append({"updateDocumentStyle": {
    "documentStyle": {
        "marginTop":    {"magnitude": 27,   "unit": "PT"},
        "marginBottom": {"magnitude": 27,   "unit": "PT"},
        "marginLeft":   {"magnitude": 43.2, "unit": "PT"},
        "marginRight":  {"magnitude": 43.2, "unit": "PT"},
    },
    "fields": "marginTop,marginBottom,marginLeft,marginRight"
}})

# 2. Per-paragraph formatting
pos = 1
for para in PARAGRAPHS:
    segs   = para["segs"]
    ptext  = para_text(para)
    plen   = len(ptext)
    pend   = pos + plen

    # Paragraph style — always zero out spacing to match template
    ps = {
        "spaceAbove": {"magnitude": 0, "unit": "PT"},
        "spaceBelow": {"magnitude": 0, "unit": "PT"},
    }
    pf = ["spaceAbove", "spaceBelow"]

    if para["align"]:
        ps["alignment"] = para["align"]; pf.append("alignment")
    if para["indent"]:
        ps["indentStart"] = {"magnitude": para["indent"], "unit": "PT"}
        pf.append("indentStart")
    if para["border"]:
        ps["borderBottom"] = BORDER_BOTTOM; pf.append("borderBottom")

    if pf:
        fmt.append({"updateParagraphStyle": {
            "range": {"startIndex": pos, "endIndex": pend},
            "paragraphStyle": ps, "fields": ",".join(pf)
        }})

    # Font size override (name=16, contact=11, rest inherit named style)
    if para["size"]:
        fmt.append({"updateTextStyle": {
            "range": {"startIndex": pos, "endIndex": pend - 1},
            "textStyle": {"fontSize": {"magnitude": para["size"], "unit": "PT"}},
            "fields": "fontSize"
        }})

    # Per-segment bold/italic
    seg_pos = pos
    for text, bold, italic in segs:
        slen = len(text)
        if slen > 0 and (bold or italic):
            ts = {}; tf = []
            if bold:   ts["bold"]   = True; tf.append("bold")
            if italic: ts["italic"] = True; tf.append("italic")
            fmt.append({"updateTextStyle": {
                "range": {"startIndex": seg_pos, "endIndex": seg_pos + slen},
                "textStyle": ts, "fields": ",".join(tf)
            }})
        seg_pos += slen

    pos = pend

# ── Apply formatting in batches ────────────────────────────────────────────────

print(f"Applying {len(fmt)} formatting requests...")
BATCH = 50
for i in range(0, len(fmt), BATCH):
    batch_update(doc_id, fmt[i:i+BATCH])
    print(f"  Applied {i+1}–{min(i+BATCH, len(fmt))}")

print(f"\n✓ Done: https://docs.google.com/document/d/{doc_id}/edit")

#!/usr/bin/env python3
"""
Phase 2a: All text replacements for v2.
Processes from highest to lowest startIndex to avoid index-shift collisions.
Each op: (start, end, new_text) → deleteContentRange[start,end) then insertText at start.
"""

import json, subprocess, sys

DOC_ID = "1qwi152UWdKt_EFZ5_8wihsLG-ibbwsNkcjbnE2xrAew"

# π, π0, π0.5 unicode
PI     = "\u03c0"
EN_DASH = "\u2013"
BULLET  = "\u2022"
LDQUO  = "\u2018"
RDQUO  = "\u2019"
APOS   = "\u2019"

# All ops: (startIndex, endIndex_exclusive, new_text)
# Ordered HIGHEST startIndex to LOWEST — do NOT reorder.
ops = [

    # ── ADDITIONAL INFORMATION ─────────────────────────────────────────────
    # Awards line [2779-2880]: run [2779-2879] + \n
    (2779, 2879,
     "Awards: Air Force SBIR Phase I/II/III & TACFI (2021\u20132024); "
     "NSF CPS Researcher (2019\u20132022); GAIN ME Award (2021)"),

    # Certifications line [2702-2779]: run [2702-2778] + \n
    (2702, 2778,
     "Languages: German (native), English (fluent)  |  "
     "Peer Reviewer: ICRA, IROS, IEEE RA-L (2021\u2013present)"),

    # Languages line [2617-2702]: runs [...2701] + \n
    (2617, 2701,
     "VLA & Foundation Models: \u03c00.5, SmolVLA, DreamZero, ACT, Diffusion Policies"),

    # Technical Skills line [2525-2617]: runs [...2616] + \n
    (2525, 2616,
     "Technical Skills: Python, C++, PyTorch, ROS2, Isaac Sim/Isaac Lab, Git"),

    # ── RWTH AACHEN (BSc) ──────────────────────────────────────────────────
    # BSc bullet [2304-2500]: run [2304-2499] + \n
    (2304, 2499,
     "Exchange Research Scholar, Barton Research Group, "
     "University of Michigan, Ann Arbor (2014\u20132015)"),

    # BSc degree line [2221-2304] — per-run replacements:
    #   date run [2294-2303]: "2007-2011"
    (2294, 2303, "2016"),
    #   degree name run [2221-2293]: "Bachelor of Engineering, Major in..."
    (2221, 2293, "B.Sc. in Mechanical Engineering"),

    # RWTH header [2183-2221] — per-run:
    #   location run [2208-2220]: "New York, NY"
    (2208, 2220, "Aachen, Germany"),
    #   company+tab run [2183-2208]: "RESUME WORDED UNIVERSITY\t"
    (2183, 2208, "RWTH AACHEN UNIVERSITY\t"),

    # ── THE UNIVERSITY OF TEXAS AT AUSTIN (Education) ──────────────────────
    # Education bullet [2088-2182]: run [2088-2181] + \n
    (2088, 2181,
     "NSF CPS Researcher (2019\u20132022)  |  Advisor: Prof. Ufuk Topcu"),

    # PhD degree line [2013-2088] — per-run:
    #   date run [2078-2087]: "2011-2012"
    (2078, 2087, "2022"),
    #   degree name run [2013-2077]: "Master of Science in Management..."
    (2013, 2077, "Doctor of Philosophy in Mechanical Engineering"),

    # UT Austin education header [1976-2013] — per-run:
    #   location run [1995-2012]: "San Francisco, CA"
    (1995, 2012, "Austin, TX"),
    #   university+tab run [1976-1995]: "LEGENDS UNIVERSITY\t"
    (1976, 1995, "THE UNIVERSITY OF TEXAS AT AUSTIN\t"),

    # ── COMPANY 3 (UT Austin Autonomous Systems Group / PhD) ───────────────
    # PhD bullet 2 [1874-1964]: run [1874-1963] + \n
    (1874, 1963,
     "Designed and commissioned the Texas Robotics Motion Capture Space; "
     "peer reviewer for ICRA, IROS, and IEEE RA-L (2021\u2013present); "
     "mentored 20+ undergraduate researchers."),

    # PhD bullet 1 [1689-1874]: run [1689-1873] + \n
    (1689, 1873,
     "Built the world\u2019s first aerial 3D printing hexacopter capable of "
     "in-flight FDM deposition (NSF CPS, Prof. Ufuk Topcu); "
     "published at IROS, ICUAS, IEEE CDC, ICMLA, and the SFF Symposium."),

    # PhD intro [1495-1689]: single run including \n → delete [1495-1688)
    (1495, 1688,
     "Graduate research in autonomous systems and formal methods; "
     "part of an NSF Cyber-Physical Systems (CPS) project spanning "
     "Caltech, UC Berkeley, Northeastern, and RPI."),

    # Company 3 title line [1452-1494] — per-run:
    #   date run [1484-1493]: "2012-2013"
    (1484, 1493, "Jan 2019\u2013Dec 2022"),
    #   title run [1452-1483]: "Business Development Consultant"
    (1452, 1483, "NSF-Supported Robotics Researcher"),

    # Company 3 header [1419-1452] — per-run:
    #   location run [1439-1451]: "New York, NY"
    (1439, 1451, "Austin, TX"),
    #   company+tab run [1419-1439]: "MY EXCITING COMPANY\t"
    (1419, 1439, "UT AUSTIN AUTONOMOUS SYSTEMS GROUP\t"),

    # ── COMPANY 2 (Multi AI, Inc. / CEO) ───────────────────────────────────
    # Multi AI bullet 2 [1328-1418]: run [1328-1417] + \n
    (1328, 1417,
     "Owned full AI development lifecycle\u2014architecture design through "
     "government delivery\u2014growing from PhD-stage prototype to "
     "Pentagon-contracted product."),

    # Multi AI bullet 1 [1122-1328]: run [1122-1327] + \n
    (1122, 1327,
     "Platform outperformed baseline by 38% on key delivery metrics "
     "in field evaluations under disrupted conditions; secured Air Force "
     "SBIR Phase II/III contracts and TACFI award."),

    # Multi AI intro [911-1121]: single run including \n → delete [911-1120)
    (911, 1120,
     "Built a multi-agent AI platform coupling decentralized Monte Carlo "
     "Tree Search (MCTS) with generative AI for adaptive decision-making "
     "under adversarial and communications-degraded conditions."),

    # Company 2 title line [883-910] — per-run:
    #   date run [900-909]: "2013-2015"
    (900, 909, "Sep 2022\u2013Jun 2025"),
    #   title run [883-899]: "Business Analyst"
    (883, 899, "Co-Founder & CEO"),

    # Company 2 header [858-883] — per-run:
    #   location run [868-882]: "Beijing, China"
    (868, 882, "Austin, TX"),
    #   company+tab run [858-868]: "INSTAMAKE\t"
    (858, 868, "MULTI AI, INC.\t"),

    # ── COMPANY 1 (Center for Autonomy, UT Austin / Postdoc) ───────────────
    # Postdoc bullet 2 [695-857]: run [695-856] + \n
    (695, 856,
     "Build and deploy learned policies on a low-cost bimanual manipulator "
     "for real-world evaluation; architectures include ACT, diffusion "
     "policies, SmolVLA, and \u03c00/\u03c00.5."),

    # Postdoc bullet 1 [510-695]: run [510-694] + \n
    (510, 694,
     "Benchmarked NVIDIA DreamZero (14B World Action Model) vs. "
     "Physical Intelligence\u2019s \u03c00.5 across zero-shot manipulation "
     "tasks in standardized suites using Isaac Sim/Lab; developed "
     "sim-to-real evaluation frameworks."),

    # Postdoc intro [192-509]: single run including \n → delete [192-508)
    (192, 508,
     "Research focuses on zero-shot evaluation and benchmarking of robot "
     "foundation models, including Vision-Language-Action (VLA) models "
     "and World Action Models (WAMs), across standardized manipulation "
     "task suites."),

    # Title line [162-191] — per-run:
    #   date run [178-190]: "2017-Present"
    (178, 190, "Jun 2025\u2013Present"),
    #   title run [162-177]: "Product Manager"
    (162, 177, "Postdoctoral Fellow (affiliated with Texas Robotics)"),

    # Company 1 header [131-162] — per-run:
    #   location run [149-161]: "New York, NY"
    (149, 161, "Austin, TX"),
    #   company+tab run [131-149]: "RESUME WORDED CO.\t"
    (131, 149, "CENTER FOR AUTONOMY, UT AUSTIN\t"),

    # ── HEADER ─────────────────────────────────────────────────────────────
    # Contact line [13-105]: delete [13-104)
    (13, 104,
     "Austin, TX  \u2022  nettekoven@utexas.edu  \u2022  "
     "linkedin.com/in/alexander-nettekoven  \u2022  github.com/alexkoven"),

    # Name [1-13]: run [1-12] + \n → delete [1-12)
    (1, 12, "Alexander Nettekoven"),
]

# Build batchUpdate requests
requests = []
for (start, end, text) in ops:
    requests.append({
        "deleteContentRange": {
            "range": {"startIndex": start, "endIndex": end}
        }
    })
    requests.append({
        "insertText": {
            "location": {"index": start},
            "text": text
        }
    })

batch = {"requests": requests}
with open("/tmp/v2_phase2a_batch.json", "w", encoding="utf-8") as f:
    json.dump(batch, f, ensure_ascii=False, indent=2)

print(f"Generated {len(requests)} requests ({len(ops)} delete+insert pairs)")
print(f"Total chars to delete: {sum(e-s for s,e,_ in ops)}")
print(f"Total chars to insert: {sum(len(t) for _,_,t in ops)}")

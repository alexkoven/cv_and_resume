"""
Extract resume content library from all .docx resume files.

Reads every resume, groups paragraphs by section, deduplicates bullets
across files, and writes a single markdown content library.
"""

import sys
from pathlib import Path
from docx import Document

# ── Config ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
APPLICATIONS_DIR = REPO_ROOT / "Applications"

# Resumes to include (exclude cover letters, old/Zzz_old drafts)
RESUME_GLOBS = [
    "Alex Nettekoven_Current_Resume.docx",
    "Applications/20260328_Google_DeepMind_Application/Alex Nettekoven Resume Robotics -v5.docx",
    "Applications/20260403_Figure_Application/Alex Nettekoven Resume Figure-Agentic-Systems-v1.docx",
    "Applications/20260403_Figure_Application/Alex Nettekoven Resume Figure-Robot-Learning-v3.docx",
    "Applications/20260404_physical_intelligence/Alex Nettekoven Resume PI-Controls-Engineer-v1.docx",
    "Applications/20260404_physical_intelligence/Alex Nettekoven Resume PI-Robot-Learning-v1.docx",
    "Applications/20260405_DYNA_Application/Alex Nettekoven Resume DYNA-Controls-Engineer-v1.docx",
    "Applications/20260405_DYNA_Application/Alex Nettekoven Resume DYNA-Research-Engineer-v1.docx",
    "Applications/20260405_Foundation_Robotics_Application/Alex Nettekoven Resume Foundation-Robot-Learning-v1.docx",
]

OUTPUT = REPO_ROOT / "resume_template.md"

# ── Helpers ───────────────────────────────────────────────────────────────────

def is_section_heading(text: str) -> bool:
    """True if the paragraph looks like a section heading.

    Heuristic: all-caps, short (≤60 chars), no trailing punctuation that
    would indicate it's a bullet or sentence.
    """
    t = text.strip()
    if not t:
        return False
    # Must be all uppercase and reasonably short
    if t != t.upper() or len(t) > 60:
        return False
    # Exclude lines that are just contact info (contain @ or •)
    if "@" in t or "•" in t or "linkedin" in t.lower():
        return False
    return True


def normalize(text: str) -> str:
    """Collapse whitespace and normalize dashes for deduplication comparison."""
    t = " ".join(text.split())
    # Treat en-dash and em-dash as regular hyphen for comparison purposes
    t = t.replace("\u2013", "-").replace("\u2014", "-")
    return t


def extract_sections(path: Path) -> dict[str, list[str]]:
    """Return {section_name: [paragraph_text, ...]} for one docx file."""
    doc = Document(path)
    sections: dict[str, list[str]] = {}
    current_section = "Header"

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        if is_section_heading(text):
            current_section = text.title()
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections.setdefault(current_section, []).append(text)

    return sections


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    # Collect sections from all resumes
    all_sections: dict[str, list[tuple[str, str]]] = {}  # section → [(text, source)]

    for rel_path in RESUME_GLOBS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            print(f"  MISSING: {rel_path}", file=sys.stderr)
            continue

        label = path.stem
        print(f"Reading: {label}")
        sections = extract_sections(path)

        for section, paragraphs in sections.items():
            all_sections.setdefault(section, [])
            for p in paragraphs:
                all_sections[section].append((p, label))

    # Deduplicate within each section (keep first occurrence)
    deduped: dict[str, list[str]] = {}
    for section, entries in all_sections.items():
        seen: set[str] = set()
        unique: list[str] = []
        for text, _source in entries:
            key = normalize(text)
            if key not in seen:
                seen.add(key)
                unique.append(text)
        deduped[section] = unique

    # Write markdown
    lines: list[str] = [
        "# Resume Content Library\n",
        "All unique resume content extracted from past applications.\n",
        "Use this as the source for tailoring copies of the master resume.\n",
        "",
    ]

    # Preferred section order (matches actual ALL-CAPS headings, title-cased here)
    order = [
        "Header", "Summary", "Professional Experience", "Education",
        "Publication Record", "Additional Information", "Skills",
        "Projects", "Awards", "Certifications",
    ]
    remaining = [s for s in deduped if s not in order]

    for section in order + remaining:
        if section not in deduped:
            continue
        lines.append(f"## {section}\n")
        for item in deduped[section]:
            # Multi-line items (e.g. job titles with dates) stay as paragraphs;
            # short items that read like bullets get a dash prefix.
            if item.startswith("- ") or item.startswith("• "):
                lines.append(item)
            elif len(item) < 120 and not item.endswith("."):
                lines.append(f"- {item}")
            else:
                lines.append(f"- {item}")
        lines.append("")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote: {OUTPUT}")
    print(f"Sections: {list(deduped.keys())}")
    print(f"Total unique items: {sum(len(v) for v in deduped.values())}")


if __name__ == "__main__":
    main()

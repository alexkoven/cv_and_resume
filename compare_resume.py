"""
Compare a tailored resume .docx against its base standard template.

Usage:
    python scripts/compare_resume.py <tailored.docx> [base.docx]

If base.docx is omitted the script infers it from the tailored filename:
  - names containing "VLA"  → Alex Nettekoven Resume VLA-Standard.docx
  - names containing "RL"   → Alex Nettekoven Resume RL-Controls-Standard.docx
  - otherwise               → Alex Nettekoven Resume VLA-Standard.docx (default)

Output: paragraph-level diff with inline word-level highlights.
Exit code 0 when diffs were found, 1 when the files are identical.
"""

import sys
import difflib
from pathlib import Path
from docx import Document

# ANSI colour codes (auto-disabled when stdout is not a tty)
def _supports_colour() -> bool:
    return sys.stdout.isatty()

RED    = "\033[31m" if _supports_colour() else ""
GREEN  = "\033[32m" if _supports_colour() else ""
YELLOW = "\033[33m" if _supports_colour() else ""
BOLD   = "\033[1m"  if _supports_colour() else ""
RESET  = "\033[0m"  if _supports_colour() else ""

REPO_ROOT = Path(__file__).resolve().parent.parent


def _infer_base(tailored: Path) -> Path:
    name = tailored.stem.upper()
    if "RL" in name or "RL-CONTROLS" in name:
        candidate = "Alex Nettekoven Resume RL-Controls-Standard.docx"
    else:
        candidate = "Alex Nettekoven Resume VLA-Standard.docx"
    return REPO_ROOT / candidate


def _paragraphs(path: Path) -> list[str]:
    doc = Document(str(path))
    return [p.text for p in doc.paragraphs]


def _word_diff(base_line: str, tail_line: str) -> str:
    """Return a single line showing removed/added words inline."""
    base_words = base_line.split()
    tail_words = tail_line.split()
    sm = difflib.SequenceMatcher(None, base_words, tail_words, autojunk=False)
    parts: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            parts.append(" ".join(base_words[i1:i2]))
        elif tag == "replace":
            parts.append(RED + "[-" + " ".join(base_words[i1:i2]) + "-]" + RESET)
            parts.append(GREEN + "[+" + " ".join(tail_words[j1:j2]) + "+]" + RESET)
        elif tag == "delete":
            parts.append(RED + "[-" + " ".join(base_words[i1:i2]) + "-]" + RESET)
        elif tag == "insert":
            parts.append(GREEN + "[+" + " ".join(tail_words[j1:j2]) + "+]" + RESET)
    return " ".join(p for p in parts if p)


def compare(tailored: Path, base: Path) -> int:
    """Print diffs and return the number of changed paragraphs."""
    base_paras = _paragraphs(base)
    tail_paras = _paragraphs(tailored)

    n_base = len(base_paras)
    n_tail = len(tail_paras)
    n_common = min(n_base, n_tail)

    print(f"{BOLD}Base   :{RESET} {base.name}  ({n_base} paragraphs)")
    print(f"{BOLD}Tailored:{RESET} {tailored.name}  ({n_tail} paragraphs)")
    print()

    changes = 0

    for i in range(n_common):
        b, t = base_paras[i], tail_paras[i]
        if b == t:
            continue
        changes += 1
        print(f"{YELLOW}[para {i:3}]{RESET}")
        print(f"  {RED}BASE   :{RESET} {b}")
        print(f"  {GREEN}TAILORED:{RESET} {t}")
        print(f"  {BOLD}DIFF   :{RESET} {_word_diff(b, t)}")
        print()

    # Extra paragraphs in tailored (insertions beyond base length)
    for i in range(n_common, n_tail):
        changes += 1
        print(f"{YELLOW}[para {i:3}]{RESET}  {GREEN}(added){RESET}")
        print(f"  {GREEN}TAILORED:{RESET} {tail_paras[i]}")
        print()

    # Paragraphs present in base but missing from tailored (deletions)
    for i in range(n_common, n_base):
        changes += 1
        print(f"{YELLOW}[para {i:3}]{RESET}  {RED}(removed){RESET}")
        print(f"  {RED}BASE   :{RESET} {base_paras[i]}")
        print()

    if changes == 0:
        print("No differences found — tailored resume is identical to base.")
    else:
        print(f"{BOLD}Summary:{RESET} {changes} paragraph(s) changed.")

    return changes


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)

    tailored = Path(args[0]).expanduser().resolve()
    if not tailored.exists():
        print(f"Error: tailored resume not found: {tailored}", file=sys.stderr)
        sys.exit(2)

    if len(args) >= 2:
        base = Path(args[1]).expanduser().resolve()
    else:
        base = _infer_base(tailored)

    if not base.exists():
        print(f"Error: base template not found: {base}", file=sys.stderr)
        print("Pass the base path explicitly as the second argument.", file=sys.stderr)
        sys.exit(2)

    n_changes = compare(tailored, base)
    sys.exit(0 if n_changes > 0 else 1)


if __name__ == "__main__":
    main()

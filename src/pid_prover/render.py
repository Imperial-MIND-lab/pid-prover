"""Markdown rendering of Table 5 and of the encoded theorems, kept in sync with the docs.

The generated blocks in README.md and docs/REFERENCE.md sit between
<!-- BEGIN name --> and <!-- END name --> markers; `pid-prover sync-docs` rewrites them.
"""
import re
from pathlib import Path
from typing import List

from .measures import MEASURES, bivariate_only_measures, strip_notes, table5
from .properties import PROPERTIES
from .theorems import NOT_ENCODED, THEOREMS

CAPTION = (
    "**Table 5: Comparison of theoretical properties across redundancy measures.** "
    "The ordering of the measures is inspired by the hierarchical clustering of Fig. 1b of the "
    "paper. \\*: this property is not formally proven but is supported by empirical "
    "simulations. †: these properties only hold for *n* = 2 sources. §: these properties only "
    "hold in the case of full-support distributions. ∥: these properties are intended globally; "
    "for many measures, the almost-everywhere version holds. ‡: the pointwise version of these "
    "properties holds for both informative and misinformative lattices separately."
)

# Icons for the cells, relative to the repository root
ICONS = {"✓": "docs/img/yes.svg", "✗": "docs/img/no.svg"}
NA_COLOR = "#2a4de0"


def no_trademark(text: str) -> str:
    """Escape "(TM)", which some Markdown viewers (e.g. Okular) turn into ™."""
    return text.replace("(TM)", "&#40;TM&#41;")


def property_label(label: str) -> str:
    """Row label as in the paper, e.g. "LP0" -> (LP<sub>0</sub>), "STAR" -> (∗)."""
    name = strip_notes(label)
    notes = label.strip()[len(name):]
    if name == "STAR":
        text = "(∗)"
    else:
        text = re.sub(r"(\d)$", r"<sub>\1</sub>", name).join("()")
    return no_trademark(f"**{text}**") + (f"<sup>{notes}</sup>" if notes else "")


def measure_label(measure: str) -> str:
    """Column header as in the paper, e.g. I_min -> I∩^min."""
    return f"<i>I</i><sub>∩</sub><sup>{MEASURES[measure][0]}</sup>"


def cell(entry: str, root: str = "") -> str:
    """Coloured cell as in the paper (green ✓, red ✗, blue n.a.), with footnote marks."""
    if entry == "n.a.":
        return f'<font color="{NA_COLOR}">n.a.</font>'
    notes = entry[1:]
    image = f'<img src="{root}{ICONS[entry[0]]}" alt="{entry[0]}" height="16">'
    return image + (f"<sup>{notes}</sup>" if notes else "")


def render_table5() -> str:
    lines = [
        "| | " + " | ".join(measure_label(m) for m in table5.columns) + " |",
        "|:--|" + ":-:|" * len(table5.columns),
    ]
    for label, row in table5.iterrows():
        lines.append(f"| {property_label(label)} | " + " | ".join(cell(e) for e in row) + " |")
    return "\n".join(lines + ["", CAPTION])


def render_properties() -> str:
    lines = ["| Symbol | Code | Name | Description |", "|:--|:--|:--|:--|"]
    for code, (name, description) in PROPERTIES.items():
        lines.append(f"| {property_label(code)} | `{code}` | {name} | {description} |")
    return "\n".join(lines)


def render_measures() -> str:
    lines = ["| Symbol | Code | Description | Sources |", "|:--|:--|:--|:-:|"]
    for code, (_, description) in MEASURES.items():
        sources = "n = 2" if code in bivariate_only_measures else "any n"
        lines.append(f"| {measure_label(code)} | `{code}` | {description} | {sources} |")
    return "\n".join(lines)


def render_theorems() -> str:
    case_text = {"all": "any", "bivariate": "n = 2", "multivariate": "n ≥ 3"}
    lines = ["| Result | Statement | Case | Derived |", "|:--|:--|:-:|:-:|"]
    for t in THEOREMS:
        lines.append(f"| {t.name} | {no_trademark(t.statement())} | {case_text[t.case]} | "
                     f"{'yes' if t.derived else ''} |")
    lines += ["", "Not encoded:", ""] + [f"- **{k}**: {no_trademark(v)}" for k, v in NOT_ENCODED.items()]
    return "\n".join(lines)


BLOCKS = {
    "README.md": {"TABLE5": render_table5},
    "docs/REFERENCE.md": {
        "PROPERTIES": render_properties,
        "MEASURES": render_measures,
        "THEOREMS": render_theorems,
    },
}


def sync_docs(root: Path = Path("."), check: bool = False) -> List[str]:
    """
    Regenerate the marked blocks in the docs.

    Returns the files that were out of date. With check=True nothing is written.
    """
    stale = []
    for rel_path, blocks in BLOCKS.items():
        path = Path(root) / rel_path
        text = path.read_text(encoding="utf-8")
        new = text
        for name, render in blocks.items():
            pattern = re.compile(rf"(<!-- BEGIN {name}\b[^\n]*-->\n).*?(<!-- END {name} -->)", re.S)
            if not pattern.search(new):
                raise ValueError(f"Markers for {name} not found in {path}")
            new = pattern.sub(lambda m: m.group(1) + render() + "\n" + m.group(2), new)
        if new != text:
            stale.append(rel_path)
            if not check:
                path.write_text(new, encoding="utf-8")
    return stale

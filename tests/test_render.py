"""Tests for the Markdown rendering and the generated blocks in the docs."""
from pathlib import Path

from pid_prover.render import ICONS, cell, property_label, render_table5, sync_docs

ROOT = Path(__file__).resolve().parents[1]


def test_cells():
    assert cell("✓") == '<img src="docs/img/yes.svg" alt="✓" height="16">'
    assert cell("✗‡") == '<img src="docs/img/no.svg" alt="✗" height="16"><sup>‡</sup>'
    assert cell("n.a.") == '<font color="#2a4de0">n.a.</font>'


def test_icons_exist():
    for path in ICONS.values():
        assert (ROOT / path).is_file()


def test_labels():
    assert property_label("LP0") == "**(LP<sub>0</sub>)**"
    assert property_label("STAR") == "**(∗)**"
    assert property_label("TM") == "**&#40;TM&#41;**"
    assert property_label("CO∥") == "**(CO)**<sup>∥</sup>"


def test_table_has_one_row_per_property():
    lines = render_table5().splitlines()
    assert sum(line.startswith("| **") for line in lines) == 21


def test_docs_are_in_sync():
    """If this fails, run `pid-prover sync-docs` from the repository root."""
    assert sync_docs(ROOT, check=True) == []

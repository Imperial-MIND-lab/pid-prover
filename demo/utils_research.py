"""
Utility functions for research exploration tests.

Provides tools for:
- Saving exploration findings to markdown reports
- Exporting graphs in various formats
- Creating formatted tables
- Tracking computational costs
"""

import time
import functools
from pathlib import Path
from typing import Any, Dict, List, Tuple, Callable
from datetime import datetime


# Research outputs directory
RESEARCH_OUTPUTS_DIR = Path(__file__).parent.parent / "research_outputs"
RESEARCH_OUTPUTS_DIR.mkdir(exist_ok=True)


def save_findings_to_markdown(
    findings: Dict[str, Any],
    filename: str,
    title: str = "Research Findings",
    description: str = ""
) -> Path:
    """
    Save research findings to a markdown file.

    Parameters
    ----------
    findings : dict
        Dictionary of findings with section names as keys
    filename : str
        Output filename (without path)
    title : str
        Document title
    description : str
        Document description

    Returns
    -------
    Path
        Path to the created file
    """
    output_path = RESEARCH_OUTPUTS_DIR / filename

    with open(output_path, 'w') as f:
        # Header
        f.write(f"# {title}\n\n")
        if description:
            f.write(f"{description}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        # Content sections
        for section_name, content in findings.items():
            f.write(f"## {section_name}\n\n")

            if isinstance(content, list):
                for item in content:
                    f.write(f"- {item}\n")
                f.write("\n")
            elif isinstance(content, dict):
                for key, value in content.items():
                    f.write(f"**{key}:** {value}\n\n")
            else:
                f.write(f"{content}\n\n")

    return output_path


def export_graph_to_dot(
    graph: Dict[Any, List[Any]],
    filename: str,
    graph_name: str = "G",
    node_labels: Dict[Any, str] = None,
    directed: bool = True
) -> Path:
    """
    Export a graph to Graphviz DOT format.

    Parameters
    ----------
    graph : dict
        Adjacency list representation {node: [neighbors]}
    filename : str
        Output filename (without path, .dot will be added)
    graph_name : str
        Name for the graph
    node_labels : dict, optional
        Custom labels for nodes {node: label}
    directed : bool
        Whether the graph is directed

    Returns
    -------
    Path
        Path to the created DOT file
    """
    if not filename.endswith('.dot'):
        filename = f"{filename}.dot"

    output_path = RESEARCH_OUTPUTS_DIR / filename

    graph_type = "digraph" if directed else "graph"
    edge_op = "->" if directed else "--"

    with open(output_path, 'w') as f:
        f.write(f"{graph_type} {graph_name} {{\n")
        f.write("    rankdir=LR;\n")
        f.write("    node [shape=box, style=rounded];\n\n")

        # Write nodes with labels
        for node in graph.keys():
            label = node_labels.get(node, str(node)) if node_labels else str(node)
            f.write(f'    "{node}" [label="{label}"];\n')
        f.write("\n")

        # Write edges
        written_edges = set()
        for node, neighbors in graph.items():
            for neighbor in neighbors:
                edge = (node, neighbor) if directed else tuple(sorted([node, neighbor]))
                if edge not in written_edges:
                    f.write(f'    "{node}" {edge_op} "{neighbor}";\n')
                    written_edges.add(edge)

        f.write("}\n")

    return output_path


def create_results_table(
    data: List[List[Any]],
    headers: List[str],
    alignment: List[str] = None
) -> str:
    """
    Create a markdown table from data.

    Parameters
    ----------
    data : list of lists
        Table data (rows)
    headers : list of str
        Column headers
    alignment : list of str, optional
        Column alignments ('left', 'center', 'right')

    Returns
    -------
    str
        Markdown table string
    """
    if alignment is None:
        alignment = ['left'] * len(headers)

    # Alignment markers
    align_map = {
        'left': ':---',
        'center': ':---:',
        'right': '---:'
    }

    # Build table
    lines = []

    # Header
    lines.append('| ' + ' | '.join(str(h) for h in headers) + ' |')

    # Separator
    lines.append('| ' + ' | '.join(align_map[a] for a in alignment) + ' |')

    # Data rows
    for row in data:
        lines.append('| ' + ' | '.join(str(cell) for cell in row) + ' |')

    return '\n'.join(lines)


def log_computational_cost(func: Callable) -> Callable:
    """
    Decorator to log execution time and basic stats for research functions.

    Usage:
        @log_computational_cost
        def expensive_search(...):
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_msg = f"Starting {func.__name__}..."
        print(f"\n{'='*60}")
        print(start_msg)
        print(f"{'='*60}")

        result = func(*args, **kwargs)

        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"Completed {func.__name__}")
        print(f"Time elapsed: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
        print(f"{'='*60}\n")

        return result

    return wrapper


def format_property_set(properties: List[str]) -> str:
    """Format a property set for display."""
    return '{' + ', '.join(sorted(properties)) + '}'


def format_implication(premise: List[str], conclusion: str) -> str:
    """Format an implication for display."""
    premise_str = ' ∧ '.join(sorted(premise))
    return f"{premise_str} ⇒ {conclusion}"


def save_conflict_catalog(
    conflicts: List[Tuple[str, ...]],
    filename: str = "conflict_catalog.md",
    case: str = "bivariate"
) -> Path:
    """
    Save a catalog of conflicts to markdown.

    Parameters
    ----------
    conflicts : list of tuples
        List of property sets that are inconsistent
    filename : str
        Output filename
    case : str
        "bivariate" or "multivariate"

    Returns
    -------
    Path
        Path to created file
    """
    findings = {
        "Summary": {
            "Case": case,
            "Total conflicts found": len(conflicts),
            "Conflict sizes": ", ".join(str(len(c)) for c in conflicts[:10]) + "..."
        },
        "Conflicts": [format_property_set(list(c)) for c in conflicts]
    }

    return save_findings_to_markdown(
        findings,
        filename,
        title=f"Conflict Catalog ({case})",
        description=f"Minimal inconsistent property sets for {case} case"
    )


def save_implication_catalog(
    implications: List[Tuple[List[str], str]],
    filename: str = "implication_catalog.md",
    case: str = "bivariate"
) -> Path:
    """
    Save a catalog of implications to markdown.

    Parameters
    ----------
    implications : list of tuples
        List of (premise_properties, conclusion_property)
    filename : str
        Output filename
    case : str
        "bivariate" or "multivariate"

    Returns
    -------
    Path
        Path to created file
    """
    findings = {
        "Summary": {
            "Case": case,
            "Total implications found": len(implications)
        },
        "Implications": [
            format_implication(premise, conclusion)
            for premise, conclusion in implications
        ]
    }

    return save_findings_to_markdown(
        findings,
        filename,
        title=f"Implication Catalog ({case})",
        description=f"Minimal logical implications for {case} case"
    )


def count_z3_calls(func: Callable) -> Callable:
    """
    Decorator to count Z3 solver calls in a function.

    Note: This is a simple counter, not a precise profiler.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.call_count = 0
        result = func(*args, **kwargs)
        print(f"\n{func.__name__} made approximately {wrapper.call_count} solver calls")
        return result

    wrapper.call_count = 0
    return wrapper

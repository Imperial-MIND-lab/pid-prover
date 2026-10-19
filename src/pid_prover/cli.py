"""Command-line interface: `pid-prover <command> [options]`."""
import argparse
import sys
from pathlib import Path

from .analysis import (
    find_maximal_compatible_sets,
    find_minimal_conflicts,
    find_minimal_implications,
    infer_property_consequences,
)
from .measures import validate_measures
from .properties import CASES
from .render import sync_docs
from .theorems import THEOREMS, redundant_theorems


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pid-prover",
        description="Automated reasoning on the properties of PID redundancy measures.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="check every measure of Table 5 against the theorems")
    sub.add_parser("theorems", help="list the encoded theorems and those derivable from others")

    def with_case(p):
        p.add_argument("--case", choices=CASES, default="bivariate",
                       help="bivariate (n = 2) or multivariate (any n); default: bivariate")
        return p

    p = with_case(sub.add_parser("conflicts", help="find minimal incompatible property sets"))
    p.add_argument("--max-size", type=int, default=4, help="largest set size (default: 4)")
    p.add_argument("--keep-reducible", action="store_true",
                   help="also report conflicts reducible to weaker ones")

    p = with_case(sub.add_parser("implications", help="find minimal implications"))
    p.add_argument("--premises", type=int, default=2, help="number of premises (default: 2)")

    p = with_case(sub.add_parser("infer", help="properties forced or ruled out by a set"))
    p.add_argument("props", nargs="+", help="intended properties, e.g. SR S0 LP")

    p = with_case(sub.add_parser("maximal", help="maximal sets of compatible properties"))
    p.add_argument("--require", nargs="*", default=[], help="properties every set must contain")
    p.add_argument("--exclude", nargs="*", default=[], help="properties no set may contain")

    p = sub.add_parser("sync-docs", help="regenerate Table 5 and the theorem list in the docs")
    p.add_argument("--root", type=Path, default=Path("."), help="repository root")
    p.add_argument("--check", action="store_true", help="only report out-of-date files")
    return parser


def main(argv=None) -> int:
    args = create_parser().parse_args(argv)

    if args.command == "validate":
        return 0 if validate_measures() else 1

    if args.command == "theorems":
        for t in THEOREMS:
            print(f"{t.name:<9} {t.statement()}" + ("" if t.case == "all" else f"  [{t.case}]"))
        for n in CASES:
            print(f"\nDerivable from the others ({n}): {', '.join(redundant_theorems(n))}")

    elif args.command == "conflicts":
        conflicts = find_minimal_conflicts(args.case, args.max_size, not args.keep_reducible)
        for c in conflicts:
            print("{" + ", ".join(c) + "}")
        print(f"{len(conflicts)} minimal conflicts of size <= {args.max_size} ({args.case})")

    elif args.command == "implications":
        implications = find_minimal_implications(args.case, args.premises)
        for premises, conclusion in implications:
            print(f"{' ∧ '.join(premises)} ⇒ {conclusion}")
        print(f"{len(implications)} minimal implications with {args.premises} premises "
              f"({args.case})")

    elif args.command == "infer":
        result = infer_property_consequences(args.props, args.case, verbose=True)
        return 0 if result["Consistent"] else 1

    elif args.command == "maximal":
        sets = find_maximal_compatible_sets(args.case, args.require, args.exclude)
        for s in sets:
            print(f"{len(s):>2}: {{{', '.join(s)}}}")

    elif args.command == "sync-docs":
        stale = sync_docs(args.root, check=args.check)
        verb = "out of date" if args.check else "updated"
        print(f"{verb}: {', '.join(stale)}" if stale else "docs are up to date")
        return 1 if (args.check and stale) else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

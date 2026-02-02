"""Command-line interface for PID theorem prover."""
import argparse
from typing import Literal

from .measures import validate_measures
from .analysis import (
    find_minimal_conflicts,
    find_minimal_implications,
    infer_property_consequences,
)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="PID Theorem Discovery Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --validate                              # Validate all measures
  %(prog)s --case bivariate --conflicts           # Find conflicts for n=2
  %(prog)s --case multivariate --implications     # Find implications for n>=3
        """
    )

    parser.add_argument(
        "--case",
        choices=["bivariate", "multivariate"],
        default="bivariate",
        help="Number of sources: 'bivariate' (n=2) or 'multivariate' (n>=3)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate all measures against axioms"
    )
    parser.add_argument(
        "--conflicts",
        action="store_true",
        help="Find minimal conflicts (inconsistent property sets)"
    )
    parser.add_argument(
        "--implications",
        action="store_true",
        help="Find minimal implications"
    )
    parser.add_argument(
        "--max-conflict-size",
        type=int,
        default=4,
        help="Maximum conflict size to search (default: 4)"
    )
    parser.add_argument(
        "--premise-size",
        type=int,
        default=2,
        help="Number of premises in implications (default: 2)"
    )

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    n: Literal["bivariate", "multivariate"] = args.case

    # Run all analyses if no specific flags are set
    run_all = not (args.validate or args.conflicts or args.implications)

    if args.validate or run_all:
        validate_measures()

    if args.conflicts and not run_all:
        find_minimal_conflicts(n, max_size=args.max_conflict_size)

    if args.implications and not run_all:
        find_minimal_implications(n, premise_size=args.premise_size)

    if run_all:
        # Example: infer consequences for a proposed measure
        print("\n" + "="*60)
        print("Example: Inferring consequences for measure with BP and SR")
        print("="*60)
        infer_property_consequences(["BP", "SR"], n="bivariate")


if __name__ == "__main__":
    main()

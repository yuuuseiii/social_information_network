from __future__ import annotations

import argparse
import sys

from .pipeline import generate_daily_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill-e-report",
        description="Skill E final daily report and visualization CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate the final daily report.")
    generate_parser.add_argument("--network", required=True, help="Skill B network_analysis.json path.")
    generate_parser.add_argument("--trends", required=True, help="Skill C trend_analysis.json path.")
    generate_parser.add_argument("--predictions", required=True, help="Skill D prediction_analysis.json path.")
    generate_parser.add_argument("--papers", required=True, help="Skill A papers.json path.")
    generate_parser.add_argument("--query", default=None, help="User query/topic focus.")
    generate_parser.add_argument("--output", required=True, help="Markdown report output path.")
    generate_parser.add_argument("--json-output", required=True, help="Merged JSON output path.")
    generate_parser.add_argument("--artifacts-dir", required=True, help="Directory for PNG artifacts.")
    generate_parser.add_argument("--top-n", type=int, default=10, help="Top-N recommendations to include.")

    args = parser.parse_args(argv)
    if args.command == "generate":
        generate_daily_report(
            network_path=args.network,
            trends_path=args.trends,
            predictions_path=args.predictions,
            papers_path=args.papers,
            query=args.query,
            output_path=args.output,
            json_output_path=args.json_output,
            artifacts_dir=args.artifacts_dir,
            top_n=args.top_n,
        )
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

from pathlib import Path

from skill_e_report.pipeline import generate_daily_report


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    output_dir = root / "output"
    generate_daily_report(
        network_path=root / "examples" / "network_analysis.json",
        trends_path=root / "examples" / "trend_analysis.json",
        predictions_path=root / "examples" / "prediction_analysis.json",
        papers_path=root / "examples" / "papers.json",
        query="embodied navigation cs.RO",
        output_path=output_dir / "daily_report.md",
        json_output_path=output_dir / "merged_data.json",
        artifacts_dir=output_dir / "artifacts",
        top_n=5,
    )

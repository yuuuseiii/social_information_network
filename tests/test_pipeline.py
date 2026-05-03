from pathlib import Path

from skill_e_report.pipeline import generate_daily_report


def test_generate_daily_report_outputs_markdown_json_and_artifacts():
    root = Path(__file__).resolve().parents[1]
    output_dir = root / ".test_outputs" / "daily_report"
    output_md = output_dir / "daily_report.md"
    output_json = output_dir / "merged_data.json"
    artifacts = output_dir / "artifacts"

    result = generate_daily_report(
        network_path=root / "examples" / "network_analysis.json",
        trends_path=root / "examples" / "trend_analysis.json",
        predictions_path=root / "examples" / "prediction_analysis.json",
        papers_path=root / "examples" / "papers.json",
        query="embodied navigation cs.RO",
        output_path=output_md,
        json_output_path=output_json,
        artifacts_dir=artifacts,
        top_n=3,
    )

    assert output_md.exists()
    assert output_json.exists()
    assert result["report"]["metrics"]["paper_count"] == 6
    assert result["report"]["recommendations"]
    assert (artifacts / "author_paper_network.png").exists()
    assert (artifacts / "domain_hotness.png").exists()
    assert (artifacts / "recommendation_scores.png").exists()

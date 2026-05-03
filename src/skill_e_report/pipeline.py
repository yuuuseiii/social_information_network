from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .extract import (
    extract_bridge_author_trends,
    extract_category_trends,
    extract_communities,
    extract_recommendations,
    load_papers,
)
from .io import read_json, write_json, write_text
from .models import RecommendationInfo, ReportArtifacts, ReportMetrics
from .report import render_markdown
from .viz import generate_visualizations


def generate_daily_report(
    network_path: str | Path,
    output_path: str | Path,
    json_output_path: str | Path,
    artifacts_dir: str | Path,
    trends_path: str | Path | None = None,
    predictions_path: str | Path | None = None,
    papers_path: str | Path | None = None,
    query: str | None = None,
    top_n: int = 10,
) -> dict[str, Any]:
    network_payload = read_json(network_path)
    trends_payload = read_json(trends_path) if trends_path else None
    predictions_payload = read_json(predictions_path) if predictions_path else None
    papers_payload = read_json(papers_path) if papers_path else None

    papers = load_papers(papers_payload)
    communities = extract_communities(network_payload, trends_payload)
    category_trends = extract_category_trends(trends_payload, papers)
    bridge_author_trends = extract_bridge_author_trends(trends_payload, network_payload)
    recommendations = extract_recommendations(predictions_payload, papers, top_n)

    author_edges = _build_author_edges(network_payload)
    future_predictions = _future_predictions(predictions_payload)
    cross_domain_suggestions = _cross_domain_suggestions(category_trends)

    metrics = ReportMetrics(
        paper_count=len(papers),
        community_count=len(communities),
        trend_count=len(category_trends),
        prediction_count=_prediction_count(predictions_payload),
        recommendation_count=len(recommendations),
        bridge_author_count=len(bridge_author_trends),
    )

    artifacts = generate_visualizations(
        papers=papers,
        recommendations=recommendations,
        trends=category_trends,
        author_edges=author_edges,
        artifacts_dir=artifacts_dir,
    )

    report_payload = {
        "report_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "query": (query or "").strip(),
        "papers": [paper.__dict__ for paper in papers],
        "communities": [community.__dict__ for community in communities],
        "category_trends": [trend.__dict__ for trend in category_trends],
        "recommendations": _serialize_recommendations(recommendations),
        "cross_domain_suggestions": cross_domain_suggestions,
        "future_predictions": future_predictions,
        "metrics": metrics.__dict__,
        "artifacts": artifacts,
    }

    merged_payload = {
        "report": report_payload,
        "inputs": {
            "network_analysis": network_payload,
            "trend_analysis": trends_payload or {},
            "prediction_analysis": predictions_payload or {},
            "papers": papers_payload or {},
        },
    }

    write_json(json_output_path, merged_payload)
    report_path = Path(output_path)
    report_payload["artifacts"] = _relative_artifacts(report_path, artifacts)
    write_text(report_path, render_markdown(report_payload))
    return merged_payload


def _serialize_recommendations(recommendations: list[RecommendationInfo]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rec in recommendations:
        rows.append(
            {
                "arxiv_id": rec.arxiv_id,
                "title": rec.title,
                "authors": list(rec.authors),
                "categories": list(rec.categories),
                "score": rec.score,
                "rationale": rec.rationale,
            }
        )
    return rows


def _build_author_edges(network_payload: dict[str, Any]) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    for bridge in network_payload.get("top_bridges", []) if isinstance(network_payload, dict) else []:
        if not isinstance(bridge, dict):
            continue
        author = str(bridge.get("name_norm") or bridge.get("author") or "").strip()
        if not author:
            continue
        for paper in bridge.get("representative_papers", []) if isinstance(bridge.get("representative_papers"), list) else []:
            if str(paper).strip():
                edges.append((author, str(paper).strip()))
    return edges


def _cross_domain_suggestions(category_trends: list[Any]) -> list[str]:
    categories = [row.category for row in category_trends if row.category]
    suggestions: list[str] = []
    for idx, left in enumerate(categories[:4]):
        for right in categories[idx + 1 : 4]:
            suggestion = f"{left} + {right}"
            suggestions.append(suggestion)
            if len(suggestions) >= 5:
                return suggestions
    return suggestions


def _future_predictions(predictions_payload: dict[str, Any] | None) -> list[str]:
    if not predictions_payload:
        return []
    lines: list[str] = []
    communities = predictions_payload.get("community_forecasts")
    if isinstance(communities, list):
        sorted_rows = sorted(
            [row for row in communities if isinstance(row, dict)],
            key=lambda row: float(
                row.get("future_attention_score")
                or row.get("opportunity_score")
                or row.get("predicted_growth_probability")
                or 0.0
            ),
            reverse=True,
        )
        for row in sorted_rows[:3]:
            lines.append(
                f"Community {row.get('community_id')}: attention={row.get('future_attention_score', 0):.3f}, "
                f"growth_prob={row.get('predicted_growth_probability', 0):.3f}"
            )
    papers = predictions_payload.get("paper_forecasts")
    if isinstance(papers, list):
        sorted_rows = sorted(
            [row for row in papers if isinstance(row, dict)],
            key=lambda row: float(row.get("recommendation_score") or row.get("near_term_attention_score") or 0.0),
            reverse=True,
        )
        for row in sorted_rows[:3]:
            lines.append(
                f"Paper {row.get('arxiv_id')}: score={row.get('recommendation_score', row.get('near_term_attention_score', 0)):.3f}"
            )
    directions = predictions_payload.get("research_direction_forecasts")
    if isinstance(directions, list):
        for row in directions[:3]:
            if isinstance(row, dict) and row.get("direction"):
                lines.append(f"Direction: {row['direction']} (score={row.get('forecast_score', 0):.3f})")
    return lines


def _prediction_count(predictions_payload: dict[str, Any] | None) -> int:
    if not predictions_payload:
        return 0
    count = 0
    for key in ("community_forecasts", "paper_forecasts", "user_recommendations"):
        value = predictions_payload.get(key)
        if isinstance(value, list):
            count += len(value)
    return count


def _relative_artifacts(report_path: Path, artifacts: dict[str, str]) -> dict[str, str]:
    if not artifacts:
        return {}
    base = report_path.parent
    rel: dict[str, str] = {}
    for key, path in artifacts.items():
        try:
            rel[key] = str(Path(path).resolve().relative_to(base.resolve()))
        except ValueError:
            rel[key] = path
    return rel

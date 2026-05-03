from __future__ import annotations

from typing import Any


def render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload.get("metrics", {})
    artifacts = payload.get("artifacts", {})
    recommendations = payload.get("recommendations", [])
    trends = payload.get("category_trends", [])
    suggestions = payload.get("cross_domain_suggestions", [])
    predictions = payload.get("future_predictions", [])

    lines = [
        "# Final Daily Report & Visualization",
        "",
        f"- Report date: {payload.get('report_date', '')}",
        f"- Query focus: {payload.get('query') or 'general daily watchlist'}",
        "",
        "## Report Overview",
        f"- Papers merged: {metrics.get('paper_count', 0)}",
        f"- Communities detected: {metrics.get('community_count', 0)}",
        f"- Trend signals: {metrics.get('trend_count', 0)}",
        f"- Predictions: {metrics.get('prediction_count', 0)}",
        f"- Recommendations: {metrics.get('recommendation_count', 0)}",
        "",
        "## Top Recommended Papers",
    ]

    if recommendations:
        lines.extend(
            [
                "| Rank | arXiv ID | Title | Authors | Categories | Score |",
                "| ---: | --- | --- | --- | --- | ---: |",
            ]
        )
        for idx, rec in enumerate(recommendations, start=1):
            authors = ", ".join(rec.get("authors", [])) or "-"
            categories = ", ".join(rec.get("categories", [])) or "-"
            title = rec.get("title") or "-"
            score = f"{float(rec.get('score', 0.0)):.3f}"
            lines.append(
                f"| {idx} | {rec.get('arxiv_id', '-') } | {title} | {authors} | {categories} | {score} |"
            )
    else:
        lines.append("- No recommendations available.")

    lines.extend(["", "## Domain Hotness & Trend Analysis"])
    if trends:
        for row in trends:
            growth = row.get("growth")
            growth_text = f", growth={growth:.2f}" if isinstance(growth, (int, float)) else ""
            lines.append(
                f"- {row.get('category', '')}: hotness={row.get('hotness_score', 0):.2f}, "
                f"count={row.get('current_count', 0)}{growth_text}"
            )
    else:
        lines.append("- No category trend data.")

    lines.extend(["", "## Cross-domain Expansion Suggestions"])
    if suggestions:
        for suggestion in suggestions:
            lines.append(f"- {suggestion}")
    else:
        lines.append("- No cross-domain suggestions.")

    lines.extend(["", "## Future Trend Predictions & Directions"])
    if predictions:
        for prediction in predictions:
            lines.append(f"- {prediction}")
    else:
        lines.append("- No future predictions available.")

    lines.extend(["", "## Visualizations"])
    if artifacts:
        for label, path in artifacts.items():
            if not path:
                continue
            lines.append(f"- {label.replace('_', ' ').title()}: ![]({path})")
    else:
        lines.append("- No visualizations generated.")

    return "\n".join(lines).rstrip() + "\n"

from __future__ import annotations

from collections import Counter
from typing import Any

from .models import CommunityInfo, PaperInfo, RecommendationInfo, TrendInfo


def load_papers(payload: dict[str, Any] | None) -> list[PaperInfo]:
    if not payload:
        return []
    raw = payload.get("papers_metadata")
    if raw is None:
        raw = payload.get("papers")
    if raw is None:
        raw = payload.get("papers_ranked")
    if not isinstance(raw, list):
        return []
    papers: list[PaperInfo] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        source = item.get("paper") if isinstance(item.get("paper"), dict) else item
        arxiv_id = str(source.get("arxiv_id") or source.get("id") or source.get("paper_id") or "").strip()
        if not arxiv_id:
            continue
        title = str(source.get("title") or "").strip()
        authors = tuple(str(author).strip() for author in source.get("authors", []) if str(author).strip())
        categories = tuple(str(cat).strip() for cat in source.get("categories", []) if str(cat).strip())
        published_at = str(
            source.get("published_at")
            or source.get("date")
            or source.get("published")
            or source.get("updated")
            or ""
        ).strip()
        papers.append(
            PaperInfo(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                categories=categories,
                published_at=published_at,
            )
        )
    return papers


def extract_communities(
    network_payload: dict[str, Any] | None,
    trends_payload: dict[str, Any] | None,
) -> list[CommunityInfo]:
    records = None
    if network_payload:
        records = network_payload.get("emerging_communities")
    if records is None and trends_payload:
        records = trends_payload.get("community_trends")
    if records is None and network_payload:
        records = network_payload.get("community_trends")
    if not isinstance(records, list):
        return []
    communities: list[CommunityInfo] = []
    for idx, item in enumerate(records):
        if not isinstance(item, dict):
            continue
        community_id = str(item.get("community_id") or f"C{idx}")
        size = max(0, int(item.get("size") or 0))
        categories = _extract_categories(item.get("top_categories"))
        representatives = _extract_representative_papers(item.get("representative_papers"))
        communities.append(
            CommunityInfo(
                community_id=community_id,
                size=size,
                top_categories=categories,
                representative_papers=representatives,
            )
        )
    return communities


def extract_category_trends(
    trends_payload: dict[str, Any] | None,
    papers: list[PaperInfo],
) -> list[TrendInfo]:
    if trends_payload and isinstance(trends_payload.get("category_trends"), list):
        trends: list[TrendInfo] = []
        for row in trends_payload["category_trends"]:
            if not isinstance(row, dict):
                continue
            category = str(row.get("category") or "").strip()
            if not category:
                continue
            current = _optional_int(row.get("current_count")) or _optional_int(row.get("count")) or 0
            growth = _optional_float(row.get("growth"))
            hotness = _hotness_score(current, growth)
            trends.append(TrendInfo(category=category, current_count=current, growth=growth, hotness_score=hotness))
        return sorted(trends, key=lambda item: (item.hotness_score, item.current_count), reverse=True)

    category_counts: Counter[str] = Counter()
    for paper in papers:
        category_counts.update(paper.categories)
    trends = [
        TrendInfo(category=category, current_count=count, growth=None, hotness_score=float(count))
        for category, count in category_counts.items()
    ]
    return sorted(trends, key=lambda item: item.hotness_score, reverse=True)


def extract_bridge_author_trends(
    trends_payload: dict[str, Any] | None,
    network_payload: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if trends_payload and isinstance(trends_payload.get("bridge_author_trends"), list):
        return [row for row in trends_payload["bridge_author_trends"] if isinstance(row, dict)]
    if network_payload and isinstance(network_payload.get("top_bridges"), list):
        return [row for row in network_payload["top_bridges"] if isinstance(row, dict)]
    return []


def extract_recommendations(
    prediction_payload: dict[str, Any] | None,
    papers: list[PaperInfo],
    top_n: int,
) -> list[RecommendationInfo]:
    paper_lookup = {paper.arxiv_id: paper for paper in papers}
    recommendations: list[RecommendationInfo] = []
    if prediction_payload and isinstance(prediction_payload.get("user_recommendations"), list):
        for row in prediction_payload["user_recommendations"]:
            if not isinstance(row, dict):
                continue
            target_type = str(row.get("target_type") or "").lower()
            if target_type not in {"paper", "", "arxiv"}:
                continue
            target_id = str(row.get("target_id") or row.get("arxiv_id") or "").strip()
            if not target_id:
                continue
            paper = paper_lookup.get(target_id)
            recommendations.append(
                RecommendationInfo(
                    arxiv_id=target_id,
                    title=paper.title if paper else str(row.get("title") or ""),
                    authors=paper.authors if paper else (),
                    categories=paper.categories if paper else (),
                    score=float(row.get("score") or row.get("recommendation_score") or 0.0),
                    rationale=str(row.get("why") or row.get("action") or "").strip(),
                )
            )
    if recommendations:
        return sorted(recommendations, key=lambda item: item.score, reverse=True)[:top_n]

    forecasts = prediction_payload.get("paper_forecasts") if prediction_payload else None
    if isinstance(forecasts, list):
        for row in forecasts:
            if not isinstance(row, dict):
                continue
            arxiv_id = str(row.get("arxiv_id") or row.get("paper_id") or "").strip()
            if not arxiv_id:
                continue
            paper = paper_lookup.get(arxiv_id)
            score = float(row.get("recommendation_score") or row.get("near_term_attention_score") or 0.0)
            recommendations.append(
                RecommendationInfo(
                    arxiv_id=arxiv_id,
                    title=paper.title if paper else str(row.get("title") or ""),
                    authors=paper.authors if paper else (),
                    categories=paper.categories if paper else (),
                    score=score,
                    rationale="".strip(),
                )
            )
    return sorted(recommendations, key=lambda item: item.score, reverse=True)[:top_n]


def _extract_categories(raw: Any) -> tuple[str, ...]:
    if isinstance(raw, list):
        categories: list[str] = []
        for entry in raw:
            if isinstance(entry, dict):
                value = entry.get("category")
            else:
                value = entry
            if str(value).strip():
                categories.append(str(value).strip())
        return tuple(categories)
    if isinstance(raw, dict):
        return tuple(str(key) for key in raw if str(key).strip())
    return ()


def _extract_representative_papers(raw: Any) -> tuple[str, ...]:
    if not isinstance(raw, list):
        return ()
    paper_ids: list[str] = []
    for entry in raw:
        if isinstance(entry, dict):
            value = entry.get("paper_id") or entry.get("arxiv_id") or entry.get("id")
        else:
            value = entry
        if str(value).strip():
            paper_ids.append(str(value).strip())
    return tuple(paper_ids)


def _hotness_score(current_count: int, growth: float | None) -> float:
    growth_score = 0.0
    if growth is not None:
        growth_score = max(-1.0, min(2.0, float(growth))) * 6.0
    return float(current_count) + growth_score


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

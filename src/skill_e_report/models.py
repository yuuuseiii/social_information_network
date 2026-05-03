from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PaperInfo:
    arxiv_id: str
    title: str
    authors: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    published_at: str = ""


@dataclass(frozen=True)
class CommunityInfo:
    community_id: str
    size: int
    top_categories: tuple[str, ...] = ()
    representative_papers: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecommendationInfo:
    arxiv_id: str
    title: str
    authors: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    score: float = 0.0
    rationale: str = ""


@dataclass(frozen=True)
class TrendInfo:
    category: str
    current_count: int = 0
    growth: float | None = None
    hotness_score: float = 0.0


@dataclass(frozen=True)
class ReportMetrics:
    paper_count: int = 0
    community_count: int = 0
    trend_count: int = 0
    prediction_count: int = 0
    recommendation_count: int = 0
    bridge_author_count: int = 0


@dataclass(frozen=True)
class ReportArtifacts:
    author_paper_network_png: str = ""
    domain_hotness_png: str = ""
    recommendation_scores_png: str = ""


@dataclass(frozen=True)
class ReportSummary:
    report_date: str
    query: str
    papers: tuple[PaperInfo, ...] = ()
    communities: tuple[CommunityInfo, ...] = ()
    trends: tuple[TrendInfo, ...] = ()
    recommendations: tuple[RecommendationInfo, ...] = ()
    metrics: ReportMetrics = field(default_factory=ReportMetrics)
    artifacts: ReportArtifacts = field(default_factory=ReportArtifacts)

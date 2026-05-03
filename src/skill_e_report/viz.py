from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import PaperInfo, RecommendationInfo, TrendInfo


def generate_visualizations(
    papers: list[PaperInfo],
    recommendations: list[RecommendationInfo],
    trends: list[TrendInfo],
    author_edges: Iterable[tuple[str, str]],
    artifacts_dir: str | Path,
) -> dict[str, str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx

    out_dir = Path(artifacts_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, str] = {}

    if papers:
        graph = nx.Graph()
        authors: set[str] = set()
        for paper in papers:
            graph.add_node(paper.arxiv_id)
            for author in paper.authors:
                graph.add_edge(author, paper.arxiv_id)
                authors.add(author)
        for left, right in author_edges:
            graph.add_edge(left, right)
            authors.add(left)
            authors.add(right)

        if graph.nodes:
            pos = nx.spring_layout(graph, seed=42)
            paper_nodes = [node for node in graph.nodes if node not in authors]
            author_nodes = [node for node in graph.nodes if node in authors]
            fig, ax = plt.subplots(figsize=(9, 6))
            nx.draw_networkx_nodes(graph, pos, nodelist=author_nodes, node_color="#4C9BE8", node_size=500, ax=ax)
            nx.draw_networkx_nodes(graph, pos, nodelist=paper_nodes, node_color="#F5B041", node_size=700, ax=ax)
            nx.draw_networkx_edges(graph, pos, alpha=0.45, ax=ax)
            nx.draw_networkx_labels(graph, pos, font_size=8, ax=ax)
            ax.set_title("Author-Paper Collaboration Network")
            ax.axis("off")
            fig.tight_layout()
            path = out_dir / "author_paper_network.png"
            fig.savefig(path, dpi=160)
            plt.close(fig)
            artifacts["author_paper_network_png"] = str(path)

    if trends:
        top = trends[:10]
        labels = [trend.category for trend in top]
        scores = [trend.hotness_score for trend in top]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.barh(labels[::-1], scores[::-1], color="#59C36A")
        ax.set_xlabel("Hotness score")
        ax.set_title("Domain Hotness")
        ax.grid(axis="x", alpha=0.3)
        fig.tight_layout()
        path = out_dir / "domain_hotness.png"
        fig.savefig(path, dpi=160)
        plt.close(fig)
        artifacts["domain_hotness_png"] = str(path)

    if recommendations:
        top = recommendations[:10]
        labels = [rec.arxiv_id for rec in top]
        scores = [rec.score for rec in top]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.barh(labels[::-1], scores[::-1], color="#8E77D8")
        ax.set_xlabel("Recommendation score")
        ax.set_title("Top Recommendations")
        ax.grid(axis="x", alpha=0.3)
        fig.tight_layout()
        path = out_dir / "recommendation_scores.png"
        fig.savefig(path, dpi=160)
        plt.close(fig)
        artifacts["recommendation_scores_png"] = str(path)

    return artifacts

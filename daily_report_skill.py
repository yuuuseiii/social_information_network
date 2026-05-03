# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List

import matplotlib
import networkx as nx
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

skill1_papers = [
    {
        "arxiv_id": "2401.0001",
        "title": "LLM Agent Network",
        "authors": ["Li", "Wang"],
        "categories": ["cs.AI"],
        "date": "2026-05-01",
    },
    {
        "arxiv_id": "2401.0002",
        "title": "Graph Learning",
        "authors": ["Zhang", "Li"],
        "categories": ["cs.LG"],
        "date": "2026-05-01",
    },
]

skill2_network = {
    "author_collaboration": [["Li", "Wang"], ["Zhang", "Li"]],
    "paper_similarity": [["2401.0001", "2401.0002", 0.85]],
    "centrality": {"2401.0001": 0.92, "2401.0002": 0.87},
    "paper_recommendation": ["2401.0001", "2401.0002"],
}

skill3_trend = {
    "hot_domains": [{"name": "AI Agent", "score": 95}, {"name": "Graph ML", "score": 90}],
    "cross_domain_suggestions": ["AI + Graph", "LLM + Network"],
}

skill4_prediction = {
    "future_trends": [{"domain": "Self-evolving Agent", "growth": 0.93}],
    "predicted_papers": ["2401.0001"],
    "potential_directions": ["Autonomous Research", "Multi-agent Collaboration"],
}

DEFAULT_CONFIG = {
    "output_dir": "./output",
    "figures_dir": "./output/figures",
    "top_k": 5,
}


def _dedupe_list(items: List[Any]) -> List[Any]:
    seen = set()
    result: List[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _dedupe_edges(edges: List[List[str]]) -> List[List[str]]:
    seen = set()
    result: List[List[str]] = []
    for edge in edges:
        if len(edge) != 2:
            continue
        key = tuple(sorted(edge))
        if key not in seen:
            seen.add(key)
            result.append(edge)
    return result


def _dedupe_similarity(similarities: List[List[Any]]) -> List[List[Any]]:
    scores: Dict[tuple, float] = {}
    for item in similarities:
        if len(item) != 3:
            continue
        left, right, score = item
        key = tuple(sorted([left, right]))
        if key not in scores or score > scores[key]:
            scores[key] = float(score)
    return [[key[0], key[1], score] for key, score in scores.items()]


def merge_data(
    papers: List[Dict[str, Any]] = skill1_papers,
    network: Dict[str, Any] = skill2_network,
    trend: Dict[str, Any] = skill3_trend,
    prediction: Dict[str, Any] = skill4_prediction,
) -> Dict[str, Any]:
    paper_map: Dict[str, Dict[str, Any]] = {}
    for paper in papers:
        paper_id = paper.get("arxiv_id")
        if not paper_id:
            continue
        if paper_id not in paper_map:
            paper_map[paper_id] = {
                "arxiv_id": paper_id,
                "title": paper.get("title", ""),
                "authors": list(paper.get("authors", [])),
                "categories": list(paper.get("categories", [])),
                "date": paper.get("date", ""),
            }
        else:
            existing = paper_map[paper_id]
            if paper.get("title"):
                existing["title"] = existing["title"] or paper["title"]
            existing["authors"] = _dedupe_list(
                existing.get("authors", []) + list(paper.get("authors", []))
            )
            existing["categories"] = _dedupe_list(
                existing.get("categories", []) + list(paper.get("categories", []))
            )
            if not existing.get("date") and paper.get("date"):
                existing["date"] = paper["date"]

    merged = {
        "papers": list(paper_map.values()),
        "author_collaboration": _dedupe_edges(network.get("author_collaboration", [])),
        "paper_similarity": _dedupe_similarity(network.get("paper_similarity", [])),
        "centrality": dict(network.get("centrality", {})),
        "paper_recommendation": _dedupe_list(network.get("paper_recommendation", [])),
        "hot_domains": list(trend.get("hot_domains", [])),
        "cross_domain_suggestions": _dedupe_list(trend.get("cross_domain_suggestions", [])),
        "future_trends": list(prediction.get("future_trends", [])),
        "predicted_papers": _dedupe_list(prediction.get("predicted_papers", [])),
        "potential_directions": _dedupe_list(prediction.get("potential_directions", [])),
    }
    return merged


def _rank_recommendations(merged_data: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
    paper_index = {paper["arxiv_id"]: paper for paper in merged_data.get("papers", [])}
    rec_ids = merged_data.get("paper_recommendation", [])
    recommendations: List[Dict[str, Any]] = []
    for paper_id in rec_ids:
        paper = paper_index.get(paper_id)
        if not paper:
            continue
        recommendations.append(
            {
                "arxiv_id": paper_id,
                "title": paper.get("title", ""),
                "authors": paper.get("authors", []),
                "categories": paper.get("categories", []),
                "date": paper.get("date", ""),
                "score": merged_data.get("centrality", {}).get(paper_id, 0),
            }
        )
    if not recommendations:
        for paper_id, score in merged_data.get("centrality", {}).items():
            paper = paper_index.get(
                paper_id,
                {"arxiv_id": paper_id, "title": "", "authors": [], "categories": [], "date": ""},
            )
            recommendations.append(
                {
                    "arxiv_id": paper_id,
                    "title": paper.get("title", ""),
                    "authors": paper.get("authors", []),
                    "categories": paper.get("categories", []),
                    "date": paper.get("date", ""),
                    "score": score,
                }
            )
    recommendations.sort(key=lambda item: item.get("score", 0), reverse=True)
    return recommendations[:top_k]


def generate_report(
    merged_data: Dict[str, Any], config: Dict[str, Any] = DEFAULT_CONFIG
) -> tuple[str, List[Dict[str, Any]]]:
    output_dir = config.get("output_dir", "./output")
    top_k = int(config.get("top_k", 5))
    os.makedirs(output_dir, exist_ok=True)

    recommendations = _rank_recommendations(merged_data, top_k)
    current_date = datetime.utcnow().strftime("%Y-%m-%d")

    lines = [
        "# 学术网络分析日报",
        "",
        f"生成日期：{current_date}",
        "",
        "## 报告概览",
        f"- 论文数量：{len(merged_data.get('papers', []))}",
        f"- 推荐论文数量：{len(recommendations)}",
        f"- 热门领域数量：{len(merged_data.get('hot_domains', []))}",
        f"- 未来趋势数量：{len(merged_data.get('future_trends', []))}",
        "",
        f"## 必看论文推荐（Top{top_k}）",
    ]

    if recommendations:
        lines.extend(
            [
                "| 排名 | arXiv ID | 标题 | 作者 | 类别 | 日期 | 推荐得分 |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for idx, rec in enumerate(recommendations, start=1):
            authors = ", ".join(rec.get("authors", [])) or "-"
            categories = ", ".join(rec.get("categories", [])) or "-"
            title = rec.get("title") or "-"
            date = rec.get("date") or "-"
            score = f"{rec.get('score', 0):.2f}"
            lines.append(
                f"| {idx} | {rec['arxiv_id']} | {title} | {authors} | {categories} | {date} | {score} |"
            )
    else:
        lines.append("- 暂无推荐论文。")

    lines.extend(["", "## 领域热度趋势"])
    hot_domains = merged_data.get("hot_domains", [])
    if hot_domains:
        for domain in hot_domains:
            lines.append(f"- {domain.get('name', '')}: {domain.get('score', 0)}")
    else:
        lines.append("- 暂无领域热度数据。")

    lines.extend(["", "## 跨领域拓展建议"])
    suggestions = merged_data.get("cross_domain_suggestions", [])
    if suggestions:
        for suggestion in suggestions:
            lines.append(f"- {suggestion}")
    else:
        lines.append("- 暂无跨领域建议。")

    lines.extend(["", "## 未来研究趋势预测"])
    future_trends = merged_data.get("future_trends", [])
    if future_trends:
        for trend in future_trends:
            lines.append(f"- {trend.get('domain', '')}: 增长率 {trend.get('growth', 0):.2f}")
    else:
        lines.append("- 暂无未来趋势预测。")

    predicted = merged_data.get("predicted_papers", [])
    if predicted:
        lines.append(f"- 可能爆发论文：{', '.join(predicted)}")

    directions = merged_data.get("potential_directions", [])
    if directions:
        lines.append(f"- 潜在研究方向：{', '.join(directions)}")

    lines.append("")
    report_content = "\n".join(lines)

    report_path = os.path.join(output_dir, "daily_report.md")
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report_content)
    return report_content, recommendations


def visualize(merged_data: Dict[str, Any], config: Dict[str, Any] = DEFAULT_CONFIG) -> None:
    output_dir = config.get("output_dir", "./output")
    figures_dir = config.get("figures_dir", os.path.join(output_dir, "figures"))
    top_k = int(config.get("top_k", 5))
    os.makedirs(figures_dir, exist_ok=True)

    graph = nx.Graph()
    for edge in merged_data.get("author_collaboration", []):
        if len(edge) == 2:
            graph.add_edge(edge[0], edge[1])
    for paper in merged_data.get("papers", []):
        paper_id = paper.get("arxiv_id")
        if not paper_id:
            continue
        graph.add_node(paper_id)
        for author in paper.get("authors", []):
            graph.add_edge(author, paper_id)

    if graph.nodes:
        authors = {
            author
            for paper in merged_data.get("papers", [])
            for author in paper.get("authors", [])
        }
        for edge in merged_data.get("author_collaboration", []):
            authors.update(edge[:2])
        author_nodes = [node for node in graph.nodes if node in authors]
        paper_nodes = [node for node in graph.nodes if node not in authors]

        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(graph, seed=42)
        nx.draw_networkx_nodes(
            graph, pos, nodelist=author_nodes, node_color="#5DADE2", node_size=500, label="Author"
        )
        nx.draw_networkx_nodes(
            graph, pos, nodelist=paper_nodes, node_color="#F5B041", node_size=700, label="Paper"
        )
        nx.draw_networkx_edges(graph, pos, alpha=0.6)
        nx.draw_networkx_labels(graph, pos, font_size=8)
        plt.title("作者/论文合作网络图")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "author_paper_network.png"), dpi=150)
        plt.close()

    hot_domains = merged_data.get("hot_domains", [])
    if hot_domains:
        df_domains = pd.DataFrame(hot_domains)
        plt.figure(figsize=(8, 5))
        plt.bar(df_domains["name"], df_domains["score"], color="#58D68D")
        plt.title("领域热度趋势")
        plt.xlabel("领域")
        plt.ylabel("热度得分")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "domain_hotness.png"), dpi=150)
        plt.close()

    recommendations = _rank_recommendations(merged_data, top_k)
    if recommendations:
        df_recommend = pd.DataFrame(recommendations)
        plt.figure(figsize=(8, 5))
        plt.bar(df_recommend["arxiv_id"], df_recommend["score"], color="#AF7AC5")
        plt.title("推荐论文得分")
        plt.xlabel("论文")
        plt.ylabel("推荐得分")
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "recommendation_scores.png"), dpi=150)
        plt.close()


def run_skill(config: Dict[str, Any] = DEFAULT_CONFIG) -> Dict[str, Any]:
    merged_data = merge_data()
    output_dir = config.get("output_dir", "./output")
    os.makedirs(output_dir, exist_ok=True)

    merged_path = os.path.join(output_dir, "merged_data.json")
    with open(merged_path, "w", encoding="utf-8") as file:
        json.dump(merged_data, file, ensure_ascii=False, indent=2)

    generate_report(merged_data, config)
    visualize(merged_data, config)
    return merged_data


if __name__ == "__main__":
    run_skill()

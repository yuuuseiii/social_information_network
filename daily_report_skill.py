import json
import os
from typing import Dict, List, Any

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


# 内置示例数据：严格不读取任何外部文件
skill1_papers = [
    {"arxiv_id": "2401.0001", "title": "LLM Agent Network", "authors": ["Li", "Wang"], "categories": ["cs.AI"], "date": "2026-05-01"},
    {"arxiv_id": "2401.0002", "title": "Graph Learning", "authors": ["Zhang", "Li"], "categories": ["cs.LG"], "date": "2026-05-01"}
]

skill2_network = {
    "author_collaboration": [["Li", "Wang"], ["Zhang", "Li"]],
    "paper_similarity": [["2401.0001", "2401.0002", 0.85]],
    "centrality": {"2401.0001": 0.92, "2401.0002": 0.87},
    "paper_recommendation": ["2401.0001", "2401.0002"]
}

skill3_trend = {
    "hot_domains": [{"name": "AI Agent", "score": 95}, {"name": "Graph ML", "score": 90}],
    "cross_domain_suggestions": ["AI + Graph", "LLM + Network"]
}

skill4_prediction = {
    "future_trends": [{"domain": "Self-evolving Agent", "growth": 0.93}],
    "predicted_papers": ["2401.0001"],
    "potential_directions": ["Autonomous Research", "Multi-agent Collaboration"]
}


def merge_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """融合四路上游数据，去重并字段对齐。"""
    paper_map: Dict[str, Dict[str, Any]] = {paper["arxiv_id"]: dict(paper) for paper in skill1_papers}

    # 补充网络特征
    for pid, cent in skill2_network.get("centrality", {}).items():
        if pid not in paper_map:
            paper_map[pid] = {"arxiv_id": pid, "title": "Unknown", "authors": [], "categories": [], "date": None}
        paper_map[pid]["centrality"] = float(cent)

    # 标记推荐来源与预测来源
    recommend_ids = skill2_network.get("paper_recommendation", [])
    predict_ids = skill4_prediction.get("predicted_papers", [])

    for pid in set(recommend_ids + predict_ids):
        if pid not in paper_map:
            paper_map[pid] = {"arxiv_id": pid, "title": "Unknown", "authors": [], "categories": [], "date": None}
        paper_map[pid]["recommended"] = pid in recommend_ids
        paper_map[pid]["predicted"] = pid in predict_ids

    # 统一缺省字段
    for pid, paper in paper_map.items():
        paper.setdefault("centrality", 0.0)
        paper.setdefault("recommended", False)
        paper.setdefault("predicted", False)
        paper.setdefault("authors", [])
        paper.setdefault("categories", [])

    # Top推荐（按中心性排序）
    top_k = int(config.get("top_k", 5))
    papers_sorted = sorted(paper_map.values(), key=lambda x: x.get("centrality", 0.0), reverse=True)

    merged_data = {
        "meta": {
            "skill_name": "daily_report_skill",
            "report_date": pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
            "domain": config.get("domain", "Academic Network Analysis")
        },
        "papers": papers_sorted,
        "top_recommendations": [p["arxiv_id"] for p in papers_sorted[:top_k]],
        "network": {
            "author_collaboration": skill2_network.get("author_collaboration", []),
            "paper_similarity": skill2_network.get("paper_similarity", [])
        },
        "trends": {
            "hot_domains": skill3_trend.get("hot_domains", []),
            "cross_domain_suggestions": list(dict.fromkeys(skill3_trend.get("cross_domain_suggestions", [])))
        },
        "predictions": {
            "future_trends": skill4_prediction.get("future_trends", []),
            "predicted_papers": list(dict.fromkeys(predict_ids)),
            "potential_directions": list(dict.fromkeys(skill4_prediction.get("potential_directions", [])))
        }
    }
    return merged_data


def generate_report(merged_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """生成Markdown日报并写入output目录。"""
    output_dir = config["output_dir"]
    top_k = int(config.get("top_k", 5))
    os.makedirs(output_dir, exist_ok=True)

    papers = merged_data["papers"]
    hot_domains = merged_data["trends"]["hot_domains"]
    cross_suggestions = merged_data["trends"]["cross_domain_suggestions"]
    future_trends = merged_data["predictions"]["future_trends"]
    potential_directions = merged_data["predictions"]["potential_directions"]

    report_lines: List[str] = [
        "# 学术网络分析日报",
        "",
        "## 报告概览",
        f"- 报告日期：{merged_data['meta']['report_date']}",
        f"- 研究领域：{merged_data['meta']['domain']}",
        f"- 收录论文数：{len(papers)}",
        f"- 推荐论文数：{len(merged_data['top_recommendations'])}",
        "",
        "## 必看论文推荐（Top5）"
    ]

    for i, p in enumerate(papers[:top_k], 1):
        report_lines.append(
            f"{i}. **{p['title']}** (`{p['arxiv_id']}`) | centrality={p.get('centrality', 0):.2f} | authors={', '.join(p.get('authors', []))}"
        )

    report_lines += ["", "## 研究领域热度趋势"]
    for d in hot_domains:
        report_lines.append(f"- {d['name']}：{d['score']}")

    report_lines += ["", "## 跨领域拓展建议"]
    for s in cross_suggestions:
        report_lines.append(f"- {s}")

    report_lines += ["", "## 未来研究趋势预测"]
    for ft in future_trends:
        report_lines.append(f"- {ft['domain']}（growth={ft['growth']:.2f}）")
    for pdir in potential_directions:
        report_lines.append(f"- 潜在方向：{pdir}")

    report_text = "\n".join(report_lines) + "\n"

    with open(os.path.join(output_dir, "daily_report.md"), "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_text


def visualize(merged_data: Dict[str, Any], config: Dict[str, Any]) -> None:
    """生成三张图：合作网络图、领域热度图、推荐论文得分图。"""
    figure_dir = os.path.join(config["output_dir"], "figures")
    os.makedirs(figure_dir, exist_ok=True)

    # 1) 论文/作者合作网络图（作者合作）
    g = nx.Graph()
    for a, b in merged_data["network"]["author_collaboration"]:
        g.add_edge(a, b)

    plt.figure(figsize=(6, 4))
    pos = nx.spring_layout(g, seed=42)
    nx.draw_networkx(g, pos=pos, node_color="#8ecae6", edge_color="#219ebc", with_labels=True)
    plt.title("Author Collaboration Network")
    plt.tight_layout()
    plt.savefig(os.path.join(figure_dir, "author_collaboration_network.png"), dpi=150)
    plt.close()

    # 2) 领域热度趋势图
    domain_df = pd.DataFrame(merged_data["trends"]["hot_domains"])
    plt.figure(figsize=(6, 4))
    plt.bar(domain_df["name"], domain_df["score"], color="#ffb703")
    plt.title("Hot Domain Trend")
    plt.ylabel("Score")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(os.path.join(figure_dir, "hot_domain_trend.png"), dpi=150)
    plt.close()

    # 3) 推荐论文得分图（centrality）
    rec_ids = set(merged_data["top_recommendations"])
    rec_df = pd.DataFrame([p for p in merged_data["papers"] if p["arxiv_id"] in rec_ids])
    rec_df = rec_df.sort_values("centrality", ascending=False)

    plt.figure(figsize=(6, 4))
    plt.bar(rec_df["arxiv_id"], rec_df["centrality"], color="#fb8500")
    plt.title("Recommended Paper Scores")
    plt.ylabel("Centrality")
    plt.tight_layout()
    plt.savefig(os.path.join(figure_dir, "recommended_paper_scores.png"), dpi=150)
    plt.close()


def run() -> Dict[str, Any]:
    """统一执行入口：融合、落盘、报告与可视化。"""
    config = {
        "output_dir": "./output",
        "top_k": 5,
        "domain": "Academic Network Analysis"
    }

    merged = merge_data(config)
    os.makedirs(config["output_dir"], exist_ok=True)

    with open(os.path.join(config["output_dir"], "merged_data.json"), "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    generate_report(merged, config)
    visualize(merged, config)
    return merged


if __name__ == "__main__":
    run()

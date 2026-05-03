# Skill E: Final Daily Report & Visualization

Skill E delivers the final daily briefing for the 5-skill arXiv research workflow. It merges the outputs of Skills A–D, generates a professional Markdown briefing, and emits a unified JSON summary and PNG visualizations.

## What It Does

- Merges upstream outputs into a single structured data model.
- Produces a readable daily briefing in Markdown.
- Generates visualizations for collaboration, domain hotness, and recommendations.
- Emits merged JSON for downstream systems.
- Supports user query focus and top‑N recommendations.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Quickstart CLI

```bash
skill-e-report generate \
  --network examples/network_analysis.json \
  --trends examples/trend_analysis.json \
  --predictions examples/prediction_analysis.json \
  --papers examples/papers.json \
  --query "embodied navigation cs.RO" \
  --output output/daily_report.md \
  --json-output output/merged_data.json \
  --artifacts-dir output/artifacts
```

## Input Schema

Required inputs:

1. **Skill B** `network_analysis.json`
   - `emerging_communities[]`
   - `communities`
   - `paper_sim_edges[]`
   - `centrality`
   - `top_bridges[]`

2. **Skill C** `trend_analysis.json`
   - `community_trends[]`
   - `category_trends[]`
   - `bridge_author_trends[]`

3. **Skill D** `prediction_analysis.json`
   - `community_forecasts[]`
   - `paper_forecasts[]`
   - `user_recommendations[]`

4. **Skill A** `papers.json`
   - `papers_metadata[]` with `title`, `authors`, `categories`, `date`, `arxiv_id`

## Output Schema

- `merged_data.json`: combined view of all inputs plus report metadata.
- `daily_report.md`: structured report with overview, recommendations, trends, and predictions.
- PNG figures saved to the artifacts directory:
  - `author_paper_network.png`
  - `domain_hotness.png`
  - `recommendation_scores.png`

## Evaluation

Suggested evaluation metrics:

- Number of merged papers, recommendations, and trend rows.
- Report completeness and readability.
- Visualization clarity and relevance.
- Configurable top‑N recommendations.

## References

- PageRank centrality for recommendation weighting.
- Community detection and trend extrapolation for forecasting.
- Content-based recommendation alignment with user query.

## How It Fits the 5-Skill Workflow

```text
Skill A: arXiv retrieval and metadata
  -> Skill B: network construction and current recommendations
  -> Skill C: temporal trend detection
  -> Skill D: inference and future prediction for user needs
  -> Skill E: final daily report and visualization
```

Skill E answers: **what should the user read today, and how do we explain the signals?**

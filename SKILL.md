# Skill E: Final Daily Report & Visualization

## Purpose

Skill E consolidates all upstream signals into a single daily briefing for arXiv research. It merges network analytics, temporal trends, and prediction outputs with paper metadata to produce a human-readable report and supporting figures.

## Inputs

- Skill B `network_analysis.json`
- Skill C `trend_analysis.json`
- Skill D `prediction_analysis.json`
- Skill A `papers.json`

## Outputs

- `merged_data.json`: structured merge of all inputs plus report metadata.
- `daily_report.md`: Markdown report with overview, recommendations, and trend summaries.
- PNG visualizations:
  - author-paper collaboration network
  - domain hotness bar chart
  - recommendation score bar chart

## CLI

```bash
skill-e-report generate \
  --network examples/network_analysis.json \
  --trends examples/trend_analysis.json \
  --predictions examples/prediction_analysis.json \
  --papers examples/papers.json \
  --query "protein design q-bio.BM" \
  --output output/daily_report.md \
  --json-output output/merged_data.json \
  --artifacts-dir output/artifacts
```

## Report Sections

1. Overview and counts.
2. Top recommended papers.
3. Domain hotness and trend analysis.
4. Cross-domain expansion suggestions.
5. Future predictions and research directions.
6. Embedded visualization links.

## Notes

The report is designed for daily briefings and can be customized using the query focus and top‑N parameters.

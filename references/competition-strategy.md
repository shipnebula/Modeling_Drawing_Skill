# Competition Strategy

How to use figures to win math modeling competitions.

---

## The truth about competition figures

Your paper will be read by people who are busy. They have 20+ papers to review. They spend 2-3 minutes per paper scanning for:

1. Does this look like a real paper?
2. Did they actually do analysis?
3. Are the results convincing?

Good figures answer "yes" to all three in seconds. Bad figures — or no figures — lose you 1-2 points before anyone reads a word.

This guide tells you exactly which figures to put where, and how to make them look professional.

---

## CUMCM (国赛) — Chinese National Math Modeling

### Paper structure and figure placement

| Section | Figures | What to show |
|---------|---------|--------------|
| 摘要 (Abstract) | 1-2 | Dashboard or radar chart. Show your key results visually. This is the first thing reviewers see. |
| 问题重述 (Problem Restatement) | 1 | Mind map or process flow. Show you understand the problem. |
| 模型建立 (Model) | 2-3 | Network graph for structure, fit curve for regression. Show your model makes sense. |
| 模型求解 (Solving) | 2-3 | Line chart for convergence, learning curve for training. Show your model works. |
| 结果分析 (Results) | 4-6 | Grouped bars, correlation matrices, scatter plots. This is where you make your case. |
| 灵敏度分析 (Sensitivity) | 1-2 | Tornado chart. Show you know which parameters matter. |
| 结论 (Conclusion) | 1 | Radar or dashboard. Summarize your findings visually. |

### Figure budget

A typical CUMCM paper has 8-12 figures. Don't overdo it. Each figure should earn its place.

### What reviewers look for

- Clean typography (not the default matplotlib font size)
- Consistent style across all figures
- Figures referenced in the text
- Labels in Chinese or English (pick one, stay consistent)
- Vector format (PDF or SVG) for print

### Common mistakes

1. **Too many pie charts.** Pie charts are for proportions only, and only when there are 4-6 slices. Use bar charts instead for most comparisons.

2. **Default matplotlib colors.** The default matplotlib cycle looks like it came from 2010. Use a proper palette.

3. **Missing labels.** Every axis needs a label. Every figure needs a title. "Figure 1" in the caption is not a substitute for an actual title.

4. **Unreferenced figures.** Every figure in your paper must be mentioned in the text. "As shown in Figure 3..." If you never mention a figure, don't include it.

---

## MCM/ICM (美赛) — US Math Modeling

### Paper structure and figure placement

| Section | Figures | What to show |
|---------|---------|--------------|
| Summary Sheet | 1 | Dashboard. Your summary sheet is the first page. One good figure here is worth 10 points. |
| Introduction & Problem Definition | 0-1 | Mind map if helpful. Don't overdo it. |
| Assumptions & Definitions | 0 | Usually no figures needed. |
| Model Formulation | 1-2 | Network graph, process flow. Show your model structure. |
| Model Analysis | 4-6 | This is the core. Grouped bars, fit curves, radar charts, scatter plots. |
| Sensitivity Analysis | 1-2 | Tornado chart. Required for MCM/ICM. |
| Model Validation | 1-2 | Residual plot, confusion matrix. Show your model is reliable. |
| Conclusion & Recommendations | 1 | Radar or dashboard. |

### O-award tips

The Outstand Prize (O奖) is the top award. Here's what separates O-award papers from H-award papers:

1. **Summary Sheet quality.** This is page 1. It gets the most attention. Put one great dashboard figure here.

2. **Sensitivity analysis.** O-award papers always have a tornado chart. It shows you understand uncertainty.

3. **Model validation.** Show residuals are random. Show cross-validation scores. Prove your model isn't overfitting.

4. **Visual consistency.** All figures should look like they came from the same person. Same colors, same font sizes, same style.

5. **Figure captions.** Each figure should have a descriptive caption, not just "Figure 1." Something like "Figure 1: Sensitivity analysis of key parameters."

### English vs Chinese

MCM/ICM papers are in English. Use English labels on all figures. Keep it simple:

- Axis labels: "Revenue (M USD)", "Accuracy (%)", "Time (s)"
- Titles: "Figure 1: Annual Revenue Comparison"
- Legends: Short, clear labels

---

## Figure types by purpose

### For summary/overview
- **Dashboard** — best for 摘要 and Summary Sheet
- **Radar chart** — good for multi-criteria comparison

### For showing relationships
- **Scatter plot** — correlation between variables
- **Correlation matrix** — multiple variables at once
- **Fit curve** — regression results

### For showing trends
- **Line chart** — the most common and most useful
- **Area chart** — when you want to emphasize volume
- **Step chart** — for discrete changes

### For showing comparisons
- **Bar chart** — the workhorse
- **Grouped bar** — multiple categories
- **Radar chart** — multi-dimensional comparison

### For showing model quality
- **Residual plot** — diagnostics
- **ROC curve** — binary classification
- **Learning curve** — bias-variance
- **Confusion matrix** — classification details

### For showing structure
- **Network graph** — model structure, relationships
- **Sankey diagram** — flow, allocation
- **Mind map** — topic hierarchy
- **Process flow** — sequential steps

### For sensitivity
- **Tornado chart** — parameter sensitivity (essential!)
- **Feature importance** — which features matter

---

## Style guide for competition papers

### Fonts

Use a consistent font throughout. The default matplotlib font (DejaVu Sans) is fine for English papers. For Chinese papers, make sure you have a CJK font configured.

Font sizes:
- Title: 12-14pt
- Axis labels: 10-12pt
- Tick labels: 8-10pt
- Legend: 8-10pt

### Colors

Use a professional palette. Avoid:
- The default matplotlib cycle (too garish)
- Red-green combinations (colorblind-unfriendly)
- More than 8 colors in one chart

Good palettes:
- `nature_qual` — clean, professional, good for papers
- `tol_8` — colorblind-safe (Paul Tol)
- `economist` — modern editorial look
- `ocean` — cool blues, good for data

### Layout

- Use consistent figure sizes across your paper
- Leave margins for axis labels
- Don't crowd multiple charts into one figure unless they tell one story
- Use subplots sparingly — reviewers prefer simple figures

### Export format

- **PDF** — best for print. Vector format, scales to any size.
- **SVG** — also vector. Good for web and some LaTeX workflows.
- **PNG** — use only if you need to embed in a format that doesn't support vector.

Always export at 300 DPI minimum.

---

## Final checklist

Before submitting:

- [ ] Every figure has a title
- [ ] Every axis has a label
- [ ] All figures use the same style and colors
- [ ] Figures are referenced in the text
- [ ] Exported as PDF or SVG (vector)
- [ ] No default matplotlib colors
- [ ] No pie charts with more than 6 slices
- [ ] Sensitivity analysis included
- [ ] Model validation included
# Typography Guide

Fonts, sizes, and formatting for competition papers.

---

## The short version

- Title: 12-14pt, bold
- Axis labels: 10-12pt
- Tick labels: 8-10pt
- Legend: 8-10pt
- Annotations: 8-9pt

That's it. Everything else is optional.

---

## Fonts

### Default font

The library uses DejaVu Sans by default. It's clean, readable, and available everywhere. Good enough for most papers.

### For Chinese papers

CJK characters need a proper font. The library handles this automatically if you have a CJK font installed.

Common CJK fonts:
- SimSun (宋体) — standard Chinese font
- SimHei (黑体) — bold Chinese font
- Noto Sans CJK — modern, clean

### For posters

Use larger fonts. The `poster` style preset does this automatically:

```python
from plot import apply_style
apply_style('poster')
```

---

## Font sizes

| Element | Size | Notes |
|---------|------|-------|
| Figure title | 12-14pt | Bold |
| Axis labels | 10-12pt | Regular weight |
| Tick labels | 8-10pt | Regular weight |
| Legend | 8-10pt | Regular weight |
| Data labels | 8-9pt | Bold for emphasis |
| Annotations | 8-9pt | Italic for notes |
| Source note | 7-8pt | Small, unobtrusive |

### Size presets

The library has predefined sizes in `FIGSIZE`:

```python
from plot import FIGSIZE
FIGSIZE['title']      # 12
FIGSIZE['xlabel']     # 10
FIGSIZE['ylabel']     # 10
FIGSIZE['tick']       # 9
FIGSIZE['legend']     # 9
FIGSIZE['annotation'] # 8
```

---

## Number formatting

Numbers in your figures should be clean and readable.

### Smart formatting (recommended)

```python
from plot import format_numbers

format_numbers(1234)       # '1234'
format_numbers(12345)      # '12.3K'
format_numbers(1234567)    # '1.2M'
format_numbers(1.234e-5)   # '1.23e-05'
```

### Custom formatting

```python
format_numbers(1234567, style='thousands')  # '1,234,567'
format_numbers(3.14159, style='decimal')     # '3.14'
format_numbers(0.45, style='percent')        # '45.0%'
format_numbers(1.234e-5, style='scientific') # '1.23e-05'
```

### For axis ticks

```python
from plot import format_ticks

# Auto-format tick labels
format_ticks(ax, style='smart')
```

---

## Axes and spines

### Style presets

The library has 7 style presets. Each one configures axes, spines, and grid.

| Style | Spines | Grid | Best for |
|-------|--------|------|----------|
| `nature` | Left + bottom only | Light, dashed | Academic papers |
| `publication` | All four | Light, dashed | Formal papers |
| `economist` | Bottom only | None | Presentations |
| `minimal` | None | None | Infographics |
| `dark` | All four (bright) | Subtle | Dark mode |
| `poster` | All four (thick) | Thick | Conference posters |
| `dark_poster` | All four (bright) | Subtle | Dark posters |

### Apply a style

```python
from plot import apply_style

apply_style('nature')       # Clean, minimal
apply_style('publication')  # Formal
apply_style('dark')         # Dark mode
```

### Manual configuration

```python
from plot import axis_config

axis_config(ax, grid='y', show_top=False, show_right=False)
```

---

## Grid

Grid lines should be subtle. They help you read values but shouldn't compete with the data.

```python
# Different grid styles
axis_config(ax, grid='y')      # Horizontal lines only
axis_config(ax, grid='x')      # Vertical lines only
axis_config(ax, grid='both')   # Both
axis_config(ax, grid='none')   # No grid
```

### Grid settings

| Setting | Value | Notes |
|---------|-------|-------|
| Color | `#DDDDDD` (light) | Subtle |
| Alpha | 0.3-0.5 | Semi-transparent |
| Line width | 0.5pt | Thin |
| Style | Dashed (`--`) | Discrete |

---

## Annotations

### Data labels

```python
from plot import add_data_labels

add_data_labels(ax, bars, fmt='%d')
```

### Text annotations

```python
from plot import add_annotation

add_annotation(ax, text='Key finding', xy=(0.5, 0.8),
               xytext=(0.7, 0.9), arrow=True)
```

### Figure titles

```python
from plot import add_figure_title

add_figure_title(fig, 'Main Title', subtitle='Optional Subtitle')
```

### Source notes

```python
from plot import add_source_note

add_source_note(ax, 'Source: World Bank, 2023')
```

---

## Layout

### Tight layout

```python
from plot import auto_layout

auto_layout(fig, pad=0.1)
```

### Multiple subplots

```python
from plot import figsubplots

fig, axes = figsubplots(nrows=2, ncols=2)
```

### Save with proper layout

```python
from plot import save_figure

save_figure(fig, 'output.png', dpi=300)
# Automatically applies tight layout
```

---

## Tips

1. **Consistency is everything.** Same font sizes, same colors, same style across all figures in your paper.

2. **Don't over-annotate.** A figure with 20 labels is unreadable. Pick the 2-3 most important ones.

3. **Use bold for emphasis.** Title, key data labels, highlighted bars. Not everything needs to be bold.

4. **Test at print size.** What looks good on screen might be too small in print. Export and check.

5. **Use vector formats.** PDF and SVG scale to any size without quality loss. PNG at 300 DPI is acceptable for emergencies.

6. **Leave space.** Don't crowd your figures. Margins make figures readable.
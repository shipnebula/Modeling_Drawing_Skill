# Color Palettes

How to pick the right palette, and why it matters.

---

## Why color matters

Your figures are read on two screens: a laptop during review, and a printer during final judging. Colors that look good on one might wash out on the other.

Three things to get right:

1. **Contrast** — colors must be distinguishable from each other
2. **Colorblind safety** — 8% of men can't tell red from green
3. **Meaning** — colors should suggest relationships (sequential = ordered, diverging = centered at zero)

---

## Qualitative palettes (categorical data)

Use when categories are unrelated (no ordering).

### nature_qual (default)
Clean, professional. Good for most papers.
```python
plot([10, 20, 30], labels=['A', 'B', 'C'], palette='nature_qual')
```

### tol_8 (colorblind-safe)
Based on Paul Tol's colorblind-safe palette. Use this if your paper has many categories.
```python
plot(data, labels=labels, palette='tol_8')
```

### economist
Muted, editorial. Looks like The Economist's charts.
```python
plot(data, labels=labels, palette='economist')
```

### Other qualitative palettes

| Palette | Character | Best for |
|---------|-----------|----------|
| `nature_qual` | Clean, professional | Default for papers |
| `tol_8` | Colorblind-safe | Many categories |
| `economist` | Muted, editorial | Presentations |
| `ocean` | Cool blues | Water/environment data |
| `sunset` | Warm tones | Energy/heat data |
| `forest` | Green tones | Agriculture/environment |
| `earth` | Earth tones | Geography/geology |
| `candy` | Bright, playful | Infographics |
| `pastel` | Soft, gentle | Non-technical audiences |
| `vibrant` | Bold, saturated | Posters |
| `business` | Conservative | Corporate presentations |
| `dark_qual` | Dark mode | Dark backgrounds |
| `warm` | Warm tones | General use |
| `cool` | Cool tones | General use |

---

## Sequential palettes (ordered data)

Use when values have a natural order (low to high, or vice versa).

### viridis (recommended)
Perceptually uniform. Works in colorblind, grayscale, and full color. The gold standard for sequential data.
```python
from plot import sequential_colormap
colors = sequential_colormap('viridis', n=50)
```

### Other sequential palettes

| Palette | Character | Best for |
|---------|-----------|----------|
| `viridis` | Perceptually uniform | Default for sequential data |
| `cividis` | Colorblind-safe | Accessibility |
| `inferno` | Dark to bright | Heat/intensity |
| `plasma` | Purple to yellow | General use |
| `magma` | Black to white | Dark backgrounds |
| `blues` | Single hue | Simple, clean |
| `greens` | Single hue | Environment data |
| `reds` | Single hue | Temperature data |
| `oranges` | Single hue | Warm data |
| `purples` | Single hue | General use |
| `browns` | Single hue | Earth data |
| `pink` | Single hue | Soft data |
| `ylgn` | Yellow-green | Environmental |
| `ylbu` | Yellow-blue | Data science |
| `gnbu` | Green-blue | Climate data |
| `orrd` | Orange-red | Heatmaps |
| `puor` | Purple-orange | Diverging-ish |

---

## Diverging palettes (centered data)

Use when data is centered at a meaningful value (zero, mean, etc.).

### coolwarm (recommended)
Blue-white-red. The standard for diverging data.
```python
from plot import diverging_colormap
colors = diverging_colormap('coolwarm', n=50)
```

### Other diverging palettes

| Palette | Character | Best for |
|---------|-----------|----------|
| `coolwarm` | Blue-white-red | Default for diverging |
| `spectral` | Rainbow | Multi-dimensional |
| `RdBu` | Red-blue | Climate data |
| `RdYlGn` | Red-yellow-green | Rating scales |
| `PiYG` | Pink-yellow-green | General use |
| `PuOr` | Purple-orange | Social science |
| `BrBG` | Brown-blue-green | Environmental |
| `GnBu` | Green-blue | Climate |
| `PuRd` | Purple-red | General use |
| `YlGnBu` | Yellow-green-blue | Climate |

---

## Theme palettes (pre-configured)

Use when you want a palette optimized for a specific purpose.

| Palette | Purpose |
|---------|---------|
| `data_analysis` | General analysis |
| `optimization` | Optimization results |
| `classification` | Classification metrics |
| `regression` | Regression results |
| `network` | Network graphs |
| `dark_mode` | Dark backgrounds |
| `warm_accent` | Warm highlights |
| `cool_accent` | Cool highlights |
| `earth_tones` | Earth-tone backgrounds |
| `pastel_theme` | Soft backgrounds |
| `vibrant_theme` | Bright backgrounds |
| `nature_themes` | Nature-inspired |

---

## How to use palettes

### With `plot()`

```python
from plot import plot

# Qualitative
plot([10, 20, 30], labels=['A', 'B', 'C'], palette='nature_qual')
plot(data, labels=labels, palette='tol_8')  # colorblind-safe

# Sequential
plot(df, type='correlation', palette='viridis')
plot(df, type='correlation', palette='coolwarm')

# With FigureFactory
f = FigureFactory(palette='economist')
f.bar(data, labels=labels, title='Results')
```

### Manual palette access

```python
from plot import get_palette, auto_colors, sequential_colormap

# Get specific palette
colors = get_palette('nature_qual')  # list of hex colors

# Auto-generate N colors
colors = auto_colors(5, 'viridis')  # 5 colors from viridis

# Sequential colormap
colors = sequential_colormap('viridis', n=50)

# Diverging colormap
colors = diverging_colormap('coolwarm', n=50)
```

### Blend and modify colors

```python
from plot import blend, lightness

# Blend two colors
new_color = blend('#FF0000', '#00FF00', 0.5)  # 50% red + 50% green

# Adjust lightness
lighter = lightness('#808080', 0.3)  # 30% lighter
```

---

## Tips

1. **Use `tol_8` for 6+ categories.** It's colorblind-safe. Reviewers with color vision deficiency will thank you.

2. **Use `viridis` for sequential data.** It's the default in matplotlib for a reason — it works everywhere.

3. **Use `coolwarm` for diverging data.** The standard blue-white-red. Everyone understands it.

4. **Don't use more than 8 colors.** If you need more, you probably have the wrong chart type.

5. **Test in grayscale.** Print your figures in grayscale. If you can't tell the colors apart, your palette is too subtle.

6. **Use `dark_mode` palette with `dark` style.** They're designed to work together.
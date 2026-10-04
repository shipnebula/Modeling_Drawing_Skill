"""
plot/cli.py — Command-line interface for Math Modeling Viz.

Installed as the ``mmv`` console script (also runnable as
``python -m plot.cli``):

    mmv plot data.csv --type bar --title "Results" -o output.pdf
    mmv types                # all chart types
    mmv palettes             # palette gallery with ANSI preview
    mmv styles               # style presets
    mmv detect data.csv      # show what auto-detection would pick
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Non-interactive rendering — must be set before pyplot is touched.
if not sys.stdout.isatty() or sys.platform.startswith("linux") and not __import__("os").environ.get("DISPLAY"):
    import os
    os.environ.setdefault("MPLBACKEND", "Agg")


# ──────────────────────────────────────────────
#  DATA  LOADING
# ──────────────────────────────────────────────

def load_data(path: str | Path):
    """Load data from CSV, TSV, JSON, XLSX or pickled numpy."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    if suffix in (".xlsx", ".xls"):
        import pandas as pd
        return pd.read_excel(path)
    if suffix == ".pkl" or suffix == ".npy":
        import numpy as np
        return np.load(path, allow_pickle=True)
    if suffix in (".csv", ".txt", ".tsv"):
        import pandas as pd
        sep = "\t" if suffix == ".tsv" else None
        try:
            return pd.read_csv(path, sep=sep, engine="python")
        except UnicodeDecodeError:
            return pd.read_csv(path, sep=sep, engine="python", encoding="utf-8-sig")
    raise ValueError(f"Unsupported data format '{suffix}'. "
                     "Use CSV, TSV, JSON, XLSX, NPY or PKL.")


def parse_scalars(text: str | None):
    """Parse '--data [1,2,3]' style JSON or comma-separated numbers."""
    if text is None:
        return None
    text = text.strip()
    if text.startswith(("[", "{")):
        return json.loads(text)
    parts = [p for p in text.replace(";", ",").split(",") if p.strip()]
    try:
        return [float(p) for p in parts]
    except ValueError:
        return parts


# ──────────────────────────────────────────────
#  SUBCOMMANDS
# ──────────────────────────────────────────────

def _cmd_types(_args) -> int:
    from .factory import list_chart_types
    print(f"{len(list_chart_types())} chart types available:\n")
    for t in list_chart_types():
        print(f"  • {t}")
    return 0


def _cmd_palettes(_args) -> int:
    from .palette import ALL_PALETTES
    for family, palettes in ALL_PALETTES.items():
        print(f"\n{family.upper()}")
        for name, colors in palettes.items():
            swatches = "".join(f"\033[48;2;{int(c[1:3], 16)};{int(c[3:5], 16)};{int(c[5:7], 16)}m   \033[0m"
                               for c in colors[:8])
            print(f"  {name:<18} {swatches}")
    return 0


def _cmd_styles(_args) -> int:
    from .styles import list_styles
    print("Available styles:")
    for s in list_styles():
        print(f"  • {s}")
    return 0


def _cmd_detect(args) -> int:
    from .factory import _detect_chart_type, resolve_chart_type
    data = load_data(args.data_file) if args.data_file else parse_scalars(args.data)
    detected = _detect_chart_type(data)
    print(f"Auto-detected chart type: {detected!r} → {resolve_chart_type(detected)!r}")
    return 0


def _cmd_plot(args) -> int:
    from . import plot, __version__

    data = None
    if args.data_file:
        data = load_data(args.data_file)
    elif args.data:
        data = parse_scalars(args.data)

    if data is None and not args.x:
        print("Error: no data. Use --data-file FILE or --data '[1,2,3]'.",
              file=sys.stderr)
        return 2

    kwargs = {}
    if args.labels:
        kwargs["labels"] = [l.strip() for l in args.labels.split(",")]
    if args.xlabel:
        kwargs["xlabel"] = args.xlabel
    if args.ylabel:
        kwargs["ylabel"] = args.ylabel

    fig_w, fig_h = (float(v) for v in args.figsize.lower().split("x"))
    figsize = (fig_w, fig_h)

    fig = plot(
        data,
        type=args.type,
        title=args.title,
        x=parse_scalars(args.x),
        y=parse_scalars(args.y),
        style=args.style,
        palette=args.palette,
        figsize=figsize,
        save_path=args.output,
        dpi=args.dpi,
        **kwargs,
    )
    out = Path(args.output)
    print(f"✓ Saved {out}  ({out.stat().st_size / 1024:.0f} KB, "
          f"dpi={args.dpi}, mmv {__version__})")
    return 0


# ──────────────────────────────────────────────
#  PREVIEW  (render one demo of a chart type)
# ──────────────────────────────────────────────

def _demo_args(chart_fn_name: str, rng) -> tuple[tuple, dict]:
    """Return (positional_args, kwargs) demo inputs per canonical chart.

    Every entry is (positional_tuple, kwargs_dict).
    """
    import numpy as np

    N = 60
    xs = np.linspace(0, 10, N)
    X, Y = np.meshgrid(np.linspace(0, 2, 30), np.linspace(0, 2, 30))
    Z = np.sin(3 * X) * np.cos(2 * Y)

    demo = {
        "bar_chart": (([12, 18, 9, 25],), {"labels": ["Q1", "Q2", "Q3", "Q4"]}),
        "line_chart": (({"Alpha": np.sin(xs) * 2 + 5, "Beta": np.cos(xs) * 2 + 5},), {"x": xs}),
        "scatter_plot": ((xs, 0.8 * xs + rng.normal(0, 1.2, N)), {}),
        "histogram": ((rng.normal(170, 8, 800),), {}),
        "box_plot": (([rng.normal(70, 8, 150), rng.normal(75, 9, 150)],), {"labels": ["A", "B"]}),
        "pie_chart": (([38, 26, 21, 15],), {"labels": ["A", "B", "C", "D"]}),
        "confusion_matrix": ((np.array([[52, 8], [6, 34]]),), {"labels": ["Neg", "Pos"]}),
        "roc_curve": ((rng.integers(0, 2, 300), rng.uniform(0, 1, 300) * 0.6 + rng.integers(0, 2, 300) * 0.3), {}),
        "radar_chart": ((["Speed", "Cost", "Risk", "Scale", "Ease"], [[4.2, 3.1, 3.8, 4.6, 4.0]]), {}),
        "surface3d": ((X, Y, Z), {}),
        "contour_plot": ((np.linspace(0, 2, 30), np.linspace(0, 2, 30), Z), {}),
        "vector_field": ((X, Y, -np.sin(Y), np.cos(X)), {}),
        "heatmap": ((rng.uniform(0, 1, (6, 8)),), {}),
        "correlation_matrix": ((rng.normal(0, 1, (200, 5)),), {"labels": ["V1", "V2", "V3", "V4", "V5"]}),
        "network_graph": ((["Hub", "A", "B", "C", "D"], [("Hub", "A"), ("Hub", "B"), ("A", "C"), ("B", "D")]), {}),
        "gantt_chart": (([{"name": "Data", "start": 0, "end": 2, "progress": 1.0},
                          {"name": "Model", "start": 2, "end": 5, "progress": 0.7}],), {}),
        "dashboard": (([{"label": "Accuracy", "value": "94%", "change": "+2%", "change_dir": "up", "progress": 0.94},
                        {"label": "F1", "value": "0.91", "change": "+0.03", "change_dir": "up", "progress": 0.91},
                        {"label": "Latency", "value": "42ms", "change": "-8ms", "change_dir": "down", "progress": 0.75},
                        {"label": "Uptime", "value": "99.9%", "change": "+0.1%", "change_dir": "up", "progress": 0.999}],), {}),
        "gauge": ((76,), {"label": "SLA"}),
        "clustermap": ((rng.normal(0, 1, (10, 6)),), {}),
        "silhouette_plot": ((np.vstack([rng.normal([0, 0], 0.6, (40, 2)), rng.normal([4, 4], 0.6, (40, 2))]),
                             np.repeat([0, 1], 40)), {}),
        "bifurcation": ((), {"a_range": (2.6, 4.0), "n_a": 300, "n_plot": 40, "n_transient": 80}),
        "cobweb": ((lambda x: 3.9 * x * (1 - x),), {"x0": 0.2, "n": 30}),
        "monte_carlo_convergence": ((rng.normal(3.5, 1.2, 800),), {"true_value": 3.5}),
        "acf_pacf": ((np.diff(np.cumsum(rng.normal(0, 1, 150))),), {}),
        "seasonal_decomposition": ((10 + 3 * np.sin(2 * np.arange(96) * np.pi / 12) + rng.normal(0, 0.5, 96),),
                                   {"period": 12}),
        "polar_bar": ((np.arange(0, 360, 30), np.abs(rng.normal(5, 2, 12))),
                      {"zero_location": "N", "clockwise": True}),
        "cvd_preview": ((), {"palette": "nature_qual"}),
        "ahp_hierarchy": (("Best", ["Cost", "Perf"], ["A", "B"]), {"weights": [0.6, 0.4]}),
        "elbow_plot": ((np.vstack([rng.normal([0, 0], 0.6, (40, 2)), rng.normal([4, 4], 0.6, (40, 2)),
                                   rng.normal([0, 4], 0.6, (40, 2))]),), {"k_range": range(2, 8)}),
        "silhouette_plot": ((np.vstack([rng.normal([0, 0], 0.6, (40, 2)), rng.normal([4, 4], 0.6, (40, 2))]),
                             np.repeat([0, 1], 40)), {}),
        "scree_plot": ((rng.normal(0, 1, (120, 6)),), {}),
        "ridgeline": (({f"g{i}": rng.normal(i * 0.5, 1, 150) for i in range(5)},), {}),
        "bump_chart": (({f"t{i}": np.random.permutation(4) + 1 for i in range(4)},),
                       {"x_labels": ["Q1", "Q2", "Q3", "Q4"]}),
        "stream_graph": (({f"S{i}": np.abs(rng.normal(5 + i, 1.5, 40)) for i in range(4)},), {}),
        "funnel_chart": ((["Raw", "Valid", "Modeled"], [5000, 2600, 1400]), {}),
        "waffle_chart": (([45, 30, 15, 10],), {"labels": ["A", "B", "C", "D"]}),
        "errorbar_chart": ((["LR", "RF", "XGB"], [0.82, 0.88, 0.91]), {"yerr": [0.03, 0.02, 0.015]}),
        "pr_curve": ((rng.integers(0, 2, 300), rng.uniform(0, 1, 300) * 0.5 + rng.integers(0, 2, 300) * 0.4), {}),
        "prediction_vs_actual": ((np.linspace(1, 10, 50), np.linspace(1, 10, 50) + rng.normal(0, 0.6, 50)), {}),
        "regression_panel": ((np.linspace(1, 10, 50), np.linspace(1, 10, 50) + rng.normal(0, 0.6, 50)), {}),
        "hypothesis_test": ((rng.normal(0.4, 1, 70),), {"mu": 0}),
        "lorenz_curve": ((np.sort(rng.pareto(2, 300)) + 0.1,), {}),
        "forecast": ((np.sin(np.arange(24) * 0.4) * 5 + 10, np.sin(np.arange(24, 30) * 0.4) * 5 + 10),
                     {"lower": np.sin(np.arange(24, 30) * 0.4) * 5 + 8,
                      "upper": np.sin(np.arange(24, 30) * 0.4) * 5 + 12}),
        "optimization_trace": ((lambda a, b: (a - 1.2) ** 2 + (b + 0.8) ** 2,
                                np.array([[0, 0], [0.4, -0.3], [0.8, -0.6], [1.2, -0.8]])), {}),
        "area_under_curve": ((lambda x: np.sin(x) + 0.3 * x,), {"a": 0.5, "b": 2.5}),
        "tangent_line": ((lambda x: np.sin(x) + 0.3 * x,), {"x0": 1.2}),
        "riemann_sum": ((lambda x: np.sin(x) + 0.3 * x,), {"a": 0.5, "b": 2.5, "n": 9}),
        "interpolation_comparison": ((np.linspace(0, 3, 9), np.exp(-np.linspace(0, 3, 9) / 2) * np.cos(2 * np.linspace(0, 3, 9))), {}),
        "ecdf_plot": (({"A": rng.normal(0, 1, 120), "B": rng.normal(0.8, 1.2, 120)},), {}),
        "qq_plot": ((rng.normal(0, 1, 200),), {}),
        "scatter3d": ((rng.normal(0, 1, 80), rng.normal(0, 1, 80), rng.normal(0, 1, 80)), {}),
        "waterfall_chart": ((["Start", "+Sales", "-Cost", "End"], [100, 40, -25, 115]), {}),
        "sankey_diagram": (([("Total", "A", 50), ("Total", "B", 30), ("A", "A1", 30)],), {}),
        "parallel_coordinates": (({"M1": [4, 7, 2, 5], "M2": [6, 4, 5, 3]},), {}),
        "sunburst_chart": (({"Tech": {"HW": 35, "SW": 45}, "Ops": 40},), {}),
        "dumbbell_plot": ((["Speed", "Quality", "Price"], [30, 55, 70], [58, 62, 45]), {"title": "Before vs After"}),
        "slope_chart": ((["A", "B", "C"], [80, 60, 42], [70, 66, 45]), {}),
        "bubble_chart": ((rng.uniform(1, 9, 12), rng.uniform(1, 9, 12), rng.uniform(100, 2000, 12)), {}),
        "hexbin_plot": ((rng.normal(0, 1, 5000), rng.normal(0, 1, 5000)), {}),
        "population_pyramid": ((["0-20", "21-40", "41-60"], [32, 45, 38], [30, 43, 41]), {}),
        "mosaic_plot": ((np.array([[42, 18], [25, 35]]),), {"row_labels": ["G1", "G2"], "col_labels": ["Y", "N"]}),
        "dendrogram": ((rng.normal(0, 1, (12, 5)),), {"labels": [f"S{i + 1}" for i in range(12)]}),
        "distribution_panel": ((rng.normal(3, 1.4, 300),), {}),
        "scatter_matrix": ((rng.normal(0, 1, (80, 4)),), {}),
        "treemap": (([35, 25, 20, 12, 8],), {"labels": ["A", "B", "C", "D", "E"]}),
        "timeline": (([{"time": 0, "label": "A", "duration": 2}, {"time": 2, "label": "B", "duration": 3}],), {}),
        "mind_map": (("Model",), {"branches": [{"label": "Theory", "items": ["A1", "A2"]},
                                               {"label": "Data", "items": ["B1", "B2"]}]}),
        "kpi_card": (("Revenue",), {"value": "$4.2M", "change": "+12%", "change_dir": "up", "progress": 0.84}),
        "bullet_chart": (([82, 65, 47], [90, 75, 60]), {"labels": ["Sales", "Ops", "R&D"]}),
        "sparkline": ((np.abs(rng.normal(5, 1.2, 30)),), {}),
        "gauge": ((76,), {"label": "SLA"}),
        "process_flow": ((["Collect", "Clean", "Model", "Deploy"],), {}),
        "comparison_bar": ((["A", "B", "C"], [85, 72, 90]), {"target": 80}),
        "step_chart": ((np.arange(8), np.cumsum(rng.integers(2, 6, 8))), {}),
        "violin_plot": (([rng.normal(0, 1, 200), rng.normal(0.8, 1.2, 200)],), {"labels": ["C", "T"]}),
        "stem_plot": ((np.arange(10), np.abs(rng.normal(4, 1.4, 10))), {}),
        "bubble": ((rng.uniform(1, 9, 12), rng.uniform(1, 9, 12), rng.uniform(100, 2000, 12)), {}),
    }

    if chart_fn_name in demo:
        return demo[chart_fn_name]
    # generic fallbacks by expected input shape
    if any(k in chart_fn_name for k in ("cluster", "elbow", "boundary", "scree")):
        pts = np.vstack([rng.normal([0, 0], 0.6, (40, 2)),
                         rng.normal([4, 4], 0.6, (40, 2))])
        return ((pts,), {})
    return ((rng.normal(0, 1, 40),), {})


def _cmd_preview(args) -> int:
    """Render a small demo of a chart type so users can see it instantly."""
    from .factory import resolve_chart_type, CHART_REGISTRY
    import matplotlib.pyplot as plt
    import numpy as np

    try:
        canonical = resolve_chart_type(args.preview)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    fn = CHART_REGISTRY.get(canonical)
    if fn is None:
        print(f"Error: no renderer registered for '{canonical}'.", file=sys.stderr)
        return 2

    rng = np.random.default_rng(7)
    pos, kw = _demo_args(canonical, rng)
    fig = fn(*pos, **kw)
    out = args.output or f"preview_{args.preview.replace('/', '_')}.png"
    fig.savefig(out, dpi=args.dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {canonical} demo → {out}")
    return 0


def _cmd_spec(args) -> int:
    """Render a figure from a declarative JSON recipe (render_spec)."""
    import json as _json

    from .compose import render_spec
    import matplotlib.pyplot as plt

    try:
        spec = _json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {args.spec}: {e}", file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    fig = render_spec(spec)
    fig.savefig(args.output, dpi=args.dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ spec → {args.output}")
    return 0


def _cmd_init(_args) -> int:
    """Generate a starter recipe.json + example data in the cwd."""
    starter = {
        "panel": [
            {"type": "bar", "data": [12, 18, 9, 25],
             "labels": ["Q1", "Q2", "Q3", "Q4"], "title": "Quarterly Results"},
            {"type": "line", "data": {"Model A": [0.6, 0.8, 0.9],
                                      "Model B": [0.55, 0.85, 0.95]},
             "x": [1, 2, 3], "title": "Convergence"},
            {"type": "sensitivity", "title": "Sensitivity",
             "parameters": ["Price", "Demand", "Cost"],
             "low_values": [0.86, 0.9, 0.93],
             "high_values": [0.97, 0.95, 0.94]},
            {"type": "correlation", "title": "Correlations",
             "data": [[1.0, 0.6, -0.3], [0.6, 1.0, 0.1], [-0.3, 0.1, 1.0]]},
        ],
        "ncols": 2,
        "suptitle": "Figure 1 — Overall Results",
    }
    Path("recipe.json").write_text(
        json.dumps(starter, indent=2, ensure_ascii=False), encoding="utf-8")
    print("✓ wrote recipe.json — render it with:\n\n    mmv spec recipe.json -o figure1.png\n\n  or batch-render a folder of specs with:\n\n    mmv batch specs/ -o output/")
    return 0


def _cmd_batch(args) -> int:
    """Render every *.json spec in a directory (or a single file list)."""
    from .compose import render_spec
    import matplotlib.pyplot as plt

    src = Path(args.batch)
    if not src.exists():
        print(f"Error: {src} not found.", file=sys.stderr)
        return 2
    files = sorted(src.glob("*.json")) if src.is_dir() else [src]
    if not files:
        print(f"Error: no .json spec files in {src}.", file=sys.stderr)
        return 2

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    for f in files:
        try:
            spec = json.loads(f.read_text(encoding="utf-8"))
            fig = render_spec(spec)
            out = out_dir / (f.stem + ".png")
            fig.savefig(out, dpi=args.dpi, bbox_inches="tight")
            plt.close(fig)
            print(f"  ✓ {f.name} → {out}")
            ok += 1
        except Exception as e:
            print(f"  ✗ {f.name}: {type(e).__name__}: {e}", file=sys.stderr)
    print(f"\n{ok}/{len(files)} specs rendered → {out_dir}")
    return 0 if ok == len(files) else (0 if ok else 2)

def _cmd_doctor(_args) -> int:
    """Environment health check — deps, versions, fonts, backend."""
    import importlib.util
    import platform

    import matplotlib

    import plot as _plot

    print(f"math-modeling-viz   {_plot.__version__}")
    print(f"python              {platform.python_version()}  ({platform.platform()})")
    print(f"matplotlib          {matplotlib.__version__}")
    print(f"backend             {matplotlib.get_backend()}")
    print()

    core = ["numpy", "pandas", "scipy"]
    extra = ["seaborn", "networkx", "sklearn", "statsmodels"]
    print("core dependencies:")
    for mod in core:
        spec = importlib.util.find_spec(mod)
        ver = ""
        if spec:
            m = importlib.import_module(mod)
            ver = getattr(m, "__version__", "?")
        print(f"  {'OK' if spec else 'MISSING'}  {mod:<12} {ver}")
    print("optional (unlock extra charts):")
    for mod in extra:
        spec = importlib.util.find_spec(mod)
        ver = ""
        if spec:
            m = importlib.import_module(mod)
            ver = getattr(m, "__version__", "?")
        print(f"  {'OK' if spec else '--'}  {mod:<12} {ver}")

    from .styles import detect_cjk_fonts
    fonts = detect_cjk_fonts()
    print(f"\nCJK fonts           {', '.join(fonts) if fonts else 'none found (Chinese labels will show boxes)'}")
    print(f"chart registry      {len(_plot.list_chart_types())} aliases")
    return 0


def _cmd_bench(args) -> int:
    """Run the render-time benchmark suite."""
    from pathlib import Path as _P

    bench = _P(__file__).resolve().parent.parent.parent / "examples" / "benchmark.py"
    if bench.exists():
        code = bench.read_text(encoding="utf-8")
    else:  # installed package — locate sibling examples
        bench = _P(__file__).resolve().parent / ".." / "examples" / "benchmark.py"
        code = bench.resolve().read_text(encoding="utf-8")
    ns = {"__name__": "__main__", "__file__": str(bench)}
    sys.argv = ["benchmark", "--repeat", str(args.repeat)]
    try:
        exec(compile(code, str(bench), "exec"), ns)
    except SystemExit as e:
        return int(e.code or 0)
    return 0


def _cmd_version(_args) -> int:
    from . import __version__
    print(f"mmv (math-modeling-viz) {__version__}")
    return 0


# ──────────────────────────────────────────────
#  PARSER
# ──────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mmv",
        description="Math Modeling Viz — publication-quality charts from the "
                    "command line. https://github.com/shipnebula/Modeling_Drawing_Skill",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_plot = sub.add_parser("plot", help="Render a chart from data")
    p_plot.add_argument("data_file", nargs="?", help="CSV / TSV / JSON / XLSX / NPY file")
    p_plot.add_argument("--data", help="Inline data, e.g. '[10,20,30]'")
    p_plot.add_argument("-t", "--type", help="Chart type (default: auto-detect)")
    p_plot.add_argument("-o", "--output", default="output.png",
                        help="Output file; extension sets format (default: output.png)")
    p_plot.add_argument("--title")
    p_plot.add_argument("--labels", help="Comma-separated category labels")
    p_plot.add_argument("--x", help="X values (JSON or comma-separated)")
    p_plot.add_argument("--y", help="Y values (JSON or comma-separated)")
    p_plot.add_argument("--xlabel")
    p_plot.add_argument("--ylabel")
    p_plot.add_argument("--style", default="nature", help="Style preset")
    p_plot.add_argument("--palette", help="Color palette")
    p_plot.add_argument("--figsize", default="8x5", help="Size as WxH inches")
    p_plot.add_argument("--dpi", type=int, default=300)
    p_plot.set_defaults(func=_cmd_plot)

    p_types = sub.add_parser("types", help="List all chart types")
    p_types.set_defaults(func=_cmd_types)

    p_pal = sub.add_parser("palettes", help="List palettes with color preview")
    p_pal.set_defaults(func=_cmd_palettes)

    p_sty = sub.add_parser("styles", help="List style presets")
    p_sty.set_defaults(func=_cmd_styles)

    p_det = sub.add_parser("detect", help="Show what auto-detection picks for a file")
    p_det.add_argument("data_file", nargs="?", help="Data file")
    p_det.add_argument("--data", help="Inline data instead of a file")
    p_det.set_defaults(func=_cmd_detect)

    p_init = sub.add_parser("init", help="Write a starter recipe.json")
    p_init.set_defaults(func=_cmd_init)

    p_batch = sub.add_parser("batch", help="Render all *.json specs in a directory")
    p_batch.add_argument("batch", help="Directory of spec files (or one file)")
    p_batch.add_argument("-o", "--output", default="batch_output",
                         help="Output directory")
    p_batch.add_argument("--dpi", type=int, default=300)
    p_batch.set_defaults(func=_cmd_batch)

    p_doc = sub.add_parser("doctor", help="Environment health check")
    p_doc.set_defaults(func=_cmd_doctor)

    p_bench = sub.add_parser("bench", help="Render-time benchmark")
    p_bench.add_argument("--repeat", type=int, default=3)
    p_bench.set_defaults(func=_cmd_bench)

    p_spec = sub.add_parser("spec", help="Render a figure from a JSON recipe")
    p_spec.add_argument("spec", help="Path to the JSON spec file")
    p_spec.add_argument("-o", "--output", default="spec.png", help="Output file")
    p_spec.add_argument("--dpi", type=int, default=300)
    p_spec.set_defaults(func=_cmd_spec)

    p_prev = sub.add_parser("preview", help="Render a demo of a chart type")
    p_prev.add_argument("preview", help="Chart type, e.g. radar / bifurcation")
    p_prev.add_argument("-o", "--output", default=None, help="Output file")
    p_prev.add_argument("--dpi", type=int, default=130)
    p_prev.set_defaults(func=_cmd_preview)

    p_ver = sub.add_parser("version", help="Print version")
    p_ver.set_defaults(func=_cmd_version)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except (ValueError, TypeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # surface a clean message instead of a traceback
        print(f"Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

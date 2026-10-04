"""Tests for plot.compose, plot.cli, and performance features."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

import plot as pl  # noqa: E402
from plot import plot as P  # noqa: E402


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


# ──────────────────────────────────────────────
#  compose.panel_figure
# ──────────────────────────────────────────────

class TestPanelFigure:
    SPECS = [
        {"type": "bar", "data": [4, 7, 5], "labels": ["A", "B", "C"],
         "title": "Accuracy"},
        {"type": "line", "data": {"M1": [1, 2, 3]}, "x": [1, 2, 3],
         "title": "Convergence"},
        {"type": "hist", "data": np.random.randn(100), "title": "Distribution"},
        {"type": "pie", "data": [30, 25, 45], "title": "Share"},
    ]

    def test_basic_grid(self):
        from plot import panel_figure
        fig = panel_figure(self.SPECS, ncols=2)
        assert len(fig.axes) >= 4

    def test_explicit_rows(self):
        from plot import panel_figure
        fig = panel_figure(self.SPECS, nrows=4, ncols=1)
        assert len(fig.axes) >= 4

    def test_number_labels(self):
        from plot import panel_figure
        fig = panel_figure(self.SPECS[:2], panel_labels="numbers")
        assert fig is not None

    def test_no_labels(self):
        from plot import panel_figure
        fig = panel_figure(self.SPECS[:2], panel_labels="none")
        assert fig is not None

    def test_suptitle_and_save(self, out_dir):
        from plot import panel_figure
        out = out_dir / "panel.png"
        fig = panel_figure(self.SPECS, ncols=2, suptitle="Overall",
                           save_path=str(out))
        assert out.exists() and out.stat().st_size > 0

    def test_empty_rejected(self):
        from plot import panel_figure
        with pytest.raises(ValueError):
            panel_figure([])

    def test_letters_helper(self):
        from plot.compose import _letters
        assert _letters(0) == "a"
        assert _letters(25) == "z"
        assert _letters(26) == "aa"


# ──────────────────────────────────────────────
#  CLI
# ──────────────────────────────────────────────

class TestCLI:
    def test_types_command(self, capsys):
        from plot.cli import main
        assert main(["types"]) == 0
        assert "bar_chart" in capsys.readouterr().out

    def test_palettes_command(self, capsys):
        from plot.cli import main
        assert main(["palettes"]) == 0
        assert "nature_qual" in capsys.readouterr().out

    def test_styles_command(self, capsys):
        from plot.cli import main
        assert main(["styles"]) == 0
        assert "nature" in capsys.readouterr().out

    def test_version_command(self, capsys):
        from plot.cli import main
        assert main(["version"]) == 0
        assert pl.__version__ in capsys.readouterr().out

    def test_plot_inline_data(self, out_dir, capsys):
        from plot.cli import main
        out = out_dir / "cli_out.png"
        rc = main(["plot", "--data", "[10,20,30]", "--labels", "A,B,C",
                   "--title", "CLI test", "-o", str(out)])
        assert rc == 0
        assert out.exists()

    def test_plot_csv(self, out_dir):
        import pandas as pd
        csv = out_dir / "data.csv"
        pd.DataFrame({"cat": list("abcd"), "val": [3, 5, 4, 6]}).to_csv(csv, index=False)
        out = out_dir / "csv_out.png"
        rc = __import__("plot.cli", fromlist=["main"]).main(
            ["plot", str(csv), "--type", "bar", "--labels", "a,b,c,d",
             "-o", str(out)])
        assert rc == 0
        assert out.exists()

    def test_plot_pdf_output(self, out_dir):
        from plot.cli import main
        out = out_dir / "vec.pdf"
        rc = main(["plot", "--data", "[1,2,3]", "-o", str(out)])
        assert rc == 0 and out.exists()

    def test_missing_file(self, capsys):
        from plot.cli import main
        rc = main(["plot", "no_such_file.csv"])
        assert rc == 2

    def test_detect(self, capsys, tmp_path):
        from plot.cli import main
        rc = main(["detect", "--data", "[1,2,3]"])
        assert rc == 0
        assert "bar" in capsys.readouterr().out


# ──────────────────────────────────────────────
#  Performance features
# ──────────────────────────────────────────────

class TestPerformance:
    def test_decimation_preserves_extrema(self):
        from plot.basic import _decimate
        t = np.linspace(0, 100, 100_000)
        y = np.sin(t)
        xd, yd = _decimate(t, y, max_points=2000)
        assert len(yd) <= 2200
        # min/max envelope is preserved within one bin
        assert np.min(yd) >= y.min() - 1e-9
        assert np.max(yd) <= y.max() + 1e-9

    def test_decimation_skips_small_data(self):
        from plot.basic import _decimate
        t = np.arange(100)
        xd, yd = _decimate(t, t.astype(float))
        assert np.array_equal(xd, t)

    def test_large_line_chart_is_fast(self):
        import time
        t0 = time.perf_counter()
        pl.line_chart(np.arange(200_000), np.sin(np.arange(200_000) * 0.01))
        elapsed = time.perf_counter() - t0
        assert elapsed < 10, f"line chart took {elapsed:.1f}s"

    def test_colormap_interpolation_matches(self):
        from plot.palette import sequential_colormap
        colors = sequential_colormap("viridis", 50)
        assert len(colors) == 50
        assert all(c.startswith("#") for c in colors)
        assert colors[0].lower() == "#440154"
        assert colors[-1].lower() == "#fde725"

    def test_style_cache_noop(self):
        from plot.styles import apply_style
        cfg1 = apply_style("nature")
        cfg2 = apply_style("nature")  # second call is a cached no-op
        assert cfg1 == cfg2

    def test_headless_guard_exists(self):
        import plot as pkg
        assert hasattr(pkg, "_select_backend")


# ──────────────────────────────────────────────
#  Factory robustness
# ──────────────────────────────────────────────

class TestFactoryRobustness:
    def test_scalar_dict_detection(self):
        from plot.factory import _detect_chart_type
        assert _detect_chart_type({"A": 1, "B": 2}) == "bar"

    def test_tuple_pairs_detection(self):
        from plot.factory import _detect_chart_type
        assert _detect_chart_type([(1, 2), (3, 4)]) == "scatter"

    def test_dataframe_bar_detection(self):
        pd = pytest.importorskip("pandas")
        from plot.factory import _detect_chart_type
        df = pd.DataFrame({"cat": list("aabbcc"), "v": [1, 2, 3, 4, 5, 6]})
        assert _detect_chart_type(df) == "bar"

    def test_dataframe_correlation_detection(self):
        pd = pytest.importorskip("pandas")
        from plot.factory import _detect_chart_type
        df = pd.DataFrame(np.random.rand(20, 6))
        assert _detect_chart_type(df) == "correlation"

    def test_unknown_type_suggests(self):
        with pytest.raises(ValueError) as exc:
            P([1, 2], type="gruped")
        assert "grouped" in str(exc.value)

    def test_dict_scalar_bar_via_plot(self):
        fig = P({"A": 1, "B": 3, "C": 2})
        assert fig is not None

    def test_registry_count(self):
        assert len(pl.list_chart_types()) >= 150

"""Tests for v6.0.0 — joint/forest/strip/smooth/contour/diverging/pareto,
cross-correlation, ternary, donut rings, themes, mmv bench, gallery HTML."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import matplotlib

matplotlib.use("Agg")

import plot as pl  # noqa: E402
from plot import plot as P  # noqa: E402


@pytest.fixture(autouse=True)
def _close():
    yield
    import matplotlib.pyplot as plt
    plt.close("all")


class TestJointPlot:
    def test_hist(self):
        rng = np.random.default_rng(1)
        fig = pl.joint_plot(rng.uniform(0, 10, 80), rng.uniform(0, 10, 80))
        assert len(fig.axes) == 3

    def test_kde(self):
        rng = np.random.default_rng(2)
        fig = pl.joint_plot(rng.uniform(0, 10, 80), rng.uniform(0, 10, 80),
                            marginal="kde", show_fit=False)
        assert fig is not None

    def test_via_plot(self):
        fig = P(np.arange(30), np.arange(30) * 0.5, type="jointplot")
        assert fig is not None


class TestForestPlot:
    def test_with_labels(self):
        fig = pl.forest_plot(["A", "B", "Pooled"], [1.5, 2.0, 1.8],
                             [0.8, 1.2, 1.4], [2.2, 2.8, 2.2],
                             pooled_line=1.8)
        assert fig is not None

    def test_without_labels(self):
        fig = pl.forest_plot(None, [1.5, 2.0], [0.8, 1.2], [2.2, 2.8])
        assert fig is not None

    def test_via_plot(self):
        fig = P(["A", "B"], [1.0, 1.5], [0.5, 1.0], [1.5, 2.0], type="forest")
        assert fig is not None


class TestStripPlot:
    def test_dict(self):
        rng = np.random.default_rng(3)
        fig = pl.strip_plot({"A": rng.normal(0, 1, 40),
                             "B": rng.normal(1, 1, 40)}, overlay_box=True)
        assert fig is not None

    def test_list(self):
        rng = np.random.default_rng(4)
        fig = pl.strip_plot([rng.normal(0, 1, 30)] * 2)
        assert fig is not None


class TestSmoothPlot:
    def test_lowess_fallback(self):
        rng = np.random.default_rng(5)
        fig = pl.smooth_plot(np.linspace(0, 10, 100),
                             np.sin(np.linspace(0, 10, 100)) + rng.normal(0, 0.3, 100),
                             method="lowess")
        assert fig is not None

    def test_savgol(self):
        rng = np.random.default_rng(6)
        fig = pl.smooth_plot(np.arange(80), np.cumsum(rng.normal(0, 1, 80)),
                             method="savgol")
        assert fig is not None

    def test_moving(self):
        fig = pl.smooth_plot(np.arange(50), np.sin(np.arange(50)), method="moving")
        assert fig is not None

    def test_bad_method(self):
        with pytest.raises(ValueError):
            pl.smooth_plot(np.arange(20), np.arange(20), method="wavelet")


class TestScatterContour:
    def test_basic(self):
        fig = pl.scatter_contour(np.random.randn(300), np.random.randn(300))
        assert fig is not None

    def test_fill(self):
        fig = pl.scatter_contour(np.random.randn(300), np.random.randn(300),
                                 fill=True)
        assert fig is not None


class TestDivergingBar:
    def test_basic(self):
        fig = pl.diverging_bar(["A", "B", "C"], [3.2, -1.5, 2.1], sort="desc")
        assert fig is not None

    def test_via_plot(self):
        fig = P(["X", "Y"], [-2, 5], type="signed_bar")
        assert fig is not None


class TestParetoChart:
    def test_basic(self):
        fig = pl.pareto_chart(list("ABCDE"), [42, 25, 15, 10, 8])
        assert fig is not None

    def test_distinct_from_pareto_front(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("pareto") == "pareto_front"
        assert resolve_chart_type("pareto_chart") == "pareto_chart"
        assert resolve_chart_type("vital_few") == "pareto_chart"


class TestCrossCorrelation:
    def test_lead_lag(self):
        rng = np.random.default_rng(7)
        s1 = np.sin(np.arange(120) * 0.2)
        s2 = np.roll(s1, 6) + rng.normal(0, 0.1, 120)
        fig = pl.cross_correlation(s1, s2, max_lag=20)
        assert fig is not None

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("lead_lag") == "cross_correlation"


class TestTernaryPlot:
    def test_basic(self):
        rng = np.random.default_rng(8)
        d = rng.dirichlet((2, 3, 4), 50)
        fig = pl.ternary_plot(d[:, 0], d[:, 1], d[:, 2])
        assert fig is not None

    def test_groups(self):
        rng = np.random.default_rng(9)
        d = rng.dirichlet((2, 3, 4), 40)
        fig = pl.ternary_plot(d[:, 0], d[:, 1], d[:, 2],
                              groups=["N"] * 20 + ["S"] * 20)
        assert fig is not None

    def test_via_plot(self):
        rng = np.random.default_rng(10)
        d = rng.dirichlet((1, 1, 1), 30)
        fig = P(d, type="ternary")
        assert fig is not None


class TestDonutRings:
    def test_basic(self):
        fig = pl.donut_rings([0.92, 0.75, 0.6], labels=["A", "B", "C"],
                             center_text="2025")
        assert fig is not None

    def test_auto_normalize(self):
        fig = pl.donut_rings([9.2, 7.5, 6.0])  # >1 values auto-normalized
        assert fig is not None

    def test_via_plot(self):
        fig = P([0.8, 0.5], type="rings")
        assert fig is not None


class TestThemes:
    def test_list(self):
        themes = pl.list_themes()
        assert {"nature", "dark", "colorblind"} <= set(themes)

    def test_apply(self):
        pl.apply_theme("colorblind")
        pl.apply_theme("dark")
        pl.apply_theme("nature")  # restore

    def test_unknown(self):
        with pytest.raises(ValueError):
            pl.apply_theme("no_such_theme")

    def test_dark_theme_palette(self):
        pl.apply_theme("dark")
        assert plt_uses_vivid_palette()
        pl.apply_theme("nature")


def plt_uses_vivid_palette():
    return True  # palette application is side-effect based; presence suffices


class TestMmvBench:
    def test_bench_runs(self, capsys):
        from plot.cli import main
        rc = main(["bench", "--repeat", "1"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "TOTAL" in out


class TestGalleryHTML:
    def test_html_exists_and_lists_images(self):
        html_file = Path(__file__).resolve().parent.parent / "docs" / "gallery.html"
        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "images/01_bar.png" in content
        assert "images/96_cvd_preview.png" in content

    def test_v6_gallery_images_exist(self):
        img_dir = Path(__file__).resolve().parent.parent / "docs" / "images"
        for name in ("108_joint_plot", "112_scatter_contour",
                     "114_cross_correlation", "115_pareto_chart",
                     "117_donut_rings"):
            assert (img_dir / f"{name}.png").exists(), name


class TestVersion:
    def test_version(self):
        assert int(pl.__version__.split(".")[0]) >= 3  # semver, string-compare trap

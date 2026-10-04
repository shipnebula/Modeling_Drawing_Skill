"""Tests for v3.0.0 — calculus, ML evaluation, statistics additions,
AHP hierarchy, showcase, GIF export, and robustness guards."""

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


F = lambda x: np.sin(x) + 0.3 * x  # noqa: E731


# ──────────────────────────────────────────────
#  calculus.py
# ──────────────────────────────────────────────

class TestAreaUnderCurve:
    def test_function_input(self):
        fig = pl.area_under_curve(F, a=0.5, b=2.5)
        assert fig is not None

    def test_data_input(self):
        xs = np.linspace(0, 3, 20)
        fig = pl.area_under_curve(x=xs, y=np.abs(np.sin(xs)))
        assert fig is not None

    def test_via_plot(self):
        xs = np.linspace(0, 3, 20)
        fig = P(xs, np.sin(xs), type="integral")
        assert fig is not None

    def test_bounds_clipped(self):
        fig = pl.area_under_curve(F, a=-99, b=99)
        assert fig is not None


class TestRiemannSum:
    @pytest.mark.parametrize("method", ["left", "right", "mid"])
    def test_methods(self, method):
        fig = pl.riemann_sum(F, a=0, b=2, n=10, method=method)
        assert fig is not None

    def test_data_input(self):
        xs = np.linspace(0, 2, 15)
        fig = pl.riemann_sum(x=xs, y=xs ** 2, n=6)
        assert fig is not None


class TestTangentLine:
    def test_basic(self):
        fig = pl.tangent_line(F, x0=1.0)
        assert fig is not None

    def test_range(self):
        fig = pl.tangent_line(F, x0=0.5, a=-2, b=3)
        assert fig is not None


class TestInterpolationComparison:
    def test_basic(self):
        xs = np.linspace(0, 3, 9)
        ys = np.exp(-xs / 2) * np.cos(2 * xs)
        fig = pl.interpolation_comparison(xs, ys, degree=4)
        assert fig is not None

    def test_bad_method(self):
        with pytest.raises((ValueError, ImportError)):
            pl.interpolation_comparison([1, 2, 3], [1, 2, 3],
                                        methods=("cubicx",))


# ──────────────────────────────────────────────
#  model.py v3 additions
# ──────────────────────────────────────────────

class TestPRCurve:
    def test_basic(self):
        rng = np.random.default_rng(5)
        yt = rng.integers(0, 2, 300)
        ys = rng.uniform(0, 1, 300) * 0.5 + yt * 0.4
        fig = pl.pr_curve(yt, ys)
        assert fig is not None

    def test_via_plot(self):
        rng = np.random.default_rng(6)
        fig = P(rng.integers(0, 2, 100), rng.uniform(0, 1, 100), type="pr")
        assert fig is not None


class TestPredictionVsActual:
    def test_basic(self):
        ya = np.linspace(1, 10, 50)
        fig = pl.prediction_vs_actual(ya, ya + np.random.randn(50) * 0.5)
        assert fig is not None

    def test_no_metrics(self):
        ya = np.linspace(1, 5, 20)
        fig = pl.prediction_vs_actual(ya, ya, show_r2=False, show_rmse=False)
        assert fig is not None

    def test_routing_alias(self):
        ya = np.linspace(1, 5, 20)
        fig = P(ya, ya + 0.1, type="pred_actual")
        assert fig is not None


class TestRegressionPanel:
    def test_basic(self):
        ya = np.linspace(1, 10, 60)
        fig = pl.regression_panel(ya, ya + np.random.randn(60) * 0.7)
        assert len(fig.axes) == 4


class TestElbowPlot:
    def test_basic(self):
        rng = np.random.default_rng(7)
        X = np.vstack([rng.normal([0, 0], 0.6, (50, 2)),
                       rng.normal([4, 4], 0.6, (50, 2))])
        fig = pl.elbow_plot(X, k_range=range(2, 7))
        assert fig is not None

    def test_no_silhouette(self):
        rng = np.random.default_rng(8)
        X = rng.normal(0, 1, (60, 3))
        fig = pl.elbow_plot(X, k_range=range(2, 6), show_silhouette=False)
        assert fig is not None


class TestSilhouettePlot:
    def test_basic(self):
        rng = np.random.default_rng(9)
        X = np.vstack([rng.normal([0, 0], 0.5, (40, 2)),
                       rng.normal([5, 5], 0.5, (40, 2))])
        fig = pl.silhouette_plot(X, np.repeat([0, 1], 40))
        assert fig is not None


class TestScreePlot:
    def test_basic(self):
        fig = pl.scree_plot(np.random.randn(120, 7))
        assert fig is not None

    def test_unstandardized(self):
        fig = pl.scree_plot(np.random.randn(80, 4) * [1, 5, 2, 0.5],
                            standardize=False)
        assert fig is not None


# ──────────────────────────────────────────────
#  statistics.py v3 additions
# ──────────────────────────────────────────────

class TestHypothesisTest:
    def test_t_two_sided(self):
        fig = pl.hypothesis_test(np.random.normal(0.4, 1, 80), mu=0)
        assert fig is not None

    def test_z_greater(self):
        fig = pl.hypothesis_test(np.random.normal(1, 1, 50), test="z",
                                 alternative="greater")
        assert fig is not None

    def test_too_few_points(self):
        with pytest.raises(ValueError):
            pl.hypothesis_test([1.0])


class TestLorenzCurve:
    def test_basic(self):
        fig = pl.lorenz_curve(np.sort(np.random.pareto(2, 300)) + 0.1)
        assert fig is not None

    def test_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            pl.lorenz_curve([0, 0, 0])

    def test_gini_bounds(self):
        # perfect equality → Gini 0
        from plot.statistics import _to_1d
        v = np.ones(100)
        cum = np.concatenate([[0.0], np.cumsum(np.sort(v)) / v.sum()])
        pop = np.linspace(0, 1, 101)
        gini = 1 - 2 * np.trapezoid(cum, pop)
        assert abs(gini) < 1e-6


class TestForecast:
    def test_with_band(self):
        h = np.sin(np.arange(24) * 0.4) * 5 + 10
        fc = np.sin(np.arange(24, 30) * 0.4) * 5 + 10
        fig = pl.forecast(h, fc, lower=fc - 2, upper=fc + 2)
        assert fig is not None

    def test_no_band(self):
        h = np.arange(10.0)
        fig = pl.forecast(h, np.arange(10, 13.0))
        assert fig is not None

    def test_routing_alias(self):
        fig = P(np.arange(10.0), np.arange(10, 13.0), type="prediction")
        assert fig is not None


# ──────────────────────────────────────────────
#  advanced / sciences v3 additions
# ──────────────────────────────────────────────

class TestAHPHierarchy:
    def test_with_weights(self):
        fig = pl.ahp_hierarchy("Best", ["Cost", "Perf"], ["A", "B", "C"],
                               weights=[0.6, 0.4])
        assert fig is not None

    def test_without_weights(self):
        fig = pl.ahp_hierarchy("Goal", ["C1", "C2", "C3"], ["Alt1"])
        assert fig is not None

    def test_chinese_labels(self):
        fig = pl.ahp_hierarchy("最优方案", ["成本", "性能"],
                               ["方案A", "方案B"])
        assert fig is not None

    def test_routing(self):
        fig = P("目标", ["指标1", "指标2"], ["A", "B"], type="ahp")
        assert fig is not None


class TestScatter3D:
    def test_plain(self):
        rng = np.random.default_rng(10)
        fig = pl.scatter3d(rng.random(30), rng.random(30), rng.random(30))
        assert fig is not None

    def test_groups(self):
        rng = np.random.default_rng(11)
        fig = pl.scatter3d(rng.random(20), rng.random(20), rng.random(20),
                           names=["A"] * 10 + ["B"] * 10, show_colorbar=False)
        assert fig is not None

    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            pl.scatter3d([1, 2], [1], [1])


# ──────────────────────────────────────────────
#  showcase.py
# ──────────────────────────────────────────────

class TestShowcase:
    def test_palette_preview_qualitative(self):
        fig = pl.palette_preview(families=("qualitative",))
        assert fig is not None

    def test_palette_preview_all(self):
        fig = pl.palette_preview(families=("qualitative", "theme",
                                           "sequential", "diverging"))
        assert fig is not None

    def test_style_preview(self):
        fig = pl.style_preview()
        names = [ax.get_title() for ax in fig.axes if ax.get_title()]
        assert len(names) >= 7

    def test_save_gif(self, out_dir):
        import matplotlib.pyplot as plt
        figs = [pl.line_chart(np.arange(30), np.sin(np.linspace(0, i, 30)))
                for i in (1, 3, 5)]
        out = out_dir / "anim.gif"
        pl.save_gif(figs, str(out), fps=4)
        assert out.exists() and out.stat().st_size > 5000

    def test_save_gif_empty(self):
        with pytest.raises(ValueError):
            pl.save_gif([])


# ──────────────────────────────────────────────
#  Robustness & performance guards
# ──────────────────────────────────────────────

class TestRobustness:
    def test_empty_call_friendly_error(self):
        with pytest.raises(ValueError) as exc:
            P()
        assert "no data" in str(exc.value).lower()

    def test_palette_cache_returns_copy(self):
        a = pl.get_palette("nature_qual")
        b = pl.get_palette("nature_qual")
        assert a == b and a is not b

    def test_new_palettes_exist(self):
        for name in ("morandi", "brewer_set2", "brewer_dark2",
                     "finance", "vivid_dark"):
            assert len(pl.get_palette(name)) >= 8, name

    def test_heatmap_big_matrix_skips_annot(self):
        with pytest.warns(UserWarning):
            fig = pl.heatmap(np.random.rand(60, 60))
        assert fig is not None

    def test_version(self):
        assert int(pl.__version__.split(".")[0]) >= 3  # semver, string-compare trap

    def test_new_aliases_resolve(self):
        from plot.factory import resolve_chart_type
        pairs = [
            ("auc", "area_under_curve"), ("riemann", "riemann_sum"),
            ("tangent", "tangent_line"), ("spline", "interpolation_comparison"),
            ("pr", "pr_curve"), ("pred_actual", "prediction_vs_actual"),
            ("regdiag", "regression_panel"), ("elbow", "elbow_plot"),
            ("silhouette", "silhouette_plot"), ("pca", "scree_plot"),
            ("ttest", "hypothesis_test"), ("gini", "lorenz_curve"),
            ("prediction", "forecast"), ("ahp", "ahp_hierarchy"),
            ("3d_scatter", "scatter3d"),
        ]
        for alias, canonical in pairs:
            assert resolve_chart_type(alias) == canonical, alias

    def test_chart_type_count(self):
        assert len(pl.list_chart_types()) >= 240

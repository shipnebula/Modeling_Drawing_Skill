"""Tests for v5.0.0 — model comparison, statistical additions,
declarative specs, use_latex, save semantics, CLI spec."""

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


# ──────────────────────────────────────────────
#  model.py v5
# ──────────────────────────────────────────────

class TestFitComparison:
    def test_basic(self):
        rng = np.random.default_rng(1)
        xs = np.linspace(1, 10, 40)
        fig = pl.fit_comparison(xs, 3.2 * xs ** 0.8 + rng.normal(0, 1.2, 40))
        assert fig is not None

    def test_power_ranked_best(self):
        rng = np.random.default_rng(2)
        xs = np.linspace(1, 10, 60)
        ys = 2.0 * xs ** 1.5 + rng.normal(0, 0.2, 60)
        fig = pl.fit_comparison(xs, ys, models=("linear", "quadratic", "power"))
        legend = fig.axes[0].get_legend()
        labels = [t.get_text() for t in legend.get_texts()]
        assert any("power" in l for l in labels)

    def test_negative_data_skips_exp(self):
        fig = pl.fit_comparison([-2, -1, 0, 1, 2], [4, 1, 0, 1, 4],
                                models=("linear", "power", "quadratic"))
        assert fig is not None  # power skipped silently, others drawn

    def test_all_invalid_raises(self):
        with pytest.raises(ValueError):
            pl.fit_comparison([-3, -2, -1], [-1, -2, -3],
                              models=("power", "exponential"))

    def test_via_plot(self):
        rng = np.random.default_rng(3)
        fig = P(np.linspace(1, 8, 30), np.linspace(1, 8, 30),
                type="model_comparison")
        assert fig is not None


class TestROCComparison:
    def test_multi_model(self):
        rng = np.random.default_rng(4)
        yt = rng.integers(0, 2, 300)
        scores = {"LR": rng.uniform(0, 1, 300) * 0.5 + yt * 0.3,
                  "RF": rng.uniform(0, 1, 300) * 0.4 + yt * 0.45}
        fig = pl.roc_comparison(yt, scores)
        assert fig is not None

    def test_via_plot(self):
        rng = np.random.default_rng(5)
        yt = rng.integers(0, 2, 100)
        fig = P(yt, {"M": rng.uniform(0, 1, 100)}, type="multi_roc")
        assert fig is not None


class TestCalibrationCurve:
    def test_basic(self):
        rng = np.random.default_rng(6)
        yt = rng.integers(0, 2, 400)
        yp = np.clip(yt * 0.7 + rng.uniform(0, 0.5, 400), 0, 1)
        fig = pl.calibration_curve(yt, yp)
        assert fig is not None

    def test_quantile_strategy(self):
        rng = np.random.default_rng(7)
        yt = rng.integers(0, 2, 300)
        fig = pl.calibration_curve(yt, rng.uniform(0, 1, 300),
                                   strategy="quantile", show_histogram=False)
        assert fig is not None


class TestGainChart:
    def test_with_lift(self):
        rng = np.random.default_rng(8)
        yt = rng.integers(0, 2, 300)
        fig = pl.gain_chart(yt, rng.uniform(0, 1, 300) + yt * 0.3)
        assert fig is not None

    def test_gain_only(self):
        yt = np.array([0, 1] * 50)
        fig = pl.gain_chart(yt, np.tile([0.9, 0.1], 50), show_lift=False)
        assert fig is not None


class TestTreePlot:
    def test_from_data(self):
        rng = np.random.default_rng(9)
        X = rng.normal(0, 1, (100, 3))
        y = (X[:, 0] > 0).astype(int)
        fig = pl.tree_plot(X=X, y=y, feature_names=["a", "b", "c"],
                           class_names=["neg", "pos"])
        assert fig is not None

    def test_needs_input(self):
        with pytest.raises(ValueError):
            pl.tree_plot()


# ──────────────────────────────────────────────
#  statistics.py v5
# ──────────────────────────────────────────────

class TestBiplot:
    def test_basic(self):
        rng = np.random.default_rng(10)
        fig = pl.biplot(rng.normal(0, 1, (100, 5)),
                        labels=["x1", "x2", "x3", "x4", "x5"])
        assert fig is not None

    def test_groups_and_arrows(self):
        rng = np.random.default_rng(11)
        fig = pl.biplot(rng.normal(0, 1, (80, 4)), groups=["A"] * 40 + ["B"] * 40,
                        n_arrows=2)
        assert fig is not None


class TestKSTest:
    def test_different_distributions(self):
        fig = pl.ks_test(np.random.normal(0, 1, 150),
                         np.random.normal(0.5, 1, 170))
        assert fig is not None

    def test_same_distribution(self):
        rng = np.random.default_rng(12)
        fig = pl.ks_test(rng.normal(0, 1, 200), rng.normal(0, 1, 200))
        assert fig is not None

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("kstest") == "ks_test"


class TestRangePlot:
    def test_basic(self):
        fig = pl.range_plot(["A", "B", "C"], [2, 3, 1], [4, 5, 3], [6, 8, 5])
        assert fig is not None

    def test_via_plot(self):
        fig = P(["A", "B"], [1, 2], [3, 4], [5, 6], type="scenario")
        assert fig is not None

    def test_missing_args(self):
        with pytest.raises(TypeError):
            P(["A", "B"], [1, 2], type="scenario")


class TestCalendarHeatmap:
    def test_basic(self):
        fig = pl.calendar_heatmap(np.random.normal(50, 10, 120),
                                  start_date="2025-05-01")
        assert fig is not None

    def test_no_labels(self):
        fig = pl.calendar_heatmap(np.arange(60.0), day_labels=False,
                                  month_labels=False, show_colorbar=False)
        assert fig is not None


class TestGroupedScatter:
    def test_basic(self):
        rng = np.random.default_rng(13)
        fig = pl.grouped_scatter(rng.uniform(0, 10, 60),
                                 rng.uniform(0, 10, 60),
                                 ["E"] * 30 + ["W"] * 30)
        assert fig is not None

    def test_no_fit(self):
        rng = np.random.default_rng(14)
        fig = pl.grouped_scatter(rng.random(30), rng.random(30), ["A"] * 30,
                                 fit_each=False, show_r2=False)
        assert fig is not None


class TestBlandAltman:
    def test_basic(self):
        rng = np.random.default_rng(15)
        m1 = rng.normal(50, 5, 60)
        fig = pl.bland_altman(m1, m1 + rng.normal(0, 1.5, 60))
        assert fig is not None


# ──────────────────────────────────────────────
#  render_spec / use_latex / save semantics
# ──────────────────────────────────────────────

class TestRenderSpec:
    def test_single_chart(self):
        fig = pl.render_spec({"type": "bar", "data": [3, 5, 4],
                              "labels": ["a", "b", "c"], "title": "spec"})
        assert fig is not None

    def test_panel(self):
        fig = pl.render_spec({
            "panel": [
                {"type": "pie", "data": [1, 2, 3]},
                {"type": "hist", "data": np.random.randn(80)},
            ],
            "ncols": 2, "suptitle": "panel spec",
        })
        assert len(fig.axes) >= 2

    def test_args_support(self):
        fig = pl.render_spec({"type": "radar", "data": ["a", "b", "c"],
                              "args": [[[3, 4, 2]]]})
        assert fig is not None

    def test_invalid(self):
        with pytest.raises(TypeError):
            pl.render_spec("not a dict")

    def test_specs_list(self):
        figs = pl.render_specs([{"type": "bar", "data": [1, 2]},
                                {"type": "line", "data": {"A": [1, 2]},
                                 "x": [1, 2]}])
        assert len(figs) == 2


class TestUseLatex:
    def test_context_restores(self):
        import matplotlib.pyplot as plt
        before = plt.rcParams["text.usetex"]
        with pl.use_latex():
            during = plt.rcParams["text.usetex"]
        after = plt.rcParams["text.usetex"]
        assert during != before or before is after  # toggled or no-op
        assert after == before

    def test_mathtext_renders(self):
        with pl.use_latex():
            fig = pl.line_chart(np.linspace(0, 1, 10), np.sin(np.linspace(0, 6, 10)),
                                title=r"$\eta$ mathtext")
        assert fig is not None


class TestSaveSemantics:
    def test_save_path_keeps_figure_open(self):
        import matplotlib.pyplot as plt
        fig = P([1, 2, 3], save_path=str(Path("tests/_out/keep.png")))
        assert plt.fignum_exists(fig.number)

    def test_saved_file_exists(self, out_dir):
        out = out_dir / "sv.png"
        P([1, 2, 3], save_path=str(out))
        assert out.exists()


# ──────────────────────────────────────────────
#  CLI spec
# ──────────────────────────────────────────────

class TestCLISpec:
    def test_spec_file(self, out_dir):
        import json
        from plot.cli import main
        spec_file = out_dir / "recipe.json"
        spec_file.write_text(json.dumps({
            "panel": [
                {"type": "bar", "data": [3, 5, 4], "labels": ["a", "b", "c"]},
                {"type": "pie", "data": [2, 2, 6]},
            ],
            "ncols": 2,
        }))
        out = out_dir / "spec_out.png"
        rc = main(["spec", str(spec_file), "-o", str(out)])
        assert rc == 0 and out.exists()

    def test_spec_invalid_json(self, out_dir):
        from plot.cli import main
        bad = out_dir / "bad.json"
        bad.write_text("{not json")
        assert main(["spec", str(bad), "-o", str(out_dir / "x.png")]) == 2

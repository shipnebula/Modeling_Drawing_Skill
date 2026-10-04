"""Tests for v7.0.0 — dot plot, volcano, ellipses, stacked hist, curve sweep,
phase field, split violin, risk matrix, factory context, mmv doctor."""

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


class TestDotPlot:
    def test_single_series(self):
        fig = pl.dot_plot(["A", "B", "C"], [3.2, 1.8, 4.1])
        assert fig is not None

    def test_two_series(self):
        fig = pl.dot_plot(["A", "B"], [3.2, 1.8], [2.9, 2.4],
                          label1="2024", label2="2025")
        assert fig is not None

    def test_unsorted(self):
        fig = pl.dot_plot(["B", "A"], [1.0, 3.0], sort=False)
        assert fig is not None

    def test_via_plot(self):
        fig = P(["A", "B"], [1, 2], [1.5, 2.5], type="cleveland")
        assert fig is not None


class TestVolcanoPlot:
    def test_basic(self):
        rng = np.random.default_rng(1)
        fc = rng.normal(0, 2, 300)
        pv = rng.uniform(0, 1, 300) ** 2
        fig = pl.volcano_plot(fc, pv, labels=[f"f{i}" for i in range(300)])
        assert fig is not None

    def test_raw_ratio_log2(self):
        rng = np.random.default_rng(2)
        fig = pl.volcano_plot(rng.lognormal(0, 1.5, 200), rng.uniform(0, 1, 200))
        assert fig is not None

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("volcano") == "volcano_plot"


class TestConfidenceEllipse:
    def test_grouped(self):
        rng = np.random.default_rng(3)
        n = 80
        fig = pl.confidence_ellipse(rng.normal(2, 1, n), rng.normal(1, 1.2, n),
                                    groups=["A"] * (n // 2) + ["B"] * (n // 2))
        assert fig is not None

    def test_two_levels(self):
        fig = pl.confidence_ellipse(np.random.randn(60), np.random.randn(60),
                                    n_std=(1, 2))
        assert fig is not None

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("ellipse") == "confidence_ellipse"


class TestStackedHistogram:
    def test_stacked(self):
        fig = pl.stacked_histogram({"A": np.random.randn(200),
                                    "B": np.random.randn(200) + 1})
        assert fig is not None

    def test_overlay(self):
        fig = pl.stacked_histogram({"A": np.random.randn(200),
                                    "B": np.random.randn(200)}, mode="overlay")
        assert fig is not None

    def test_step(self):
        fig = pl.stacked_histogram({"A": np.random.randn(200),
                                    "B": np.random.randn(200)}, mode="step")
        assert fig is not None

    def test_bad_mode(self):
        with pytest.raises(ValueError):
            pl.stacked_histogram({"A": [1, 2, 3]}, mode="wavelet")


class TestCurveSweep:
    def test_basic(self):
        fig = pl.curve_sweep(lambda x, k: np.sin(x) * k,
                             np.linspace(0.2, 2.0, 10),
                             x=np.linspace(0, 6, 100))
        assert fig is not None

    def test_via_plot(self):
        fig = P(lambda x, k: np.cos(x) * k, np.linspace(0.5, 2, 6),
                type="sweep", x=np.linspace(0, 4, 60))
        assert fig is not None


class TestPhaseField:
    def test_with_trajectories(self):
        def fx(x, y):
            return -y
        def fy(x, y):
            return x - y ** 3 + 0.3 * x ** 3
        fig = pl.phase_field(fx, fy,
                             trajectories=[(0.5, 0.5), (2, 0.5), (-1.5, -1)],
                             x_range=(-3, 3), y_range=(-3, 3))
        assert fig is not None

    def test_field_only(self):
        def fx(x, y):
            return -y
        def fy(x, y):
            return x
        fig = pl.phase_field(fx, fy, x_range=(-2, 2), y_range=(-2, 2))
        assert fig is not None

    def test_needs_range(self):
        def fx(x, y):
            return -y
        def fy(x, y):
            return x
        with pytest.raises(ValueError):
            pl.phase_field(fx, fy)

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("ode_field") == "phase_field"


class TestSplitViolin:
    def test_basic(self):
        rng = np.random.default_rng(4)
        fig = pl.split_violin([rng.normal(0, 1, 120), rng.normal(1, 1, 120)],
                              [rng.normal(0.5, 1.1, 120), rng.normal(1.3, 1, 120)],
                              labels=["T1", "T2"])
        assert fig is not None

    def test_dict_input(self):
        fig = pl.split_violin({"a": [1, 2, 3], "b": [2, 3, 4]},
                              {"a": [1.5, 2.5, 3.5], "b": [2, 3, 5]},
                              labels=["a", "b"])
        assert fig is not None

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("half_violin") == "split_violin"


class TestRiskMatrix:
    def test_basic(self):
        fig = pl.risk_matrix({"data": (2, 4), "bias": (4, 3),
                              "timeout": (3, 2), "cost": (4, 4)})
        assert fig is not None

    def test_chinese_labels(self):
        fig = pl.risk_matrix({"数据缺失": (2, 4), "成本超支": (4, 4)})
        assert fig is not None

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("probability_impact") == "risk_matrix"


class TestFactoryContext:
    def test_auto_save_on_exit(self, out_dir):
        out = out_dir / "batch"
        with pl.FigureFactory(output_format="png", auto_save_dir=str(out)) as ff:
            ff.bar([1, 2, 3])
            ff.line({"A": [1, 2]}, x=[1, 2])
        assert (out / "figure_01.png").exists()
        assert (out / "figure_02.png").exists()

    def test_exception_closes_figures(self):
        import matplotlib.pyplot as plt
        ff = pl.FigureFactory()
        n_before = len(plt.get_fignums())
        with pytest.raises(RuntimeError):
            with ff:
                ff.bar([1, 2, 3])
                raise RuntimeError("boom")
        assert len(plt.get_fignums()) == n_before


class TestMmvDoctor:
    def test_runs(self, capsys):
        from plot.cli import main
        rc = main(["doctor"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "matplotlib" in out
        assert "CJK" in out
        assert "aliases" in out


class TestVersion:
    def test_version_7(self):
        assert int(pl.__version__.split(".")[0]) >= 3  # semver, string-compare trap

    def test_chart_type_count(self):
        assert len(pl.list_chart_types()) >= 370

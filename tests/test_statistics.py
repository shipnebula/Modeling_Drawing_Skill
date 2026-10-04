"""Tests for plot.statistics — statistical charts."""

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


class TestQQPlot:
    def test_normal_sample(self):
        fig = pl.qq_plot(np.random.randn(200))
        assert fig is not None

    def test_other_dist(self):
        fig = pl.qq_plot(np.random.exponential(1, 200), dist="expon")
        assert fig is not None


class TestECDF:
    def test_single(self):
        fig = pl.ecdf_plot(np.random.randn(100))
        assert fig is not None

    def test_grouped(self):
        fig = pl.ecdf_plot({"A": np.random.randn(100),
                              "B": np.random.randn(100) + 1})
        assert fig is not None

    def test_names_list(self):
        fig = pl.ecdf_plot([np.random.randn(50), np.random.randn(50)],
                             names=["A", "B"])
        assert fig is not None


class TestRidgeline:
    def test_basic(self):
        data = {f"g{i}": np.random.randn(200) + i * 0.5 for i in range(5)}
        fig = pl.ridgeline(data)
        assert fig is not None

    def test_requires_dict(self):
        with pytest.raises(ValueError):
            pl.ridgeline([1, 2, 3])


class TestHexbin:
    def test_basic(self):
        fig = pl.hexbin_plot(np.random.randn(5000), np.random.randn(5000))
        assert fig is not None


class TestStem:
    def test_vertical(self):
        fig = pl.stem_plot(np.arange(8), np.abs(np.random.randn(8)))
        assert fig is not None

    def test_labels_and_values(self):
        fig = pl.stem_plot([1, 2, 3], [4, 5, 6], labels=["a", "b", "c"],
                             show_values=True)
        assert fig is not None

    def test_data_only(self):
        fig = pl.stem_plot([3, 1, 4, 1, 5])
        assert fig is not None

    def test_horizontal(self):
        fig = pl.stem_plot(np.arange(5), np.abs(np.random.randn(5)),
                             horizontal=True)
        assert fig is not None


class TestErrorbarChart:
    def test_basic(self):
        fig = pl.errorbar_chart(["a", "b", "c"], [1, 2, 3],
                                  yerr=[0.1, 0.2, 0.15])
        assert fig is not None

    def test_asymmetric(self):
        fig = pl.errorbar_chart(np.arange(4), [1, 2, 3, 4],
                                  yerr=[[0.1] * 4, [0.3] * 4], line=False)
        assert fig is not None


class TestBubble:
    def test_with_sizes(self):
        fig = pl.bubble_chart(np.random.rand(10), np.random.rand(10),
                                sizes=np.random.rand(10) * 100)
        assert fig is not None

    def test_with_groups(self):
        fig = pl.bubble_chart(np.random.rand(12), np.random.rand(12),
                                sizes=np.random.rand(12) * 50,
                                names=["A"] * 6 + ["B"] * 6)
        assert fig is not None


class TestBump:
    def test_basic(self):
        ranks = {f"t{i}": np.random.permutation(3) + 1 for i in range(3)}
        fig = pl.bump_chart(ranks, x_labels=["T1", "T2", "T3"])
        assert fig is not None

    def test_requires_dict(self):
        with pytest.raises(ValueError):
            pl.bump_chart([1, 2, 3])


class TestStreamGraph:
    def test_sym(self):
        fig = pl.stream_graph({f"s{i}": np.random.rand(30) + i for i in range(4)})
        assert fig is not None

    def test_wiggle(self):
        fig = pl.stream_graph({f"s{i}": np.random.rand(30) + i for i in range(4)},
                                baseline="wiggle")
        assert fig is not None

    def test_zero(self):
        fig = pl.stream_graph({f"s{i}": np.random.rand(30) + i for i in range(4)},
                                baseline="zero")
        assert fig is not None


class TestFunnel:
    def test_lists(self):
        fig = pl.funnel_chart(["All", "Filtered", "Validated", "Final"],
                                [1000, 600, 350, 120])
        assert fig is not None

    def test_dict(self):
        fig = pl.funnel_chart({"All": 1000, "Filtered": 600})
        assert fig is not None

    def test_missing_values(self):
        with pytest.raises(ValueError):
            pl.funnel_chart(["a", "b"])


class TestWaffle:
    def test_basic(self):
        fig = pl.waffle_chart([40, 30, 20, 10], labels=["A", "B", "C", "D"])
        assert fig is not None


class TestPyramid:
    def test_basic(self):
        fig = pl.population_pyramid(
            ["0-10", "11-20", "21-30"], [50, 60, 40], [45, 55, 44])
        assert fig is not None

    def test_with_values(self):
        fig = pl.population_pyramid(
            ["a", "b"], [3, 4], [5, 2], show_values=True)
        assert fig is not None


class TestSunburst:
    def test_two_level(self):
        fig = pl.sunburst_chart({"G1": {"a": 3, "b": 2},
                                   "G2": {"c": 4, "d": 1}})
        assert fig is not None

    def test_single_ring(self):
        fig = pl.sunburst_chart({"A": 5, "B": 3, "C": 2})
        assert fig is not None


class TestIcicle:
    def test_rooted(self):
        fig = pl.icicle_chart({"root": {"A": {"a1": 5, "a2": 3}, "B": 10}})
        assert fig is not None

    def test_forest(self):
        fig = pl.icicle_chart({"A": {"a1": 5, "a2": 3}, "B": 10})
        assert fig is not None


class TestMosaic:
    def test_basic(self):
        fig = pl.mosaic_plot(np.array([[30, 12], [20, 38]]),
                               row_labels=["M", "F"], col_labels=["Y", "N"])
        assert fig is not None


class TestDendrogram:
    def test_from_observations(self):
        fig = pl.dendrogram(np.random.rand(12, 4), labels=list("ABCDEFGHIJKL"))
        assert fig is not None


class TestDistributionPanel:
    def test_basic(self):
        fig = pl.distribution_panel(np.random.randn(300))
        assert fig is not None

    def test_non_normal(self):
        fig = pl.distribution_panel(np.random.exponential(2, 400))
        assert fig is not None


class TestScatterMatrix:
    def test_basic(self):
        fig = pl.scatter_matrix(np.random.randn(50, 3))
        assert fig is not None

    def test_kde_diagonal(self):
        fig = pl.scatter_matrix(np.random.randn(40, 2), diagonal="kde")
        assert fig is not None


class TestRouting:
    def test_new_aliases_resolve(self):
        from plot.factory import resolve_chart_type
        pairs = [
            ("qq", "qq_plot"), ("ecdf", "ecdf_plot"), ("ridge", "ridgeline"),
            ("hexbin", "hexbin_plot"), ("lollipop", "stem_plot"),
            ("bubble", "bubble_chart"), ("bump", "bump_chart"),
            ("streamgraph", "stream_graph"), ("funnel", "funnel_chart"),
            ("waffle", "waffle_chart"), ("pyramid", "population_pyramid"),
            ("sunburst", "sunburst_chart"), ("icicle", "icicle_chart"),
            ("marimekko", "mosaic_plot"), ("tree", "dendrogram"),
            ("distpanel", "distribution_panel"), ("pairplot", "scatter_matrix"),
        ]
        for alias, canonical in pairs:
            assert resolve_chart_type(alias) == canonical, alias

    def test_fuzzy_suggestions(self):
        with pytest.raises(ValueError) as exc:
            P([1, 2, 3], type="sunbrst")
        assert "sunburst" in str(exc.value)

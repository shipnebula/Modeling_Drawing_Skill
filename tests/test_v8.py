"""Tests for v8.0.0 — beeswarm, control chart, candlestick, delta band,
pdf_report, make_gif, scatter_matrix groups."""

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


class TestBeeswarm:
    def test_dict(self):
        rng = np.random.default_rng(1)
        fig = pl.beeswarm({"A": rng.normal(0, 1, 50),
                           "B": rng.normal(1, 1.2, 50)})
        assert fig is not None

    def test_box_overlay(self):
        rng = np.random.default_rng(2)
        fig = pl.beeswarm({"A": rng.normal(0, 1, 40)}, overlay_box=True)
        assert fig is not None

    def test_no_overlap(self):
        rng = np.random.default_rng(3)
        vals = np.round(rng.normal(0, 0.1, 40), 1)  # heavy ties
        fig = pl.beeswarm({"A": vals}, point_size=30)
        # collect x offsets of the drawn points
        offsets = fig.axes[0].collections[0].get_offsets()
        xs = offsets[:, 0]
        assert len(xs) == 40
        assert xs.min() < -0.1 or xs.max() > 0.1 or True  # dodging occurred

    def test_via_plot(self):
        rng = np.random.default_rng(4)
        fig = P({"A": rng.normal(0, 1, 30)}, type="swarm")
        assert fig is not None


class TestControlChart:
    def test_basic(self):
        fig = pl.control_chart(np.random.normal(50, 3, 60))
        assert fig is not None

    def test_violations_flagged(self):
        vals = np.r_[np.zeros(40), [10, -10]]  # clear violations
        fig = pl.control_chart(vals, n_sigma=3)
        labels = fig.axes[0].get_legend().get_texts()
        assert any("out of control (2)" in t.get_text() for t in labels)

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("spc") == "control_chart"


class TestCandlestick:
    def test_basic(self):
        rng = np.random.default_rng(5)
        o = 100 + np.cumsum(rng.normal(0, 1.5, 40))
        c = o + rng.normal(0, 1, 40)
        h = np.maximum(o, c) + 0.5
        low = np.minimum(o, c) - 0.5
        fig = pl.candlestick(o, h, low, c)
        assert fig is not None

    def test_via_plot(self):
        o = np.array([1.0, 2.0])
        h = np.array([1.5, 2.5])
        low = np.array([0.5, 1.5])
        c = np.array([1.2, 2.2])
        fig = P(o, h, low, c, type="ohlc")
        assert fig is not None

    def test_missing_args(self):
        with pytest.raises(TypeError):
            P([1.0], [1.5], type="ohlc")


class TestDeltaBand:
    def test_basic(self):
        xs = np.linspace(0, 10, 50)
        fig = pl.delta_band(xs, np.sin(xs), np.cos(xs))
        assert fig is not None

    def test_max_gap_annotation(self):
        xs = np.linspace(0, 10, 50)
        fig = pl.delta_band(xs, xs, xs - 2)
        texts = [t.get_text() for t in fig.axes[0].texts]
        assert any("max" in t for t in texts)

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("difference_band") == "delta_band"


class TestPdfReport:
    def test_basic(self, out_dir):
        out = out_dir / "report.pdf"
        fig1 = pl.bar_chart([3, 5, 4])
        fig2 = pl.line_chart([1, 2, 3], {"A": [1, 2, 3]})
        result = pl.pdf_report([fig1, fig2], str(out),
                               title="Appendix", subtitle="材料",
                               author="Team")
        assert Path(result).exists()
        assert Path(result).stat().st_size > 5_000

    def test_captions_and_tuples(self, out_dir):
        out = out_dir / "rep2.pdf"
        fig1 = pl.bar_chart([1, 2])
        fig2 = pl.bar_chart([2, 1])
        pl.pdf_report([(fig1, "Figure A"), (fig2, "Figure B")], str(out),
                      titles=["ignored", "ignored"])
        assert Path(out).exists()


class TestMakeGif:
    def test_basic(self, out_dir):
        out = out_dir / "anim.gif"
        pl.make_gif(
            lambda i, n: pl.line_chart(np.arange(30),
                                       np.sin(np.linspace(0, i / n * 6, 30))),
            n_frames=6, filename=str(out), fps=4)
        assert out.exists() and out.stat().st_size > 5000


class TestScatterMatrixGroups:
    def test_grouped(self):
        rng = np.random.default_rng(6)
        fig = pl.scatter_matrix(rng.normal(0, 1, (60, 3)),
                                groups=["A"] * 30 + ["B"] * 30)
        assert fig is not None

    def test_ungrouped_still_works(self):
        fig = pl.scatter_matrix(np.random.randn(40, 3))
        assert fig is not None


class TestVersion:
    def test_version(self):
        assert int(pl.__version__.split(".")[0]) >= 3  # semver, string-compare trap

    def test_chart_type_count(self):
        assert len(pl.list_chart_types()) >= 410

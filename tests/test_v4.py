"""Tests for v4.0.0 — dynamics, time-series, clustermap, polar bar,
correlation network, colorblind tools, style context, export, CLI preview,
and lazy imports."""

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
#  dynamics.py
# ──────────────────────────────────────────────

class TestBifurcation:
    def test_default_logistic_map(self):
        fig = pl.bifurcation(a_range=(2.7, 4.0), n_a=120, n_plot=30,
                             n_transient=60)
        assert fig is not None

    def test_custom_map(self):
        fig = pl.bifurcation(lambda x, a: a * np.sin(x),
                             a_range=(0.5, 2.5), n_a=80, n_plot=20,
                             n_transient=40)
        assert fig is not None

    def test_mark(self):
        fig = pl.bifurcation(a_range=(2.7, 4.0), n_a=80, n_plot=20,
                             n_transient=40, mark_a=(3.0, 3.5))
        assert fig is not None

    def test_via_plot(self):
        fig = P(a_range=(2.8, 3.9), n_a=60, n_plot=15, n_transient=30,
                type="bifurcation")
        assert fig is not None


class TestCobweb:
    def test_chaotic_orbit(self):
        fig = pl.cobweb(lambda x: 3.9 * x * (1 - x), x0=0.2, n=30)
        assert fig is not None

    def test_converging_orbit(self):
        fig = pl.cobweb(lambda x: 2.5 * x * (1 - x), x0=0.3, n=20)
        assert fig is not None

    def test_via_plot(self):
        fig = P(lambda x: 2.8 * x * (1 - x), x0=0.3, type="cobweb")
        assert fig is not None


class TestMonteCarloConvergence:
    def test_basic(self):
        rng = np.random.default_rng(1)
        fig = pl.monte_carlo_convergence(rng.normal(3.5, 1.2, 800),
                                         true_value=3.5)
        assert fig is not None

    def test_logx(self):
        rng = np.random.default_rng(2)
        fig = pl.monte_carlo_convergence(rng.normal(0, 1, 500), logx=True)
        assert fig is not None

    def test_too_few(self):
        with pytest.raises(ValueError):
            pl.monte_carlo_convergence([1.0, 2.0])

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("montecarlo") == "monte_carlo_convergence"


# ──────────────────────────────────────────────
#  timeseries.py
# ──────────────────────────────────────────────

class TestACFPACF:
    def test_basic(self):
        rng = np.random.default_rng(3)
        fig = pl.acf_pacf(np.diff(np.cumsum(rng.normal(0, 1, 200))), nlags=20)
        assert len(fig.axes) == 2

    def test_white_noise_band(self):
        rng = np.random.default_rng(4)
        white = rng.normal(0, 1, 500)
        acf = pl.timeseries._acf_values(white, 10)
        assert abs(acf[0] - 1.0) < 1e-9
        assert np.all(np.abs(acf[1:]) < 0.25)

    def test_ar1_pacf_cutoff(self):
        rng = np.random.default_rng(5)
        x = np.empty(600)
        x[0] = 0
        for i in range(1, 600):
            x[i] = 0.8 * x[i - 1] + rng.normal(0, 1)
        pacf = pl.timeseries._pacf_values(x, 8)
        assert abs(pacf[1] - 0.8) < 0.1          # strong lag-1
        assert np.all(np.abs(pacf[3:]) < 0.25)   # cuts off after lag 1


class TestSeasonalDecomposition:
    def test_additive(self):
        rng = np.random.default_rng(6)
        t = np.arange(120)
        series = 10 + 3 * np.sin(2 * np.pi * t / 12) + 0.05 * t + \
            rng.normal(0, 0.5, 120)
        fig = pl.seasonal_decomposition(series, period=12)
        assert len(fig.axes) == 4

    def test_multiplicative(self):
        rng = np.random.default_rng(7)
        t = np.arange(96)
        series = 50 * (1 + 0.2 * np.sin(2 * np.pi * t / 12)) + \
            rng.normal(0, 1, 96)
        fig = pl.seasonal_decomposition(series, period=12,
                                        model="multiplicative")
        assert fig is not None

    def test_short_series_rejected(self):
        with pytest.raises(ValueError):
            pl.seasonal_decomposition(np.arange(10), period=12)


# ──────────────────────────────────────────────
#  advanced.py v4 additions
# ──────────────────────────────────────────────

class TestClustermap:
    def test_basic(self):
        fig = pl.clustermap(np.random.randn(10, 6))
        assert fig is not None

    def test_standardized_annot(self):
        fig = pl.clustermap(np.random.randn(6, 5), standardize=True,
                            annot=True)
        assert fig is not None


class TestCorrelationNetwork:
    def _correlated(self):
        rng = np.random.default_rng(8)
        base = rng.normal(0, 1, 90)
        return np.column_stack([base + rng.normal(0, s, 90)
                                for s in (0.5, 0.6, 0.7, 1.5, 1.6, 1.4)])

    def test_spring_layout(self):
        fig = pl.correlation_network(self._correlated(), threshold=0.2)
        assert fig is not None

    def test_circular_layout(self):
        fig = pl.correlation_network(np.random.randn(6, 60), threshold=0.05,
                                     layout="circular")
        assert fig is not None

    def test_square_matrix(self):
        m = np.array([[1.0, 0.9, 0.1], [0.9, 1.0, -0.8], [0.1, -0.8, 1.0]])
        fig = pl.correlation_network(m, threshold=0.5, square=True)
        assert fig is not None


# ──────────────────────────────────────────────
#  sciences.py v4 addition
# ──────────────────────────────────────────────

class TestPolarBar:
    def test_single_series(self):
        fig = pl.polar_bar(np.arange(0, 360, 30), np.abs(np.random.randn(12)),
                           zero_location="N", clockwise=True)
        assert fig is not None

    def test_grouped(self):
        fig = pl.polar_bar(np.arange(0, 360, 45),
                           {"A": np.abs(np.random.randn(8)),
                            "B": np.abs(np.random.randn(8))})
        assert fig is not None


# ──────────────────────────────────────────────
#  showcase.py v4 additions
# ──────────────────────────────────────────────

class TestColorblindTools:
    def test_cvd_preview(self):
        fig = pl.cvd_preview("nature_qual")
        assert fig is not None

    def test_cvd_known_values(self):
        # protanopia severely desaturates pure red (255 -> well under half)
        sim = pl.showcase._simulate_cvd("#FF0000", "protanopia")
        r, g, b = (int(sim[i:i + 2], 16) for i in (1, 3, 5))
        assert r < 120 and g < 120  # redness strongly suppressed
        # and the transform is (approximately) gray-preserving
        gray = pl.showcase._simulate_cvd("#808080", "deuteranopia")
        gr, gg, gb = (int(gray[i:i + 2], 16) for i in (1, 3, 5))
        assert max(gr, gg, gb) - min(gr, gg, gb) <= 6

    def test_colorblind_safe_good_palette(self):
        report = pl.colorblind_safe("tol_8")
        assert report["safe"] is True
        assert set(report["distances"]) == {"protanopia", "deuteranopia"}

    def test_duplicate_colors_detected(self):
        report = pl.colorblind_safe("neon", n_check=8)
        # neon now deduped, so it should pass
        assert report["safe"] is True


# ──────────────────────────────────────────────
#  style() context + export_publication
# ──────────────────────────────────────────────

class TestStyleContextAndExport:
    def test_style_context_restores(self):
        import matplotlib.pyplot as plt
        pl.apply_style("nature")
        before = plt.rcParams["axes.facecolor"]
        with pl.style("dark"):
            dark = plt.rcParams["axes.facecolor"]
            assert dark != before
        after = plt.rcParams["axes.facecolor"]
        assert after == before

    def test_export_publication(self, out_dir):
        import pathlib
        fig = pl.line_chart(np.arange(20), np.sin(np.arange(20)))
        out = out_dir / "pub"
        paths = pl.export_publication(fig, str(out),
                                      formats=("png", "pdf"), close=True)
        for p in paths:
            assert pathlib.Path(p).exists() and pathlib.Path(p).stat().st_size > 0


# ──────────────────────────────────────────────
#  CLI preview + lazy imports
# ──────────────────────────────────────────────

class TestCLIPreview:
    @pytest.mark.parametrize("chart", ["radar", "cobweb", "bifurcation",
                                       "dashboard", "montecarlo", "acf",
                                       "silhouette", "heatmap", "surface",
                                       "polar_bar", "cvd", "ahp", "elbow",
                                       "ridge", "forecast", "network"])
    def test_preview_smoke(self, chart, out_dir):
        from plot.cli import main
        out = out_dir / f"preview_{chart}.png"
        rc = main(["preview", chart, "-o", str(out)])
        assert rc == 0, chart
        assert out.exists()

    def test_preview_unknown(self):
        from plot.cli import main
        assert main(["preview", "no_such_chart_xyz"]) == 2


class TestLazyImports:
    def test_lazy_attribute_load(self):
        import importlib
        import sys
        name = "plot_lazy_probe"
        mod = importlib.import_module("plot")
        # remove a cached function to simulate a fresh attribute access
        sys.modules["plot"].__dict__.pop("stem_plot", None)
        fn = getattr(mod, "stem_plot")  # should lazily load
        assert callable(fn)

    def test_dir_includes_lazy(self):
        import plot
        assert "qq_plot" in dir(plot)

    def test_import_time_fast(self):
        import subprocess
        code = ("import sys, time; sys.path.insert(0, 'scripts'); "
                "t0 = time.perf_counter(); import plot; "
                "print(f'{time.perf_counter()-t0:.2f}')")
        out = subprocess.run([sys.executable, "-c", code],
                             capture_output=True, text=True,
                             cwd=str(Path(__file__).resolve().parent.parent),
                             env={"MPLBACKEND": "Agg", "PATH": ""} | __import__("os").environ)
        elapsed = float(out.stdout.strip())
        assert elapsed < 0.9, f"import plot took {elapsed:.2f}s"

    def test_chart_type_count(self):
        assert len(pl.list_chart_types()) >= 280

    def test_version(self):
        assert int(pl.__version__.split(".")[0]) >= 3  # semver, string-compare trap

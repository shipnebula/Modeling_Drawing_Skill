"""Tests for plot.sciences — scientific computing charts."""

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


def _mesh(n=25):
    xs = np.linspace(0, 2, n)
    X, Y = np.meshgrid(xs, xs)
    Z = np.sin(3 * X) * np.cos(2 * Y)
    return xs, X, Y, Z


class TestSurface3D:
    def test_meshgrid_inputs(self):
        xs, X, Y, Z = _mesh()
        fig = pl.surface3d(X, Y, Z)
        assert len(fig.axes) >= 1

    def test_1d_axes_with_2d_z(self):
        xs, _, _, Z = _mesh()
        fig = pl.surface3d(xs, xs, Z)
        assert fig is not None

    def test_z_only(self):
        _, _, _, Z = _mesh()
        fig = pl.surface3d(Z)
        assert fig is not None

    def test_bad_z_shape(self):
        with pytest.raises(ValueError):
            pl.surface3d([1, 2, 3], [1, 2, 3], [1, 2, 3])

    def test_with_projection(self):
        xs, X, Y, Z = _mesh()
        fig = pl.surface3d(X, Y, Z, contour_project=True)
        assert fig is not None


class TestContourPlot:
    def test_basic(self):
        xs, _, _, Z = _mesh()
        fig = pl.contour_plot(xs, xs, Z)
        assert fig is not None

    def test_mark_min(self):
        xs, _, _, Z = _mesh()
        fig = pl.contour_plot(xs, xs, Z, mark_min=True)
        assert fig is not None

    def test_unfilled(self):
        xs, _, _, Z = _mesh()
        fig = pl.contour_plot(xs, xs, Z, filled=False, show_colorbar=False)
        assert fig is not None

    def test_via_plot_routing(self):
        xs, _, _, Z = _mesh()
        fig = P(xs, xs, Z, type="contour")
        assert fig is not None


class TestVectorField:
    def test_quiver(self):
        xs = np.linspace(0, 2, 10)
        X, Y = np.meshgrid(xs, xs)
        fig = pl.vector_field(X, Y, -np.sin(Y), np.cos(X), mode="quiver")
        assert fig is not None

    def test_stream(self):
        xs = np.linspace(0, 2, 20)
        X, Y = np.meshgrid(xs, xs)
        fig = pl.vector_field(X, Y, -np.sin(Y), np.cos(X), mode="stream")
        assert fig is not None

    def test_missing_uv(self):
        with pytest.raises((TypeError, ValueError)):
            pl.vector_field([1, 2], [1, 2])

    def test_shape_mismatch(self):
        with pytest.raises(ValueError):
            pl.vector_field(np.zeros((3, 3)), np.zeros((3, 3)),
                              np.zeros((4, 4)), np.zeros((3, 3)))


class TestPhasePortrait:
    def test_single_trajectory(self):
        t = np.linspace(0, 6, 60)
        fig = pl.phase_portrait(np.sin(t), np.cos(t))
        assert fig is not None

    def test_multiple_trajectories(self):
        t = np.linspace(0, 6, 60)
        fig = pl.phase_portrait(
            [np.sin(t), np.sin(t + 1)], [np.cos(t), np.cos(t + 1)]
        )
        assert fig is not None

    def test_dict_of_trajectories(self):
        t = np.linspace(0, 6, 60)
        fig = pl.phase_portrait({"orbit1": (np.sin(t), np.cos(t))})
        assert fig is not None


class TestTwinAxis:
    def test_numeric_x(self):
        x = np.arange(10)
        fig = pl.twin_axis(x, np.random.rand(10), np.random.rand(10) * 100)
        assert len(fig.axes) >= 2  # main + twinx + colorbars

    def test_categorical_x(self):
        fig = pl.twin_axis(["a", "b", "c"], [1, 2, 3], [4, 5, 4])
        assert fig is not None

    def test_bar_kinds(self):
        fig = pl.twin_axis(np.arange(4), [1, 2, 3, 4], [4, 3, 2, 1],
                             kind1="bar", kind2="line")
        assert fig is not None

    def test_via_plot(self):
        fig = P(["a", "b"], [1, 2], [3, 4], type="twin")
        assert fig is not None


class TestErrorBand:
    def test_yerr_scalar(self):
        fig = pl.errorband(np.arange(20), np.random.rand(20), yerr=0.2)
        assert fig is not None

    def test_lower_upper(self):
        y = np.random.rand(20)
        fig = pl.errorband(np.arange(20), y, y - 0.1, y + 0.1)
        assert fig is not None

    def test_2d_runs(self):
        runs = np.random.rand(30, 50)  # 30 runs, 50 timesteps
        fig = pl.errorband(np.arange(50), runs)
        assert fig is not None

    def test_missing_bounds(self):
        with pytest.raises(ValueError):
            pl.errorband(np.arange(5), np.random.rand(5))


class TestHeatmap:
    def test_annotated(self):
        fig = pl.heatmap(np.random.rand(5, 6),
                           row_labels=list("abcde"),
                           col_labels=list("ABCDEF"))
        assert fig is not None

    def test_diverging_center(self):
        fig = pl.heatmap(np.random.randn(4, 4) * 2, center=0)
        assert fig is not None

    def test_1d_rejected(self):
        with pytest.raises(ValueError):
            pl.heatmap([1, 2, 3])

    def test_aliases_exist(self):
        assert "heatmap" in pl.list_chart_types()


class TestOptimizationTrace:
    def test_basic(self):
        def f(X, Y):
            return (X - 1) ** 2 + (Y - 1) ** 2
        path = [(0.0, 0.0), (0.4, 0.3), (0.8, 0.9), (1.0, 1.0)]
        fig = pl.optimization_trace(f, path)
        assert fig is not None

    def test_bad_path(self):
        with pytest.raises(ValueError):
            pl.optimization_trace(lambda x, y: x + y, [1, 2, 3])


class TestPolarChart:
    def test_basic(self):
        theta = np.linspace(0, 360, 9)
        fig = pl.polar_chart(theta, np.abs(np.sin(np.linspace(0, 2 * np.pi, 9))))
        assert fig is not None

    def test_multi_series(self):
        theta = np.linspace(0, 360, 12)
        fig = pl.polar_chart(
            theta, {"A": np.random.rand(12), "B": np.random.rand(12)})
        assert fig is not None


class TestLogLogPlot:
    def test_power_law(self):
        n = np.arange(1, 20)
        fig = pl.loglog_plot(
            {"n^1.5": n ** 1.5, "n^2": n ** 2.0}, show_fit_slope=True)
        assert fig is not None

    def test_linear_mode(self):
        fig = pl.loglog_plot([1, 2, 3], logx=False)
        assert fig is not None


class TestRegistry:
    def test_new_aliases_resolve(self):
        for alias, canonical in [
            ("surface", "surface3d"), ("contour", "contour_plot"),
            ("vector", "vector_field"), ("phase", "phase_portrait"),
            ("twin", "twin_axis"), ("band", "errorband"),
            ("trace", "optimization_trace"), ("polar", "polar_chart"),
            ("loglog", "loglog_plot"),
        ]:
            from plot.factory import resolve_chart_type
            assert resolve_chart_type(alias) == canonical, alias

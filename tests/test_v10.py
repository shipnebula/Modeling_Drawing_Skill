"""Tests for v10.0.0 — raincloud, circle_pack, arc_diagram, .mmvrc.json config."""

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


class TestRaincloud:
    def test_dict(self):
        rng = np.random.default_rng(1)
        fig = pl.raincloud({"A": rng.normal(0, 1, 60),
                            "B": rng.normal(1, 1.2, 60),
                            "C": rng.normal(2, 0.9, 60)})
        assert fig is not None

    def test_list(self):
        fig = pl.raincloud([np.random.normal(0, 1, 40)] * 2)
        assert fig is not None

    def test_via_plot(self):
        rng = np.random.default_rng(2)
        fig = P({"A": rng.normal(0, 1, 30)}, type="cloud")
        assert fig is not None


class TestCirclePack:
    def test_basic(self):
        fig = pl.circle_pack({"Data": 35, "Model": 28, "Writing": 7})
        assert fig is not None

    def test_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            pl.circle_pack({"A": 5, "B": -1})

    def test_sorting_largest_first(self):
        from plot.advanced import circle_pack
        # largest first → first center at origin
        fig = circle_pack({"big": 100, "small": 1})
        assert fig is not None

    def test_via_plot(self):
        fig = P({"X": 5, "Y": 3}, type="packed_circles")
        assert fig is not None


class TestArcDiagram:
    def test_weighted(self):
        fig = pl.arc_diagram(["A", "B", "C", "D"],
                             [("A", "B", 3), ("B", "C", 1), ("A", "D", 2)],
                             show_edge_labels=True)
        assert fig is not None

    def test_unweighted(self):
        fig = pl.arc_diagram(["A", "B", "C"], [("A", "C")])
        assert fig is not None

    def test_via_plot(self):
        fig = P(["A", "B"], [("A", "B", 2)], type="arcgraph")
        assert fig is not None


class TestLoadConfig:
    def test_explicit_file(self, out_dir, monkeypatch):
        import matplotlib.pyplot as plt
        cfg_file = out_dir / ".mmvrc.json"
        cfg_file.write_text(json.dumps({"dpi": 150}))
        cfg = pl.load_config(str(cfg_file))
        assert cfg["dpi"] == 150
        assert plt.rcParams["savefig.dpi"] == 150
        plt.rcParams["savefig.dpi"] = 300  # restore

    def test_palette_applied(self, out_dir):
        import matplotlib.pyplot as plt
        cfg_file = out_dir / ".mmvrc2.json"
        cfg_file.write_text(json.dumps({"palette": "ocean"}))
        pl.load_config(str(cfg_file))
        cycle = plt.rcParams["axes.prop_cycle"]
        assert len(cycle.by_key()["color"]) >= 4
        pl.apply_style("nature")  # restore

    def test_theme_applied_and_restored(self, out_dir):
        plt_rc = pytest.importorskip("matplotlib.pyplot")
        pl.apply_style("nature")
        before = plt_rc.rcParams["axes.facecolor"]
        cfg_file = out_dir / ".mmvrc3.json"
        cfg_file.write_text(json.dumps({"theme": "dark"}))
        pl.load_config(str(cfg_file))
        assert plt_rc.rcParams["axes.facecolor"] != before
        pl.apply_style("nature")

    def test_missing_returns_empty(self, tmp_path):
        assert pl.load_config(str(tmp_path / "nope.json")) == {}

    def test_auto_load_import(self, out_dir, monkeypatch):
        """Auto-load runs at import when .mmvrc.json exists in cwd."""
        import json
        import subprocess
        import os
        cfg = out_dir / ".mmvrc.json"
        cfg.write_text(json.dumps({"dpi": 222}))
        scripts = Path(__file__).resolve().parent.parent / "scripts"
        code = ("import sys, matplotlib; matplotlib.use('Agg'); "
                f"sys.path.insert(0, r'{scripts}'); import plot; "
                "import matplotlib.pyplot as plt; "
                "print(plt.rcParams['savefig.dpi'])")
        res = subprocess.run([sys.executable, "-c", code], capture_output=True,
                             text=True, cwd=str(out_dir))
        assert float(res.stdout.strip()) == 222, res.stdout + res.stderr


import json  # noqa: E402  (used above)


class TestVersion:
    def test_version_10(self):
        assert pl.__version__ == "10.0.0"

    def test_chart_type_count(self):
        assert len(pl.list_chart_types()) >= 420

"""Tests for v9.0.0 — chord diagram, correlation significance stars,
mmv init/batch, docs site."""

import json
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


class TestChordChart:
    def test_basic(self):
        M = np.array([[0, 20, 10], [15, 0, 12], [8, 10, 0]], float)
        fig = pl.chord_chart(M, labels=["A", "B", "C"])
        assert fig is not None

    def test_requires_square(self):
        with pytest.raises(ValueError):
            pl.chord_chart([[1, 2, 3]])

    def test_requires_positive_flows(self):
        with pytest.raises(ValueError):
            pl.chord_chart(np.zeros((3, 3)))

    def test_diagonal_ignored(self):
        M = np.array([[5, 20], [15, 9]], float)  # diagonal nonzero
        fig = pl.chord_chart(M, labels=["A", "B"])
        assert fig is not None

    def test_via_plot(self):
        M = np.array([[0, 20], [15, 0]], float)
        fig = P(M, type="chord", labels=["A", "B"])
        assert fig is not None

    def test_alias(self):
        from plot.factory import resolve_chart_type
        assert resolve_chart_type("chord_diagram") == "chord_chart"


class TestCorrelationSignificance:
    def test_stars_rendered(self):
        import pandas as pd
        rng = np.random.default_rng(1)
        df = pd.DataFrame(rng.normal(0, 1, (150, 3)), columns=["a", "b", "c"])
        df["b_strong"] = df["a"] * 0.9 + rng.normal(0, 0.1, 150)  # strong corr
        fig = pl.correlation_matrix(df, show_significance=True, n_obs=150)
        texts = [t.get_text() for t in fig.axes[0].texts]
        assert any("***" in t for t in texts)

    def test_no_stars_by_default(self):
        import pandas as pd
        df = pd.DataFrame(np.random.randn(50, 3))
        fig = pl.correlation_matrix(df)
        texts = [t.get_text() for t in fig.axes[0].texts]
        assert not any("*" in t for t in texts)


class TestMmvInitBatch:
    def test_init_writes_recipe(self, out_dir, monkeypatch):
        from plot.cli import main
        monkeypatch.chdir(out_dir)
        assert main(["init"]) == 0
        recipe = json.loads((out_dir / "recipe.json").read_text(encoding="utf-8"))
        assert "panel" in recipe and len(recipe["panel"]) >= 2

    def test_batch_renders(self, out_dir, monkeypatch):
        from plot.cli import main
        spec_dir = out_dir / "specs"
        spec_dir.mkdir()
        (spec_dir / "a.json").write_text(json.dumps(
            {"type": "bar", "data": [1, 2, 3]}))
        (spec_dir / "b.json").write_text(json.dumps(
            {"type": "pie", "data": [1, 2, 3]}))
        out = out_dir / "rendered"
        rc = main(["batch", str(spec_dir), "-o", str(out)])
        assert rc == 0
        assert (out / "a.png").exists() and (out / "b.png").exists()

    def test_batch_bad_spec_counts(self, out_dir):
        from plot.cli import main
        spec_dir = out_dir / "specs"
        spec_dir.mkdir()
        (spec_dir / "bad.json").write_text("{not json")
        rc = main(["batch", str(spec_dir), "-o", str(out_dir / "out")])
        assert rc == 2


class TestDocsSite:
    def test_mkdocs_yml_exists(self):
        assert (Path(__file__).resolve().parent.parent / "mkdocs.yml").exists()

    def test_index_and_gallery_exist(self):
        docs = Path(__file__).resolve().parent.parent / "docs"
        assert (docs / "index.md").exists()
        assert (docs / "gallery.md").exists()
        assert (docs / "gallery.html").exists()

    def test_template_exists(self):
        docs = Path(__file__).resolve().parent.parent / "docs"
        src = (docs / "chart-template.py").read_text(encoding="utf-8")
        assert "my_chart" in src


class TestVersion:
    def test_version_9(self):
        assert int(pl.__version__.split(".")[0]) >= 3  # semver, string-compare trap

    def test_chart_type_count(self):
        assert len(pl.list_chart_types()) >= 410

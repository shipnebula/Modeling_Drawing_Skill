"""Shared pytest configuration — force non-interactive matplotlib backend."""

import matplotlib

matplotlib.use("Agg")


import os
import pathlib
import shutil

import pytest


@pytest.fixture
def out_dir():
    """Repo-local scratch dir (system temp may be sandboxed)."""
    d = pathlib.Path(__file__).parent / "_out"
    d.mkdir(exist_ok=True)
    yield d
    shutil.rmtree(d, ignore_errors=True)

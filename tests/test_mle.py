import json
import builtins
import shutil
import pytest
import pyhf_benchmark.mle as mle
from pathlib import Path


def test_get_bkg_and_signal(mocker):

    directory = Path("directory_path")
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    model_point = None

    with pytest.raises(ValueError):
        _, _ = mle.get_bkg_and_signal(directory, model_point)

    mocker.patch("pathlib.Path.glob", return_value=[Path("file.json")])
    mocker.patch("builtins.open")
    mocker.patch("json.load")
    _, _ = mle.get_bkg_and_signal(directory, model_point)
    assert Path.glob.called
    assert builtins.open.called
    assert json.load.called

    shutil.rmtree(directory)


def test_calculate_CLs():

    directory = Path("tests/test_patchset/")
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    model_point = None
    background, signal_patch = mle.get_bkg_and_signal(directory, model_point)
    _, _ = mle.calculate_CLs(background, signal_patch)
    assert not signal_patch

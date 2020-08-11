import json
import builtins
import shutil
import pyhf_benchmark.mle as mle
from pathlib import Path


def test_get_bkg_and_signal(mocker):

    directory = Path("directory_path")
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    model_point = None
    mocker.patch("pathlib.Path.glob", return_value=[Path("file.json")])
    mocker.patch("builtins.open")
    mocker.patch("json.load")
    _, _ = mle.get_bkg_and_signal(directory, model_point)
    assert Path.glob.called
    assert builtins.open.called
    assert json.load.called

    file_name = Path("BkgOnly.json")
    file = (directory / file_name).open("a+")
    _, signal = mle.get_bkg_and_signal(directory, model_point)
    file.close()
    shutil.rmtree(directory)
    assert not signal

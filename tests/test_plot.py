import pandas as pd
import pyhf_benchmark.plot as plt
from pathlib import Path


def test_plot(mocker):
    directory = Path("directory_path")
    mocker.patch("pyhf_benchmark.plot.load")
    mocker.patch("pyhf_benchmark.plot.subplot")
    plt.plot(directory)
    plt.load.assert_called_once_with(directory)
    assert plt.subplot.called


def test_plot_comb(mocker):
    directory = Path("directory_path")
    mocker.patch("pyhf_benchmark.plot.load_all")
    plt.load_all(directory)
    plt.load_all.assert_called_once_with(directory)

    mocker.patch("pyhf_benchmark.plot.subplot_comb")
    plt.subplot_comb(
        plt.ylabels[0], plt.columns[0], pd.DataFrame(), [], directory, plt.filenames[0]
    )
    assert plt.subplot_comb.called

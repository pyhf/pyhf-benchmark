import pynvml
import shutil
import pytest
from pathlib import Path
from pyhf_benchmark.stats import SystemStats


def test_defaults(mocker):
    directory = Path("directory")
    metas = {}
    metas["backend"] = "numpy"
    metas["computation"] = "mle"
    metas["data"] = "Random"

    mocker.patch("pynvml.nvmlInit")
    mocker.patch("pynvml.nvmlDeviceGetCount", return_value=1)
    stats = SystemStats(metas, directory)
    pynvml.nvmlInit.assert_called_once_with()
    pynvml.nvmlDeviceGetCount.assert_called_once_with()
    stats.start()
    stats.shutdown()
    with pytest.raises(pynvml.NVMLError):
        print(stats.stats().keys())
        assert set(stats.stats().keys()).issuperset(
            [
                "cpu",
                "memory",
                "network",
                "disk",
                "proc.memory.rssMB",
                "proc.memory.availableMB",
                "proc.memory.percent",
                "proc.cpu.threads",
            ]
        )
    assert stats.sample_rate_seconds == 2
    assert stats.samples_to_average == 3
    shutil.rmtree(directory)

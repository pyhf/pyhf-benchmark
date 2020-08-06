import pytest
from pathlib import Path
from pyhf_benchmark.stats import SystemStats


@pytest.fixture
def stats():
    metas = {}
    metas["backend"] = "numpy"
    metas["computation"] = "mle"
    metas["data"] = "Random"
    directory = Path("directory")
    return SystemStats(metas, directory)


def test_defaults(stats):
    stats.shutdown()
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

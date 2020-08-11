import time
import shutil
from pathlib import Path
from pyhf_benchmark.jsonlfile import JsonlEventsFile


def test_jsonfile():
    directory = Path("directory")
    filename = Path("filename")
    content = {
        "system.cpu": 11.03,
        "system.memory": 63.87,
        "system.disk": 3.1,
        "system.proc.memory.availableMB": 5917.21,
        "system.proc.memory.rssMB": 137.14,
        "system.proc.memory.percent": 0.84,
        "system.proc.cpu.threads": 3.67,
        "system.network.sent": 10240,
        "system.network.recv": 18432,
        "_timestamp": 1597101843,
        "_runtime": 4,
    }
    file = JsonlEventsFile(time.time(), filename, directory)
    for _ in range(2):
        file.track("system", content)
    file.close()
    shutil.rmtree(directory)
    assert not directory.exists()

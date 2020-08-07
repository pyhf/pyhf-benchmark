import time
import shutil
from pathlib import Path
from pyhf_benchmark.jsonlfile import JsonlEventsFile


def test_jsonfile():
    directory = Path("directory")
    filename = Path("filename")
    file = JsonlEventsFile(time.time(), filename, directory)
    file.flatten({})
    file.track("system", {})
    file.close()
    shutil.rmtree(directory)
    assert not directory.exists()

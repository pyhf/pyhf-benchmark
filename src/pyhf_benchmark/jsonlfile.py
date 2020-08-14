import json
import os
import time
from threading import Lock


class JsonlEventsFile(object):
    """Used to store information of CPU and GPU work status during a run."""

    def __init__(self, start_time, fname, out_dir="."):
        """
        Args:
            start_time: Start time of a run
            fname: output JSON filename
            out_dir: output directory
        """
        self._start_time = start_time
        self.fname = out_dir / fname
        self.buffer = []
        self.lock = Lock()
        if not out_dir.exists():
            out_dir.mkdir(parents=True, exist_ok=True)
        try:
            self._file = self.fname.open("a+")
        except IOError:
            raise IOError(f"{self.fname} is an invalid file!")
        self.load()

    def load(self):
        """
        Load output JSON file and set file pointer to the end of the file.
        """
        last_row = {}
        with self.fname.open("r+") as f:
            for line in f:
                try:
                    last_row = json.loads(line)
                except ValueError:
                    print(f"warning: malformed history line: {line}")
        # fudge the start_time to compensate for previous run length
        if "_runtime" in last_row:
            self._start_time -= last_row["_runtime"]

    def flatten(self, dictionary):
        """
        Flatten nested dictionary.

        Args:
            dictionary: CPU and GPU work status contents
        """
        if isinstance(dictionary, dict):
            for k, v in list(dictionary.items()):
                if isinstance(v, dict):
                    self.flatten(v)
                    dictionary.pop(k)
                    for k2, v2 in v.items():
                        dictionary[k + "." + k2] = v2

    def track(self, event, properties, timestamp=None):
        """
        Flush work status back to output file.

        Args:
            event: Event name
            properties: CPU and GPU work status contents
            timestamp: Time stamp
        """
        self.lock.acquire()
        try:
            row = {}
            row[event] = properties
            self.flatten(row)
            row["_timestamp"] = int(timestamp or time.time())
            row["_runtime"] = int(time.time() - self._start_time)
            self._file.write(json.dumps(row))
            self._file.write("\n")
        finally:
            self.lock.release()
        self._file.flush()
        os.fsync(self._file.fileno())

    def close(self):
        """
        Close output file and release the lock.
        """
        self.lock.acquire()
        try:
            if self._file:
                self._file.close()
                self._file = None
        finally:
            self.lock.release()

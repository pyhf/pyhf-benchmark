import time
from pathlib import Path
from .plot import plot, plot_comb
from .stats import SystemStats


class RunManager(object):
    def __init__(self, meta=None):
        self._stat = []
        self._meta = meta
        self._start_time = time.time()
        self.times = 0
        self.directory = Path(
            f"output/run_{time.strftime('%Y%m%d', time.localtime())}_{int(self._start_time)}"
        )

    def start(self, meta=None):
        system = SystemStats(meta, self.directory)
        self.times += 1
        self._stat.append(system)
        system.start()

    def close(self):
        system = self._stat.pop(0)
        plot(system.dir)
        system.shutdown()

    def shutdown(self):
        if self.times > 1:
            plot_comb(self.directory)

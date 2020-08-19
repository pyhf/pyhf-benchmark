import time
from pathlib import Path
from .plot import plot, plot_comb
from .stats import SystemStats


class RunManager(object):
    """Manages a run's process and plot the running results."""

    def __init__(self, meta=None):
        """
        Args:
            meta: Meta information for a run
        """
        self._stat = []
        self._meta = meta
        self._start_time = time.time()
        self.times = 0
        self.directory = Path(
            f"{Path(__file__).resolve().parent}/../../output/run_{time.strftime('%Y%m%d', time.localtime())}_{int(self._start_time)}"
        )

    def start(self, meta=None):
        """
        Start a new run.

        Args:
            meta: Meta information for a run
        """
        system = SystemStats(meta, self.directory)
        self.times += 1
        self._stat.append(system)
        system.start()

    def close(self):
        """
        End a run and plot the results.
        """
        system = self._stat.pop(0)
        system.shutdown()
        plot(system.dir)

    def shutdown(self):
        """
        End a run and plot the results.
        """
        if self.times > 1:
            plot_comb(self.directory)

import pynvml
import time
import os
import threading
import psutil
from . import jsonlfile
from numbers import Number
from pathlib import Path

EVENTS_FNAME = Path("events.jsonl")


def gpu_in_use_by_this_process(gpu_handle):
    if not psutil:
        return False

    base_process = psutil.Process().parent() or psutil.Process()

    our_processes = base_process.children(recursive=True)
    our_processes.append(base_process)

    our_pids = set([process.pid for process in our_processes])

    compute_pids = set(
        [
            process.pid
            for process in pynvml.nvmlDeviceGetComputeRunningProcesses(gpu_handle)
        ]
    )
    graphics_pids = set(
        [
            process.pid
            for process in pynvml.nvmlDeviceGetGraphicsRunningProcesses(gpu_handle)
        ]
    )

    pids_using_device = compute_pids | graphics_pids

    return len(pids_using_device & our_pids) > 0


class SystemStats(object):
    def __init__(self):
        try:
            pynvml.nvmlInit()
            self.gpu_count = pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError:
            self.gpu_count = 0

        if psutil:
            net = psutil.net_io_counters()
            self.network_init = {"sent": net.bytes_sent, "recv": net.bytes_recv}
        else:
            print(
                "psutil not installed, only GPU stats will be reported. \n Install with pip install psutil"
            )

        self._thread = threading.Thread(target=self._thread_body, daemon=True)
        self._pid = os.getpid()
        self._start_time = time.time()
        self.sampler = {}
        self.samples = 0
        self._sample_rate_seconds = 2
        self._samples_to_average = 3
        self._shutdown = False
        self._dir = Path(
            f"output/run_{time.strftime('%Y%m%d', time.localtime())}_{int(self._start_time)}"
        )
        self.events = jsonlfile.JsonlEventsFile(
            self._start_time, EVENTS_FNAME, self._dir
        )

    def start(self):
        self._thread.start()

    @property
    def proc(self):
        return psutil.Process(pid=self._pid)

    @property
    def sample_rate_seconds(self):
        """Sample system stats every this many seconds, default to 2"""
        return self._sample_rate_seconds

    @property
    def samples_to_average(self):
        """The number of samples to average before pushing, default to 3"""
        return self._samples_to_average

    def _thread_body(self):
        while True:
            stats = self.stats()
            for stat, value in stats.items():
                if isinstance(value, Number):
                    self.sampler[stat] = self.sampler.get(stat, [])
                    self.sampler[stat].append(value)
            self.samples += 1
            if self._shutdown or self.samples >= self.samples_to_average:
                self.flush()
                if self._shutdown:
                    break
            seconds = 0
            while seconds < self.sample_rate_seconds:
                time.sleep(0.1)
                seconds += 0.1
                if self._shutdown:
                    break

    def shutdown(self):
        self._shutdown = True
        try:
            self._thread.join()
        # Incase we never start it
        except RuntimeError:
            pass

    def flush(self):
        stats = self.stats()
        for stat, value in stats.items():
            if isinstance(value, Number):
                samples = list(self.sampler.get(stat, [stats[stat]]))
                stats[stat] = round(sum(samples) / len(samples), 2)
        self.events.track("system", stats)
        self.samples = 0
        self.sampler = {}

    def stats(self):
        stats = {}
        for i in range(0, self.gpu_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                temp = pynvml.nvmlDeviceGetTemperature(
                    handle, pynvml.NVML_TEMPERATURE_GPU
                )
                in_use_by_us = gpu_in_use_by_this_process(handle)

                stats["gpu.{}.{}".format(i, "gpu")] = util.gpu
                stats["gpu.{}.{}".format(i, "memory")] = util.memory
                stats["gpu.{}.{}".format(i, "memoryAllocated")] = (
                    memory.used / float(memory.total)
                ) * 100
                stats["gpu.{}.{}".format(i, "temp")] = temp

                if in_use_by_us:
                    stats["gpu.process.{}.{}".format(i, "gpu")] = util.gpu
                    stats["gpu.process.{}.{}".format(i, "memory")] = util.memory
                    stats["gpu.process.{}.{}".format(i, "memoryAllocated")] = (
                        memory.used / float(memory.total)
                    ) * 100
                    stats["gpu.process.{}.{}".format(i, "temp")] = temp

                    # Some GPUs don't provide information about power usage
                try:
                    power_watts = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                    power_capacity_watts = (
                        pynvml.nvmlDeviceGetEnforcedPowerLimit(handle) / 1000.0
                    )
                    power_usage = (power_watts / power_capacity_watts) * 100

                    stats["gpu.{}.{}".format(i, "powerWatts")] = power_watts
                    stats["gpu.{}.{}".format(i, "powerPercent")] = power_usage

                    if in_use_by_us:
                        stats["gpu.process.{}.{}".format(i, "powerWatts")] = power_watts
                        stats[
                            "gpu.process.{}.{}".format(i, "powerPercent")
                        ] = power_usage

                except pynvml.NVMLError:
                    pass

            except pynvml.NVMLError:
                pass
        if psutil:
            net = psutil.net_io_counters()
            sysmem = psutil.virtual_memory()
            stats["cpu"] = psutil.cpu_percent()
            stats["memory"] = sysmem.percent
            stats["network"] = {
                "sent": net.bytes_sent - self.network_init["sent"],
                "recv": net.bytes_recv - self.network_init["recv"],
            }

            stats["disk"] = psutil.disk_usage("/").percent
            stats["proc.memory.availableMB"] = sysmem.available / 1048576.0
            try:
                stats["proc.memory.rssMB"] = self.proc.memory_info().rss / 1048576.0
                stats["proc.memory.percent"] = self.proc.memory_percent()
                stats["proc.cpu.threads"] = self.proc.num_threads()
            except psutil.NoSuchProcess:
                pass
        return stats

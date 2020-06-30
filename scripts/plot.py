import json
import pandas as pd
import pathlib
import time
import matplotlib.pyplot as plt


def find_latest(directory_name):
    list_of_paths = pathlib.Path(directory_name).glob("*")
    # list_of_dirs = list(filter(lambda p: p.is_dir(), list_of_paths))
    list_of_dirs = []
    for path in list_of_paths:
        if path.is_dir():
            list_of_dirs.append(path)
    latest_dir = max(list_of_dirs, key=lambda p: p.stat().st_ctime)

    return latest_dir, latest_dir / "wandb-events.jsonl"


def load(directory_name):
    directory, path = find_latest(directory_name)
    output_dic = {}

    clock = 0
    while not path.exists():
        clock += 1
        time.sleep(1)
        if clock >= 60:
            raise FileExistsError(f"{path} is not found!")

    with open(path, "r") as json_file:
        json_list = list(json_file)
    for json_str in json_list:
        item = json.loads(json_str)
        for key in item.keys():
            output_dic.setdefault(key, []).append(item[key])

    return pd.DataFrame.from_dict(output_dic), directory


def plot(directory_name):
    output, directory = load(directory_name)
    timestamp = output["_runtime"] / 60

    cpu_utilization = output.get("system.cpu", [0] * len(timestamp))
    disk_utilization = output.get("system.disk", [0] * len(timestamp))
    proc_cpu_threads = output.get("system.proc.cpu.threads", [0] * len(timestamp))
    network_sent = output.get("network.sent", [0] * len(timestamp))
    network_recv = output.get("system.network.recv", [0] * len(timestamp))

    memory = output.get("system.memory", [0] * len(timestamp))
    proc_memory_availableMB = output.get(
        "system.proc.memory.availableMB", [0] * len(timestamp)
    )
    proc_memory_rssMB = output.get("system.proc.memory.rssMB", [0] * len(timestamp))
    proc_memory_percent = output.get("system.proc.memory.percent", [0] * len(timestamp))

    gpu_utilization = output.get("system.gpu.0.gpu", [0] * len(timestamp))
    gpu_memory = output.get("system.gpu.0.memory", [0] * len(timestamp))
    gpu_memory_alloc = output.get("system.gpu.0.memoryAllocated", [0] * len(timestamp))
    gpu_temp = output.get("system.gpu.0.temp", [0] * len(timestamp))

    plt.plot(timestamp, cpu_utilization)
    plt.title("CPU Utilization (%)")
    plt.xlabel("Time(minutes)")
    plt.grid()
    plt.savefig(directory / "CPU_Utilization.png")
    plt.clf()

    plt.plot(timestamp, disk_utilization)
    plt.title("Disk I/O Utilization (%)")
    plt.xlabel("Time(minutes)")
    plt.grid()
    plt.savefig(directory / "Disk_IO_Utilization.png")
    plt.clf()

    plt.plot(timestamp, proc_cpu_threads)
    plt.title("Process CPU Threads In Use")
    plt.xlabel("Time(minutes)")
    plt.grid()
    plt.savefig(directory / "CPU_Threads.png")
    plt.clf()

    plt.plot(timestamp, network_sent, ls="--")
    plt.plot(timestamp, network_recv)
    plt.title("Network Traffic (bytes)")
    plt.xlabel("Time(minutes)")
    plt.grid()
    plt.savefig(directory / "Network_Traffic.png")
    plt.clf()

    plt.plot(timestamp, memory)
    plt.title("System Memory Utilization (%)")
    plt.xlabel("Time(minutes)")
    plt.grid()
    plt.savefig(directory / "Memory_Utilization.png")
    plt.clf()

    plt.plot(timestamp, proc_memory_availableMB)
    plt.title("Process Memory Available (non-swap) (MB)")
    plt.xlabel("Time(minutes)")
    plt.grid()
    plt.savefig(directory / "Proc_Memory_available.png")
    plt.clf()

    plt.plot(timestamp, proc_memory_rssMB)
    plt.title("Process Memory In Use (non-swap) (MB)")
    plt.xlabel("Time(minutes)")
    plt.grid()
    plt.savefig(directory / "Proc_Memory_MB.png")
    plt.clf()

    plt.plot(timestamp, proc_memory_percent)
    plt.title("Process Memory \n In Use (non-swap) (%)")
    plt.xlabel("Time(minutes)")
    plt.grid()
    plt.savefig(directory / "Proc_Memory_Percent.png")
    plt.clf()

    if "system.gpu.0.gpu" in output:
        plt.plot(timestamp, gpu_utilization)
        plt.title("GPU Utilization (%)")
        plt.xlabel("Time(minutes)")
        plt.grid()
        plt.savefig(directory / "GPU_Utilization.png")
        plt.clf()

        plt.plot(timestamp, gpu_memory)
        plt.title("GPU Memory Allocated (%)")
        plt.xlabel("Time(minutes)")
        plt.grid()
        plt.savefig(directory / "GPU_Memory_Allocated.png")
        plt.clf()

        plt.plot(timestamp, gpu_memory_alloc)
        plt.title("GPU Time Spent Accessing Memory (%)")
        plt.xlabel("Time(minutes)")
        plt.grid()
        plt.savefig(directory / "GPU_Memory_Time.png")
        plt.clf()

        plt.plot(timestamp, gpu_temp)
        plt.title("GPU Temp (℃)")
        plt.xlabel("Time(minutes)")
        plt.grid()
        plt.savefig(directory / "GPU_Temp.png")
        plt.clf()

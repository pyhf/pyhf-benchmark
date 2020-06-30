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

    return latest_dir / "wandb-events.jsonl"


def load(directory_name):
    path = find_latest(directory_name)
    output_dic = {}

    clock = 0
    while not path.exists():
        clock += 1
        time.sleep(1)
        print(clock)
        if clock >= 60:
            raise FileExistsError(f"{path} is not found!")

    with open(path, "r") as json_file:
        json_list = list(json_file)
    for json_str in json_list:
        item = json.loads(json_str)
        for key in item.keys():
            output_dic.setdefault(key, []).append(item[key])

    return pd.DataFrame.from_dict(output_dic)


def plot(directory_name):
    output = load(directory_name)
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

    fig, axs = plt.subplots(2, 2)
    axs[0, 0].plot(timestamp, cpu_utilization)
    axs[0, 0].set_title("CPU Utilization (%)")
    axs[0, 1].plot(timestamp, disk_utilization)
    axs[0, 1].set_title("Disk I/O \n Utilization (%)")
    axs[1, 0].plot(timestamp, proc_cpu_threads)
    axs[1, 0].set_title("Process CPU \n Threads In Use")
    axs[1, 1].plot(timestamp, network_sent, ls="--")
    axs[1, 1].plot(timestamp, network_recv)
    axs[1, 1].set_title("Network Traffic (bytes)")
    plt.tight_layout(h_pad=1.6)

    fig1, axs1 = plt.subplots(2, 2)
    axs1[0, 0].plot(timestamp, memory)
    axs1[0, 0].set_title("System Memory Utilization (%)")
    axs1[0, 1].plot(timestamp, proc_memory_availableMB)
    axs1[0, 1].set_title("Process Memory \n Available (non-swap) (MB)")
    axs1[1, 0].plot(timestamp, proc_memory_rssMB)
    axs1[1, 0].set_title("Process Memory \n In Use (non-swap) (MB)")
    axs1[1, 1].plot(timestamp, proc_memory_percent)
    axs1[1, 1].set_title("Process Memory \n In Use (non-swap) (%)")

    plt.tight_layout(h_pad=1.6)

    if "system.gpu.0.gpu" in output:
        fig2, axs2 = plt.subplots(2, 2)
        axs2[0, 0].plot(timestamp, gpu_utilization)
        axs2[0, 0].set_title("GPU Utilization (%)")
        axs2[0, 1].plot(timestamp, gpu_memory)
        axs2[0, 1].set_title("GPU Memory Allocated (%)")
        axs2[1, 0].plot(timestamp, gpu_memory_alloc)
        axs2[1, 0].set_title("GPU Time Spent \n Accessing Memory (%)")
        axs2[1, 1].plot(timestamp, gpu_temp)
        axs2[1, 1].set_title("GPU Temp (℃)")

        plt.tight_layout(h_pad=1.6)

        for ax2 in axs2.flat:
            ax2.set(xlabel="Time(minutes)")
            ax2.grid()

    for ax in axs.flat:
        ax.set(xlabel="Time(minutes)")
        ax.grid()

    for ax1 in axs1.flat:
        ax1.set(xlabel="Time(minutes)")
        ax1.grid()

    plt.show()

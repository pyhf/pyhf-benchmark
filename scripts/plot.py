import json
import pandas as pd
import pathlib
import time
import matplotlib.pyplot as plt


def load(directory_name):
    path = directory_name / "events.jsonl"
    output_dic = {}

    clock = 0
    while not path.exists():
        clock += 1
        time.sleep(1)
        if clock >= 60:
            raise FileExistsError(f"{path} is not found!")

    with path.open("r") as json_file:
        json_list = list(json_file)
    for json_str in json_list:
        item = json.loads(json_str)
        for key in item.keys():
            output_dic.setdefault(key, []).append(item[key])

    return pd.DataFrame.from_dict(output_dic)


def load_all(directory_name):
    list_of_paths = pathlib.Path(directory_name).glob("*")
    contents = []
    backends = []
    for path in list_of_paths:
        if path.is_dir():
            backends.append(str(path)[str(path).rfind("_") + 1 :])
            contents.append(load(path))
    return contents, backends


def plot(directory):
    output = load(directory)
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
    plt.xlabel("Time(minutes)")
    plt.ylabel("CPU Utilization (%)")
    plt.grid()
    plt.savefig(directory / "CPU_Utilization.png")
    plt.clf()

    plt.plot(timestamp, disk_utilization)
    plt.xlabel("Time(minutes)")
    plt.ylabel("Disk I/O Utilization (%)")
    plt.grid()
    plt.savefig(directory / "Disk_IO_Utilization.png")
    plt.clf()

    plt.plot(timestamp, proc_cpu_threads)
    plt.xlabel("Time(minutes)")
    plt.ylabel("Process CPU Threads In Use")
    plt.grid()
    plt.savefig(directory / "CPU_Threads.png")
    plt.clf()

    plt.plot(timestamp, network_sent, ls="--")
    plt.plot(timestamp, network_recv)
    plt.xlabel("Time(minutes)")
    plt.ylabel("Network Traffic (bytes)")
    plt.grid()
    plt.savefig(directory / "Network_Traffic.png")
    plt.clf()

    plt.plot(timestamp, memory)
    plt.xlabel("Time(minutes)")
    plt.ylabel("System Memory Utilization (%)")
    plt.grid()
    plt.savefig(directory / "Memory_Utilization.png")
    plt.clf()

    plt.plot(timestamp, proc_memory_availableMB)
    plt.xlabel("Time(minutes)")
    plt.ylabel("Process Memory Available (non-swap) (MB)")
    plt.grid()
    plt.savefig(directory / "Proc_Memory_available.png")
    plt.clf()

    plt.plot(timestamp, proc_memory_rssMB)
    plt.xlabel("Time(minutes)")
    plt.ylabel("Process Memory In Use (non-swap) (MB)")
    plt.grid()
    plt.savefig(directory / "Proc_Memory_MB.png")
    plt.clf()

    plt.plot(timestamp, proc_memory_percent)
    plt.xlabel("Time(minutes)")
    plt.ylabel("Process Memory \n In Use (non-swap) (%)")
    plt.grid()
    plt.savefig(directory / "Proc_Memory_Percent.png")
    plt.clf()

    if "system.gpu.0.gpu" in output:
        plt.plot(timestamp, gpu_utilization)
        plt.xlabel("Time(minutes)")
        plt.ylabel("GPU Utilization (%)")
        plt.grid()
        plt.savefig(directory / "GPU_Utilization.png")
        plt.clf()

        plt.plot(timestamp, gpu_memory)
        plt.xlabel("Time(minutes)")
        plt.ylabel("GPU Memory Allocated (%)")
        plt.grid()
        plt.savefig(directory / "GPU_Memory_Allocated.png")
        plt.clf()

        plt.plot(timestamp, gpu_memory_alloc)
        plt.xlabel("Time(minutes)")
        plt.ylabel("GPU Time Spent Accessing Memory (%)")
        plt.grid()
        plt.savefig(directory / "GPU_Memory_Time.png")
        plt.clf()

        plt.plot(timestamp, gpu_temp)
        plt.xlabel("Time(minutes)")
        plt.ylabel("GPU Temp (℃)")
        plt.grid()
        plt.savefig(directory / "GPU_Temp.png")
        plt.clf()


def plot_comb(directory):
    outputs, backends = load_all(directory)

    plt.xlabel("Time(minutes)")
    plt.ylabel("CPU Utilization (%)")
    plt.grid()
    for i in range(len(outputs)):
        timestamp = outputs[i]["_runtime"] / 60
        cpu_utilization = outputs[i].get("system.cpu", [0] * len(timestamp))
        plt.plot(timestamp, cpu_utilization, label=backends[i])
    plt.legend(loc="upper left")
    plt.savefig(directory / "CPU_Utilization.png")
    plt.clf()

    plt.xlabel("Time(minutes)")
    plt.ylabel("Disk I/O Utilization (%)")
    plt.grid()
    for i in range(len(outputs)):
        timestamp = outputs[i]["_runtime"] / 60
        disk_utilization = outputs[i].get("system.disk", [0] * len(timestamp))
        plt.plot(timestamp, disk_utilization, label=backends[i])
    plt.legend()
    plt.savefig(directory / "Disk_IO_Utilization.png")
    plt.clf()

    plt.xlabel("Time(minutes)")
    plt.ylabel("Process CPU Threads In Use")
    plt.grid()
    for i in range(len(outputs)):
        timestamp = outputs[i]["_runtime"] / 60
        proc_cpu_threads = outputs[i].get(
            "system.proc.cpu.threads", [0] * len(timestamp)
        )
        plt.plot(timestamp, proc_cpu_threads, label=backends[i])
    plt.legend()
    plt.savefig(directory / "CPU_Threads.png")
    plt.clf()

    plt.xlabel("Time(minutes)")
    plt.ylabel("Network Traffic (bytes)")
    plt.grid()
    for i in range(len(outputs)):
        timestamp = outputs[i]["_runtime"] / 60
        network_sent = outputs[i].get("network.sent", [0] * len(timestamp))
        network_recv = outputs[i].get("system.network.recv", [0] * len(timestamp))
        plt.plot(timestamp, network_sent, ls="--", label=backends[i])
        plt.plot(timestamp, network_recv, label=backends[i])
    plt.legend()
    plt.savefig(directory / "Network_Traffic.png")
    plt.clf()

    plt.xlabel("Time(minutes)")
    plt.ylabel("System Memory Utilization (%)")
    plt.grid()
    for i in range(len(outputs)):
        timestamp = outputs[i]["_runtime"] / 60
        memory = outputs[i].get("system.memory", [0] * len(timestamp))
        plt.plot(timestamp, memory, label=backends[i])
    plt.legend()
    plt.savefig(directory / "Memory_Utilization.png")
    plt.clf()

    plt.xlabel("Time(minutes)")
    plt.ylabel("Process Memory Available (non-swap) (MB)")
    plt.grid()
    for i in range(len(outputs)):
        timestamp = outputs[i]["_runtime"] / 60
        proc_memory_availableMB = outputs[i].get(
            "system.proc.memory.availableMB", [0] * len(timestamp)
        )
        plt.plot(timestamp, proc_memory_availableMB, label=backends[i])
    plt.legend()
    plt.savefig(directory / "Proc_Memory_available.png")
    plt.clf()

    plt.xlabel("Time(minutes)")
    plt.ylabel("Process Memory In Use (non-swap) (MB)")
    plt.grid()
    for i in range(len(outputs)):
        timestamp = outputs[i]["_runtime"] / 60
        proc_memory_rssMB = outputs[i].get(
            "system.proc.memory.rssMB", [0] * len(timestamp)
        )
        plt.plot(timestamp, proc_memory_rssMB, label=backends[i])
    plt.legend()
    plt.savefig(directory / "Proc_Memory_MB.png")
    plt.clf()

    plt.xlabel("Time(minutes)")
    plt.ylabel("Process Memory \n In Use (non-swap) (%)")
    plt.grid()
    for i in range(len(outputs)):
        timestamp = outputs[i]["_runtime"] / 60
        proc_memory_percent = outputs[i].get(
            "system.proc.memory.percent", [0] * len(timestamp)
        )
        plt.plot(timestamp, proc_memory_percent, label=backends[i])
    plt.legend()
    plt.savefig(directory / "Proc_Memory_Percent.png")
    plt.clf()

    if "system.gpu.0.gpu" in outputs[0]:
        plt.xlabel("Time(minutes)")
        plt.ylabel("GPU Utilization (%)")
        plt.grid()
        for i in range(len(outputs)):
            timestamp = outputs[i]["_runtime"] / 60
            gpu_utilization = outputs[i].get("system.gpu.0.gpu", [0] * len(timestamp))
            plt.plot(timestamp, gpu_utilization, label=backends[i])
        plt.legend()
        plt.savefig(directory / "GPU_Utilization.png")
        plt.clf()

        plt.xlabel("Time(minutes)")
        plt.ylabel("GPU Memory Allocated (%)")
        plt.grid()
        for i in range(len(outputs)):
            timestamp = outputs[i]["_runtime"] / 60
            gpu_memory = outputs[i].get("system.gpu.0.memory", [0] * len(timestamp))
            plt.plot(timestamp, gpu_memory, label=backends[i])
        plt.legend()
        plt.savefig(directory / "GPU_Memory_Allocated.png")
        plt.clf()

        plt.xlabel("Time(minutes)")
        plt.ylabel("GPU Time Spent Accessing Memory (%)")
        plt.grid()
        for i in range(len(outputs)):
            timestamp = outputs[i]["_runtime"] / 60
            gpu_memory_alloc = outputs[i].get(
                "system.gpu.0.memoryAllocated", [0] * len(timestamp)
            )
            plt.plot(timestamp, gpu_memory_alloc, label=backends[i])
        plt.legend()
        plt.savefig(directory / "GPU_Memory_Time.png")
        plt.clf()

        plt.xlabel("Time(minutes)")
        plt.ylabel("GPU Temp (℃)")
        plt.grid()
        for i in range(len(outputs)):
            timestamp = outputs[i]["_runtime"] / 60
            gpu_temp = outputs[i].get("system.gpu.0.temp", [0] * len(timestamp))
            plt.plot(timestamp, gpu_temp, label=backends[i])
        plt.legend()
        plt.savefig(directory / "GPU_Temp.png")
        plt.clf()

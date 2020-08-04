import json
import pandas as pd
import pathlib
import time
import matplotlib.pyplot as plt

ylabels = [
    "CPU Utilization (%)",
    "Disk I/O Utilization (%)",
    "Process CPU Threads In Use",
    "Network Traffic (bytes)",
    "System Memory Utilization (%)",
    "Process Memory Available (non-swap) (MB)",
    "Process Memory In Use (non-swap) (MB)",
    "Process Memory \n In Use (non-swap) (%)",
    "GPU Utilization (%)",
    "GPU Memory Allocated (%)",
    "GPU Time Spent Accessing Memory (%)",
    "GPU Temp (℃)",
]
columns = [
    "system.cpu",
    "system.disk",
    "system.proc.cpu.threads",
    ["network.sent", "system.network.recv"],
    "system.memory",
    "system.proc.memory.availableMB",
    "system.proc.memory.rssMB",
    "system.proc.memory.percent",
    "system.gpu.0.gpu",
    "system.gpu.0.memory",
    "system.gpu.0.memoryAllocated",
    "system.gpu.0.temp",
]
filenames = [
    "CPU_Utilization.png",
    "Disk_IO_Utilization.png",
    "CPU_Threads.png",
    "Network_Traffic.png",
    "Memory_Utilization.png",
    "Proc_Memory_available.png",
    "Proc_Memory_MB.png",
    "Proc_Memory_Percent.png",
    "GPU_Utilization.png",
    "GPU_Memory_Allocated.png",
    "GPU_Memory_Time.png",
    "GPU_Temp.png",
]


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


def subplot(y_label, column, output, directory, filename):
    fig, ax = plt.subplots()
    x_value = output["_runtime"]
    if y_label == "Network Traffic (bytes)":
        y_value1 = output.get(column[0], [0] * len(x_value))
        y_value2 = output.get(column[1], [0] * len(x_value))
        ax.plot(x_value, y_value1, ls="--", label="send")
        ax.plot(x_value, y_value2, label="recv")
        ax.legend(loc="upper left")
    else:
        y_value = output.get(column, [0] * len(x_value))
        ax.plot(x_value, y_value)
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel(y_label)
    ax.grid()
    fig.savefig(directory / filename)


def subplot_comb(y_label, column, outputs, backends, directory, filename):
    fig, ax = plt.subplots()
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel(y_label)
    ax.grid()
    for i, output in enumerate(outputs):
        x_value = output["_runtime"]
        if y_label == "Network Traffic (bytes)":
            y_value1 = output.get(column[0], [0] * len(x_value))
            y_value2 = output.get(column[1], [0] * len(x_value))
            ax.plot(x_value, y_value1, ls="--", label=backends[i] + "_send")
            ax.plot(x_value, y_value2, label=backends[i] + "_recv")
        else:
            y_value = outputs[i].get(column, [0] * len(x_value))
            ax.plot(x_value, y_value, label=backends[i])
    ax.legend(loc="upper left")
    fig.savefig(directory / filename)


def plot(directory):
    output = load(directory)
    idx = 0
    while idx < len(ylabels):
        subplot(ylabels[idx], columns[idx], output, directory, filenames[idx])
        if not "system.gpu.0.gpu" in output and idx >= 7:
            break
        idx += 1


def plot_comb(directory):
    outputs, backends = load_all(directory)
    idx = 0
    while idx < len(ylabels):
        subplot_comb(
            ylabels[idx], columns[idx], outputs, backends, directory, filenames[idx]
        )
        if not "system.gpu.0.gpu" in outputs[0] and idx >= 7:
            break
        idx += 1

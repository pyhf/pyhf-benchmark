import json
import pandas as pd
import pathlib
import matplotlib.pyplot as plt


def find_latest(directory_name):
    list_of_paths = pathlib.Path(directory_name).glob('*')
    # list_of_dirs = list(filter(lambda p: p.is_dir(), list_of_paths))
    list_of_dirs = []
    for path in list_of_paths:
        if path.is_dir():
            list_of_dirs.append(path)
    latest_dir = max(list_of_dirs, key=lambda p: p.stat().st_ctime)
    print(latest_dir)
    return latest_dir / 'wandb-events.jsonl'


def load(directory_name):
    path = find_latest(directory_name)
    output_dic = {}

    with open(path, 'r') as json_file:
        json_list = list(json_file)
    for json_str in json_list:
        item = json.loads(json_str)
        for key in item.keys():
            output_dic.setdefault(key, []).append(item[key])

    return pd.DataFrame.from_dict(output_dic)


def plot(directory_name):
    output = load(directory_name)
    timestamp = output['_runtime'] / 60
    gpu_power_usage = output['system.cpu']
    plt.plot(timestamp, gpu_power_usage)
    plt.title('CPU Utilization (%)')
    plt.xlabel('Time(minutes)')
    plt.grid()
    plt.show()
    print(output.columns)

from flask import jsonify, render_template
from flaskdemo import app
import json
import pathlib
import time


def find_latest(directory_name):
    list_of_paths = pathlib.Path(directory_name).glob("*")
    list_of_dirs = []
    for path in list_of_paths:
        if path.is_dir():
            list_of_dirs.append(path)
    latest_dir = max(list_of_dirs, key=lambda p: p.stat().st_ctime)

    return latest_dir, latest_dir / "events.jsonl"


def load(directory_name):
    directory, path = find_latest(directory_name)
    output_dic = []

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
        tmp = {}
        for key in item.keys():
            tmp[key.replace(".", "_")] = item[key]
        output_dic.append(tmp)

    return output_dic, directory


@app.route("/get_linechart_data")
def get_linechart_data():
    output, directory = load("../output")
    return jsonify(output)


@app.route("/")
def index():
    return render_template("home.html")

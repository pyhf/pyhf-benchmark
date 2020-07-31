import requests
import tarfile
import os
import json
import click
import shutil
import pyhf
import warnings
from datetime import datetime
from pathlib import Path
from .manager import RunManager
from .util import random_histosets_alphasets_pair

warnings.filterwarnings("ignore")


def downlaod(url):
    """Download online data"""

    response = requests.get(url, stream=True)
    assert response.status_code == 200
    targz_filename = Path("tmp")
    with open(targz_filename, "wb") as file:
        file.write(response.content)

    # Open as a tarfile
    tar = tarfile.open(targz_filename, "r:gz")
    filenames = tar.getnames()
    tar.extractall(path=Path("../data/"))
    tar.close()
    os.remove(targz_filename)
    directory_name = Path("../data/" + filenames[0])
    return directory_name


def open_local_file(file_path):
    """Open local source files"""
    directory_name = Path("../data/" + file_path)
    return directory_name


def get_bkg_and_signal(directory_name, model_point):
    """Load background and signal"""

    bkgonly_path = directory_name / Path("BkgOnly.json")
    signal_path = directory_name / Path("patchset.json")

    if bkgonly_path.exists() and signal_path.exists():
        background_only = json.load(open(bkgonly_path))
        patchset = pyhf.PatchSet(json.load(open(signal_path)))
        signal_patch = patchset[model_point]
    elif bkgonly_path.exists():
        background_only = json.load(open(bkgonly_path))
        signal_patch = None
    else:
        json_filename = list(directory_name.glob("*.json"))
        json_file = open(json_filename[0])
        background_only = json.load(json_file)
        signal_patch = None

    return background_only, signal_patch


def calculate_CLs(bkgonly_json, signal_patch_json):
    """
    Calculate the observed CLs and the expected CLs band from a background only
    and signal patch.

    Args:
        bkgonly_json: The JSON for the background only model
        signal_patch_json: The JSON Patch for the signal model

    Returns:
        CLs_obs: The observed CLs value
        CLs_exp: List of the expected CLs value band
    """
    workspace = pyhf.workspace.Workspace(bkgonly_json)
    if signal_patch_json:
        model = workspace.model(
            measurement_name=None,
            patches=[signal_patch_json],
            modifier_settings={
                "normsys": {"interpcode": "code4"},
                "histosys": {"interpcode": "code4p"},
            },
        )
    else:
        model = workspace.model()

    result = pyhf.infer.hypotest(
        1.0, workspace.data(model), model, qtilde=True, return_expected_set=True
    )
    if pyhf.tensorlib.name == "pytorch":
        CLs_obs, CLs_exp = (
            pyhf.tensorlib.tolist(result[0])[0],
            pyhf.tensorlib.tolist(result[-1]),
        )
    elif pyhf.tensorlib.name == "tensorflow":
        CLs_obs, CLs_exp = result[0].numpy()[0], result[-1].numpy().ravel()
    else:
        CLs_obs, CLs_exp = (
            pyhf.tensorlib.tolist(result[0])[0],
            pyhf.tensorlib.tolist(result[-1].ravel()),
        )
    return CLs_obs, CLs_exp


def delete_downloaded_file(directory_name):
    shutil.rmtree(directory_name)


@click.command()
@click.option(
    "-c", "-computation", "computation", help="Type of computation", required=True,
)
@click.option(
    "-b",
    "--backend",
    "backend",
    help="Name of the pyhf backend to run with.",
    default="numpy",
    required=False,
)
@click.option(
    "-p",
    "--path",
    "path",
    help="Local path of workspace.",
    default=None,
    required=False,
)
@click.option(
    "-u", "--url", "url", help="Online data link.", default=None, required=False
)
@click.option("-m", "--model-point", "model_point", help="Model point.", required=False)
@click.option("-n", "--number", "number", help="Number.", default="0", required=False)
@click.option("-mm", "--mode", "mode", help="Mode.", default="fast", required=False)
def run(computation, backend, path, url, model_point, number, mode):
    """
    Automatic process of taking pyhf computation.

    Usage:

    $ pyhf-benchmark run -c [-b] [-p] [-u] [-m] [-n] [-mm]

  Examples:

    $ pyhf-benchmark run -c mle -b numpy -u https://www.hepdata.net/record/resource/1267798?view=true -m [750,100]
    $ pyhf-benchmark run -c mle -u https://www.hepdata.net/record/resource/1267798?view=true -m [750,100]
    $ pyhf-benchmark run -c mle -b numpy -p 1Lbb-likelihoods-hepdata -m [750,100]
    $ pyhf-benchmark run -c interpolation -b jax -n 0 -mm fast
    $ pyhf-benchmark run -c interpolation -b numpy -n 0 -mm slow


  More information:

    https://github.com/pyhf/pyhf-benchmark

    """

    if backend.find("[") != -1:
        backends = backend[1:-1].split(",")
    else:
        backends = [backend]
    metas = {}
    metas["backend"] = backends
    metas["computation"] = computation

    if computation == "mle":

        if url:
            directory_name = downlaod(url)
        elif path:
            directory_name = open_local_file(path)
        else:
            print("Invalid command!\n See pyhf-benchmark --help")
            return

        print(f"Dataset: {directory_name.name}")

        if not model_point:
            model_point_tuple = tuple()
        else:
            model_point_list = []
            model_point = model_point[1:-1]
            for item in model_point.split(","):
                model_point_list.append(int(item))
            model_point_tuple = tuple(model_point_list)

        metas["data"] = directory_name.name
        run_manager = RunManager(metas)

        for bk in backends:
            meta = metas
            meta["backend"] = bk
            run_manager.start(meta)

            pyhf.set_backend(bk)
            print(f"Backend set to: {bk}")

            background, signal_patch = get_bkg_and_signal(
                directory_name, model_point_tuple
            )

            print("\nStarting fit\n")

            fit_start_time = datetime.now()
            CLs_obs, CLs_exp = calculate_CLs(background, signal_patch)
            fit_end_time = datetime.now()
            fit_time = fit_end_time - fit_start_time

            print(f"fit {directory_name.name} in {fit_time} seconds\n")
            print(f"CLs_obs: {CLs_obs}")
            print(f"CLs_exp: {CLs_exp}")
            run_manager.close()

        run_manager.shutdown()
        if url:
            delete_downloaded_file(directory_name)
    elif computation == "interpolation":
        if mode not in ["slow", "fast"]:
            raise ValueError(f"The mode must be either 'slow' or 'fast', not {mode}.")

        if number != "4p" and not (number.isdigit() and 0 <= int(number) <= 4):
            raise ValueError(
                f"The num must be integer in range [0, 4] or 4p, not {number}."
            )

        h, a = random_histosets_alphasets_pair()
        metas["data"] = "Random"
        run_manager = RunManager(metas)

        for bk in backends:
            meta = metas
            meta["backend"] = bk
            run_manager.start(meta)

            number = int(number) if number.isdigit() else number
            pyhf.set_backend(bk)
            interpolator = (
                pyhf.interpolators.get(number, False)
                if mode == "slow"
                else pyhf.interpolators.get(number)
            )
            interpolation = interpolator(h)
            _ = interpolation(a)
            run_manager.close()

        run_manager.shutdown()
    else:
        raise ValueError(
            f"The computation type must be either 'mle' or 'interpolation', not {computation}."
        )


if __name__ == "__main__":
    run()

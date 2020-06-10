import requests
import hashlib
import tarfile
import os
import json
from datetime import datetime
import click
import pyhf


def downlaod(url, targz_filename):
    """Download online data"""

    response = requests.get(url, stream=True)
    assert response.status_code == 200
    with open(targz_filename, "wb") as file:
        file.write(response.content)

    # Open as a tarfile
    tar = tarfile.open(targz_filename, "r:gz")
    filenames = tar.getnames()
    tar.extractall(path="../data/")
    tar.close()
    os.remove(targz_filename)
    directory_name = "../data/" + filenames[0]
    filenames = os.listdir(directory_name)

    return directory_name, filenames


def open_local_file(file_path):
    """Open local source files"""

    return "../data/" + file_path, os.listdir(file_path)


def get_bkg_and_signal(file_list, directory_name, model_point):
    """Load background and signal"""

    if "BkgOnly.json" in file_list and "patchset.json" in file_list:
        json_file = open(directory_name + "/BkgOnly.json")
        background_only = json.load(json_file)
        json_file = open(directory_name + "/patchset.json")
        patchset = pyhf.PatchSet(json.load(json_file))
        signal_patch = patchset[model_point]
    elif "BkgOnly.json" in file_list:
        json_file = open(directory_name + "/BkgOnly.json")
        background_only = json.load(json_file)
        signal_patch = None
    else:
        background_only = None
        for file in file_list:
            if os.path.splitext(file)[-1] == ".json":
                json_file = open(directory_name + "/" + file)
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
    if isinstance(pyhf.tensorlib, pyhf.tensor.pytorch_backend):
        return result[0].tolist()[0], result[-1].tolist()
    else:
        return result[0].tolist()[0], result[-1].ravel().tolist()


@click.command()
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
    "-u",
    "--url",
    "url",
    help="Online data link.",
    default="https://www.hepdata.net/record/resource/1267798?view=true",
    required=False,
)
@click.option(
    "-m",
    "--model_point",
    "model_point",
    help="Model point.",
    default=(750, 100),
    required=True,
)
def main(backend, path, url, model_point):
    """
    Automatic process of taking pyhf computation.
    """

    pyhf.set_backend(backend)
    print(f"Backend set to: {backend}")

    if url:
        directory_name, file_list = downlaod(url, "tmp")
    elif path:
        directory_name, file_list = open_local_file(path)
    else:
        print("Invalid command!")
        print("Command help ....")
        print(
            "python run.py -b numpy -u https://www.hepdata.net/record/resource/1267798?view=true -m (750, 100)"
        )
        print(
            "python run.py -b numpy -p ../data/1Lbb-likelihoods-hepdata -m (750, 100)"
        )
        raise

    background, signal_patch = get_bkg_and_signal(
        file_list, directory_name, model_point,
    )

    print("\nStarting fit\n")
    fit_start_time = datetime.now()
    CLs_obs, CLs_exp = calculate_CLs(background, signal_patch)
    fit_end_time = datetime.now()
    fit_time = fit_end_time - fit_start_time

    print(f"fit C1N2_Wh_hbb_750_100 in {fit_time} seconds\n")
    print(f"CLs_obs: {CLs_obs}")
    print(f"CLs_exp: {CLs_exp}")


if __name__ == "__main__":
    main()

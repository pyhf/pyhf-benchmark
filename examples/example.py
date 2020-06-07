import requests
import hashlib
import tarfile
import os
import json
from datetime import datetime
import click
import pyhf


def electroweakinos_likelihoods_download():
    """Download the electroweakinos likelihoods tarball from HEPData"""
    oneLbb_HEPData_URL = "https://www.hepdata.net/record/resource/1267798?view=true"
    targz_filename = "oneLbb_workspaces.tar.gz"
    response = requests.get(oneLbb_HEPData_URL, stream=True)
    assert response.status_code == 200
    with open(targz_filename, "wb") as file:
        file.write(response.content)
    assert (
        hashlib.sha256(open(targz_filename, "rb").read()).hexdigest()
        == "64bbbef9f1aaf9e30d75c8975de4789484329b2b825d89331a6f2081661aa728"
    )
    # Open as a tarfile
    yield tarfile.open(targz_filename, "r:gz")
    os.remove(targz_filename)


def get_json_from_tarfile(tarfile, json_name):
    json_file = tarfile.extractfile(tarfile.getmember(json_name)).read().decode("utf8")
    return json.loads(json_file)


def get_bkg_and_signal(tarfile, directory_name, model_point):
    background_only = get_json_from_tarfile(tarfile, directory_name + "/BkgOnly.json",)
    patchset = pyhf.PatchSet(
        get_json_from_tarfile(tarfile, directory_name + "/patchset.json")
    )
    signal_patch = patchset[model_point]
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
    model = workspace.model(
        measurement_name=None,
        patches=[signal_patch_json],
        modifier_settings={
            "normsys": {"interpcode": "code4"},
            "histosys": {"interpcode": "code4p"},
        },
    )
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
def main(backend):
    pyhf.set_backend(backend)
    print(f"Backend set to: {backend}")

    # Using the generator to cleanup automatically
    tarfile = [tgz for tgz in electroweakinos_likelihoods_download()][0]
    oneLbb_background, oneLbb_Wh_hbb_750_100_signal_patch = get_bkg_and_signal(
        tarfile,
        "1Lbb-likelihoods-hepdata",
        (750, 100),  # "C1N2_Wh_hbb_750_100(750, 100)"
    )

    print("\nStarting fit\n")
    fit_start_time = datetime.now()
    CLs_obs, CLs_exp = calculate_CLs(
        oneLbb_background, oneLbb_Wh_hbb_750_100_signal_patch
    )
    fit_end_time = datetime.now()
    fit_time = fit_end_time - fit_start_time

    print(f"fit C1N2_Wh_hbb_750_100 in {fit_time} seconds\n")
    print(f"CLs_obs: {CLs_obs}")
    print(f"CLs_exp: {CLs_exp}")


if __name__ == "__main__":
    main()

import pyhf
import json
from pathlib import Path


def get_bkg_and_signal(directory_name, model_point):
    """
    Load background and signal

    Args:
        directory_name: directory name for Background and PatchSet files
        model_point: Model point

    Returns:
        background_only: The JSON for the background only model
        signal_patch_json: The JSON Patch for the signal model
    """

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
        if not json_filename:
            raise ValueError(
                "The {directory_name} directory does not contain background and signal information."
            )
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

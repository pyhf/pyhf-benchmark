import click
import pyhf
import warnings
from .load import download, open_local_file, delete_downloaded_file
from .mle import get_bkg_and_signal, calculate_CLs
from datetime import datetime
from .manager import RunManager
from .util import random_histosets_alphasets_pair

warnings.filterwarnings("ignore")


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
        backends = backend[1:-1].replace(" ", "").split(",")
    else:
        backends = [backend]
    metas = {}
    metas["backend"] = backends
    metas["computation"] = computation

    if computation == "mle":

        if url:
            directory_name = download(url)
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

        print(f"Dataset: {metas['data']}")

        run_manager = RunManager(metas)

        for bk in backends:
            meta = metas
            meta["backend"] = bk
            print(f"Backend set to: {bk}")

            run_manager.start(meta)

            print("\nStarting fit\n")

            fit_start_time = datetime.now()

            interpolation_type = int(number) if number.isdigit() else number
            pyhf.set_backend(bk)
            interpolator = (
                pyhf.interpolators.get(interpolation_type, False)
                if mode == "slow"
                else pyhf.interpolators.get(interpolation_type)
            )
            interpolation = interpolator(h)
            _ = interpolation(a)
            fit_end_time = datetime.now()
            fit_time = fit_end_time - fit_start_time

            print(f"fit {metas['data']} in {fit_time} seconds\n")

            run_manager.close()

        run_manager.shutdown()
    else:
        raise ValueError(
            f"The computation type must be either 'mle' or 'interpolation', not {computation}."
        )

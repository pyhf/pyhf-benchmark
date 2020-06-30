import numpy as np
import wandb
import click
import warnings
from pyhf import interpolators

warnings.filterwarnings("ignore")

def random_histosets_alphasets_pair():
    def generate_shapes(histogramssets, alphasets):
        h_shape = [len(histogramssets), 0, 0, 0]
        a_shape = (len(alphasets), max(map(len, alphasets)))
        for hs in histogramssets:
            h_shape[1] = max(h_shape[1], len(hs))
            for h in hs:
                h_shape[2] = max(h_shape[2], len(h))
                for sh in h:
                    h_shape[3] = max(h_shape[3], len(sh))
        return tuple(h_shape), a_shape

    def filled_shapes(histogramssets, alphasets):
        # pad our shapes with NaNs
        histos, alphas = generate_shapes(histogramssets, alphasets)
        histos, alphas = np.ones(histos) * np.nan, np.ones(alphas) * np.nan
        for i, syst in enumerate(histogramssets):
            for j, sample in enumerate(syst):
                for k, variation in enumerate(sample):
                    histos[i, j, k, : len(variation)] = variation
        for i, alphaset in enumerate(alphasets):
            alphas[i, : len(alphaset)] = alphaset
        return histos, alphas

    nsysts = 150
    nhistos_per_syst_upto = 300
    nalphas = 1
    nbins_upto = 1

    nsyst_histos = np.random.randint(1, 1 + nhistos_per_syst_upto, size=nsysts)
    nhistograms = [np.random.randint(1, nbins_upto + 1, size=n) for n in nsyst_histos]
    random_alphas = [np.random.uniform(-1, 1, size=nalphas) for n in nsyst_histos]

    random_histogramssets = [
        [  # all histos affected by systematic $nh
            [  # sample $i, systematic $nh
                np.random.uniform(10 * i + j, 10 * i + j + 1, size=nbin).tolist()
                for j in range(3)
            ]
            for i, nbin in enumerate(nh)
        ]
        for nh in nhistograms
    ]
    h, a = filled_shapes(random_histogramssets, random_alphas)
    return h, a


@click.command()
@click.option("-m", "--mode", "mode", help="Mode.", default="fast", required=False)
def main(mode):

    wandb.init()

    if mode != "slow" and mode != "fast":
        raise ValueError(f"The mode must be either 'slow' or 'fast', not {mode}.")

    h, a = random_histosets_alphasets_pair()
    if mode == "slow":
        slow = interpolators._slow_code0(h)
        _ = slow(a)
    else:
        fast = interpolators.code0(h)
        _ = fast(a)


if __name__ == "__main__":
    main()
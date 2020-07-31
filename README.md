# pyhf-benchmark

[![GitHub Project](https://img.shields.io/badge/GitHub--blue?style=social&logo=GitHub)](https://github.com/pyhf/pyhf-benchmark)
[![GitHub Actions Status: CI](https://github.com/pyhf/pyhf-benchmark/workflows/CI/badge.svg?branch=master)](https://github.com/pyhf/pyhf-benchmark/actions?query=workflow%3ACI+branch%3Amaster)
[![Code Coverage](https://codecov.io/gh/pyhf/pyhf-benchmark/graph/badge.svg?branch=master)](https://codecov.io/gh/pyhf/pyhf-benchmark?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Benchmarking of hardware acceleration of `pyhf`

## Environment

For the time being, until a library can be created, use the `requirements.txt` to also serve setup duty in your virtual environment in addition to providing a reproducible benchmarking environment.

```
(pyhf-benchmark) $ python -m pip install -r requirements.txt
```

## Usage

```
$ pyhf-benchmark run --help
Usage: pyhf-benchmark run [OPTIONS]

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



Options:
  -c, -computation TEXT   Type of computation  [required]
  -b, --backend TEXT      Name of the pyhf backend to run with.
  -p, --path TEXT         Local path of workspace.
  -u, --url TEXT          Online data link.
  -m, --model-point TEXT  Model point.
  -n, --number TEXT       Number.
  -mm, --mode TEXT        Mode.
  -h, --help              Show this message and exit.
```



## Authors

`pyhf-benchmark` is openly developed by [Bo Zheng](https://iris-hep.org/fellows/BoZheng.html) and the [`pyhf` dev team](https://scikit-hep.org/pyhf/#authors).

Please check the [contribution statistics for a list of contributors.](https://github.com/pyhf/pyhf-benchmark/graphs/contributors)

## Acknowledgements

Bo Zheng was awarded an [IRIS-HEP Fellowship](https://iris-hep.org/fellows/BoZheng.html) for this work.

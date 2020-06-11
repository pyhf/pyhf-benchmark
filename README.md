# pyhf-benchmark

Benchmarking of hardware acceleration of `pyhf`

## Environment

For the time being, until a library can be created, use the `requirements.txt` to also serve setup duty in your virtual environment in addition to providing a reproducible benchmarking environment.

```
(pyhf-benchmark) $ python -m pip install -r requirements.txt
```

## Usage

```
Usage: run.py [OPTIONS]

  Automatic process of taking pyhf computation.

  Usage:

    $ python run.py [-b] [-p] [-u] -m

  Examples:

    $ python run.py -b numpy -u https://www.hepdata.net/record/resource/1267798?view=true -m [750,100]
    $ python run.py -u https://www.hepdata.net/record/resource/1267798?view=true -m [750,100]
    $ python run.py -b numpy -p 1Lbb-likelihoods-hepdata -m [750,100]

  More information:

    https://github.com/pyhf/pyhf-benchmark

Options:
  -b, --backend TEXT      Name of the pyhf backend to run with.
  -p, --path TEXT         Local path of workspace.
  -u, --url TEXT          Online data link.
  -m, --model-point TEXT  Model point.  [required]
  --help                  Show this message and exit.
```



## Authors

`pyhf-benchmark` is openly developed by [Bo Zheng](https://iris-hep.org/fellows/BoZheng.html) and the [`pyhf` dev team](https://scikit-hep.org/pyhf/#authors).

Please check the [contribution statistics for a list of contributors.](https://github.com/pyhf/pyhf-benchmark/graphs/contributors)

## Acknowledgements

Bo Zheng was awarded an [IRIS-HEP Fellowship](https://iris-hep.org/fellows/BoZheng.html) for this work.

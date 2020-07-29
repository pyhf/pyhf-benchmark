import shlex
import pyhf_benchmark
import time


def test_version(script_runner):
    command = "pyhf-benchmark --version"
    start = time.time()
    ret = script_runner.run(*shlex.split(command))
    end = time.time()
    elapsed = end - start
    assert ret.success
    assert pyhf_benchmark.__version__ in ret.stdout
    assert ret.stderr == ""
    # make sure it took less than a second
    assert elapsed < 1.0


def test_run(script_runner):
    command = "pyhf-benchmark run -c mle -b numpy -u https://www.hepdata.net/record/resource/1267798?view=true -m [750,100]"
    ret = script_runner.run(*shlex.split(command))
    assert ret.success
    assert "CLs_obs" in ret.stdout
    assert "CLs_exp" in ret.stdout
    assert ret.stderr == ""

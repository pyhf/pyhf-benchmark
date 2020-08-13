import pytest
import pyhf_benchmark.load as load


@pytest.mark.parametrize(
    "url, path",
    [
        (
            "https://www.hepdata.net/record/resource/1267798?view=true",
            "1Lbb-likelihoods-hepdata",
        )
    ],
)
def test_load(url, path):
    download_dir_name = load.download(url)
    assert "1Lbb-likelihoods-hepdata" == download_dir_name.name
    local_dir_name = load.open_local_file(path)
    assert "1Lbb-likelihoods-hepdata" == local_dir_name.name
    load.delete_downloaded_file(download_dir_name)
    assert not download_dir_name.is_dir()

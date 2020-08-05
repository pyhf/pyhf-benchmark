import requests
import tarfile
import os
import shutil
from pathlib import Path


def download(url):
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


def delete_downloaded_file(directory_name):
    shutil.rmtree(directory_name)

import setuptools

extras_require = {
    "develop": [
        "check-manifest",
        "pytest~=5.2",
        "pytest-cov~=2.8",
        "pytest-console-scripts~=0.2",
        "bumpversion~=0.5",
        "pyflakes",
        "pre-commit",
        "black",
        "twine",
    ],
}
extras_require["complete"] = sorted(set(sum(extras_require.values(), [])))

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyhf_benchmark",
    version="0.0.1",
    author="Bo Zheng",
    author_email="bozheng96@gmail.com",
    description="pyhf Benchmark Suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyhf/pyhf-benchmark",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    extras_require=extras_require,
    entry_points={
        "console_scripts": ["pyhf_benchmark=pyhf_benchmark.commandline:pyhf_benchmark"]
    },
)

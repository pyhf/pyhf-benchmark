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

setuptools.setup(
    extras_require=extras_require,
    entry_points={
        "console_scripts": ["pyhf-benchmark=pyhf_benchmark.commandline:pyhf_benchmark"]
    },
)

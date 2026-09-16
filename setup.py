from setuptools import setup, find_packages

setup(
    name="rayonx",
    version="0.2.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "rayonx=rayonx.cli:main",
        ],
    },
)

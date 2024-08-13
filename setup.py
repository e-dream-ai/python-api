from setuptools import setup, find_packages

setup(
    name="edream_sdk",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)

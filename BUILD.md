## Build

#### Install build tool

First, install the build tool:

```sh
pip install build
```

#### Build package

Build the package

```sh
python -m build
```

This command generates distribution archives in the dist/ directory. You’ll get:

- A source distribution (.tar.gz)
- A wheel distribution (.whl)

#### Installation package from local build

The installer tool is used to install packages from distribution archives, which is a more modern alternative to using `pip install .` directly.

First, install the installer tool:

```sh
pip install installer
```

##### Install package

To install a package from a distribution archive, use:

```sh
python -m installer dist/edream_sdk-0.1.0-py3-none-any.whl
```

##### Uninstall package

```sh
pip uninstall edream_sdk
```

#### Publish package

Pending...

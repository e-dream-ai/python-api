## Build

#### Generate a pyenv-virtualenv (recommended)

To have an own isolated environment for project, using pyenv-virtualenv is recommended, follow [this](https://github.com/pyenv/pyenv-virtualenv?tab=readme-ov-file#installation) documentation for installation.

```sh
pyenv virtualenv 3.12.2 edream_sdk
```

And then activate it

```sh
pyenv activate edream_sdk
```

#### Install requirements

```sh
pip install -r requirements.txt
```

#### Install build tool (skip, already installed on requirements)

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

First, install the installer tool (skip, already installed on requirements):

```sh
pip install installer
```

##### Install package

To install a package from a distribution archive, use:

```sh
python -m installer dist/edream_sdk-0.1.0-py3-none-any.whl
```

##### Uninstall package

If you need to uninstall the package locally, execute next command

```sh
pip uninstall edream_sdk
```

#### Publish package

Pending...

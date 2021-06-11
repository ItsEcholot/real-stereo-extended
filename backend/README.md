# backend

> Info: All commands listed in this readme have to be executed within the `backend` folder.

## Installation

If the devcontainer is used for developing on this project, the installation step can be skipped as it will be done automatically.

Requirements:
- [**python**](https://www.python.org/): `3.8` or newer
- [**poetry**](https://python-poetry.org/): `1.0` or newer

To install all python dependencies and create the venv, run:
```bash
poetry install
```

## Usage

For development, make sure the venv is activated by executing:
```bash
poetry shell
```

To then start the full backend, including the tracking, audio balancing and the API, simply run:
```bash
python src
```

The API will then be available on [`https://localhost:8080/api`](https://localhost:8080/api).

Additionally, the static build from the frontend will be served on [`https://localhost:8080`](https://localhost:8080).

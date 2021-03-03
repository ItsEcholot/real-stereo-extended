# Real Stereo Extended

## Frontend

### Package Manager
[Yarn](https://yarnpkg.com) is used as the package manager for the webapp.


## Backend

### Package Manager
[Poetry](https://python-poetry.org) is used as the package manager to alleviate a lot of problems that pip, pipenv etc. introduce.

### Webserver
The main script starts a webserver using the [Flask](https://flask.palletsprojects.com) framework in a separate thread. This webserver provides the whole API needed for the frontend and can additionally serve the webapp located at `frontend/dist`.


## Development

### Devcontainers
Devcontainers are made for development using VSCode.  
The appeal of devcontainers is the ability of working inside of a Docker container and thus not needing to setup all the development dependencies. The whole environment is created automatically, including all dependencies, vscode extensions and the required vscode settings.  
If there are some new requirements for the environment (e.g. build tools for the Raspberry Pi), they can simply be added to the Dockerfile and everyone working on this repo will also automatically have it.

### Without devcontainers
If you don't want use devcontainers, simply install [Poetry](https://python-poetry.org) on your machine, run `poetry install` inside the backend folder. Select `backend/.venv/bin/python` as your python interpreter in VSCode (if you actually use that editor for python). Otherwise, the packages installed by poetry will not be available. The same also applies if you are using another editor (e.g. PyCharm).
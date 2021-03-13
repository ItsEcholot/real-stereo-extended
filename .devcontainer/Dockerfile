ARG VARIANT=3
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# Install node
ARG INSTALL_NODE="true"
ARG NODE_VERSION="lts/*"
RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# Install the protobuf compiler
RUN curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v3.15.6/protoc-3.15.6-linux-x86_64.zip \
  && unzip -o protoc-3.15.6-linux-x86_64.zip -d /usr/local bin/protoc \
  && unzip -o protoc-3.15.6-linux-x86_64.zip -d /usr/local 'include/*' \
  && rm -f protoc-3.15.6-linux-x86_64.zip \
  && chmod +x /usr/local/bin/protoc

# Install poetry for the vscode user
USER vscode
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH "/home/vscode/.poetry/bin:$PATH"

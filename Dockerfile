FROM python:3.7-buster

ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUALENV_PYTHON=/usr/bin/python3.7

ARG DEV_PACKAGES="python3.7-dev build-essential libgeos-dev"

RUN apt-get update && \
  apt-get install --yes --no-install-recommends \
  python3-pip \
  python3-venv \
  virtualenv \
  ${DEV_PACKAGES} \
  zsh \
  vim \
  xsltproc \
  postgresql-client

ENV SHELL /bin/zsh

RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

COPY . /workspace/

WORKDIR /workspace

RUN pip install -r requirements.txt -r requirements-tests.txt -r dev-requirements.txt

# keep container running until killed - For DEV use only
CMD [ "pserve", "development.ini", "--reload"]

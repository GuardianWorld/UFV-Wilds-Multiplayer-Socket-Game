.PHONY: venv install server client terminal

PYTHON_CMD := python

ifeq ($(OS),Windows_NT)
    PYTHON_CMD = py -3
else
    PYTHON_CMD = $(shell which python3 || which python)
endif

VENV_DIR = .venv
PYTHON = $(VENV_DIR)/Scripts/python
PIP = $(VENV_DIR)/Scripts/pip

ifeq ($(OS),Windows_NT)
    PYTHON = $(VENV_DIR)/Scripts/python
    PIP = $(VENV_DIR)/Scripts/pip
else
    PYTHON = $(VENV_DIR)/bin/python
    PIP = $(VENV_DIR)/bin/pip
endif

venv:
	$(PYTHON_CMD) -m venv $(VENV_DIR)


install: venv
	$(PIP) install -r requirements.txt

server: install
	$(PYTHON) server/server.py 

client: install
	$(PYTHON) client.py

terminal: install
	$(PYTHON) terminal/client_terminal_only.py

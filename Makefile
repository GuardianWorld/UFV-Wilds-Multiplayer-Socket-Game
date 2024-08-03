.PHONY: venv install hot_reload server_install server client_install client

VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

venv:
	python -m venv $(VENV_DIR)

install: venv
	$(PIP) install -r requirements.txt

server:
	$(PYTHON) server/server.py 

hot_reload:
	$(PYTHON) hotreload.py ./server/server.py

client:
	$(PYTHON) client.py

server_install: install
	$(PYTHON) server/server.py

client_install: install
	$(PYTHON) client.py
	
client_host: 
	$(PYTHON) client.py ufvwilds.mixxy.playit.gg 50125

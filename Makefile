include .env
export $(shell sed 's/=.*//' .env)

VENV_ACTIVATE = source $(shell pwd)/.venv/bin/activate
SERVER = streamlit run src/Home.py

install:
	python3 -m venv .venv
	bash -c '$(VENV_ACTIVATE)' && '.venv/bin/python3 -m pip install -r requirements.txt'

run:
# 	Para acrescentar um log
	bash -c '$(VENV_ACTIVATE) && $(SERVER)' > server.log 2>&1 &
# 	bash -c '$(VENV_ACTIVATE) && $(SERVER)'
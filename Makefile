ifneq ("$(wildcard .env)","")
    include .env
    export $(shell sed 's/=.*//' .env)
endif

PYTHON = .venv/bin/python3
STREAMLIT = .venv/bin/streamlit
export PYTHONPATH := $(shell pwd)

install:
	python3 -m venv .venv
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(STREAMLIT) run src/Home.py

init-db:
	@echo "Inicializando o banco de dados..."
	$(PYTHON) -m src.backend.create_tables

test:
	$(PYTHON) -m src.backend.dbconnection

clean:
	rm -rf .venv
	rm -f server.log
	find . -type d -name "__pycache__" -exec rm -rf {} +
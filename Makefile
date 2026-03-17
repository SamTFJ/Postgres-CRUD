include .env
export $(shell sed 's/=.*//' .env)

VENV_ACTIVATE = source $(shell pwd)/.venv/bin/activate
SERVER = streamlit run src/Home.py
TEST = .venv/bin/python3 -m src.backend.dbconnection

install:
	python3 -m venv .venv
<<<<<<< HEAD
	bash -c '$(VENV_ACTIVATE)' && '.venv/bin/python3 -m pip install -r requirements.txt'
=======
	bash -c '$(VENV_ACTIVATE) && .venv/bin/python3 -m pip install -r requirements.txt'
>>>>>>> feature/interfaceup

run:
# 	Para acrescentar um log
# 	bash -c '$(VENV_ACTIVATE) && $(SERVER)' > server.log 2>&1 &
	bash -c '$(VENV_ACTIVATE) && $(SERVER)'

clean:
	rm -f server.log

test:
<<<<<<< HEAD
	bash -c '$(TEST)'
=======
	bash -c '$(TEST)'

init-db:
	bash -c '$(VENV_ACTIVATE) && .venv/bin/python3 -m src.backend.create_tables'
>>>>>>> feature/interfaceup

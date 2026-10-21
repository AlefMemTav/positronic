PYTHON ?= python3

.PHONY: install test run

# Instala as versões diretas fixadas em requirements.txt.
install:
	$(PYTHON) -m pip install -r requirements.txt

# Executa os testes unitários do registrador e do núcleo.
test:
	$(PYTHON) -m unittest discover -s tests -v

# Executa os experimentos exploratórios históricos 1 a 5.
run:
	$(PYTHON) rodar_todos.py

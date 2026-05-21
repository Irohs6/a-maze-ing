.SILENT:

install:
	poetry config virtualenvs.in-project true
	poetry install

run: install
	. .venv/bin/activate; python3 a_maze_ing.py config.txt
	clear

debug: install
	. .venv/bin/activate; python3 -m pdb a_maze_ing.py config.txt

clean:
	rm -rf */*/__pycache__
	rm -rf */__pycache__
	rm -rf __pycache__
	rm -rf */*/.mypy_cache
	rm -rf */.mypy_cache
	rm -rf .mypy_cache
	rm -rf */*/.pytest_cache
	rm -rf */.pytest_cache
	rm -rf .pytest_cache

fclean: clean
	rm -rf .venv
	rm -rf poetry.lock
	rm -rf dist
	rm -rf mazegen.egg-info

lint: install
	. .venv/bin/activate; python3 -m flake8 && printf '\033[1;32mFlake8 all good !\033[0m\n'; python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	. .venv/bin/activate; python3 -m flake8 && printf '\033[1;32mFlake8 all good !\033[0m\n'; python3 -m mypy . --strict

test: install
	. .venv/bin/activate; pytest tests/ -v

.PHONY: install run debug clean fclean lint lint-strict test
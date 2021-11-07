MAKEFLAGS += --always-make --jobs --max-load=3 --output-sync=target

.PHONY: ALL pylint mypy isort black vulture pytype poetryprep

OBJS=dtvprocessing.py resultParser.py stringprocessing.py topturnierprocessing.py tpsprocessing.py singleResultParser.py

ALL: pylint mypy formatting vulture pytype

poetryprep:
	sudo apt install python3-distutils
	poetry env use $$(which python3.9)
	poetry update
	poetry install

pylint:
	-poetry run pylint $(OBJS)

mypy:
	-poetry run mypy --install-types --non-interactive $(OBJS)

out/%.pyi: %.py
	stubgen $^

formatting:
	poetry run isort --python-version 39 --profile black $(OBJS)
	poetry run black $(OBJS)

vulture:
	-poetry run vulture $(OBJS)

pytype:
	-poetry run pytype --keep-going --protocols --precise-return $(OBJS)

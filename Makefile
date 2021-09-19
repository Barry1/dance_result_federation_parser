MAKEFLAGS += --always-make --jobs --max-load=3 --output-sync=target

.PHONY: ALL pylint mypy isort black vulture pytype

OBJS=dtvprocessing.py resultParser.py stringprocessing.py topturnierprocessing.py tpsprocessing.py

ALL: pylint mypy formatting vulture pytype

pylint:
	-pylint $(OBJS)

mypy:
	-mypy --install-types --non-interactive $(OBJS)

out/%.pyi: %.py
	stubgen $^

formatting:
	isort .
	black .

vulture:
	-vulture .

pytype:
	-pytype --keep-going --protocols --precise-return $(OBJS)

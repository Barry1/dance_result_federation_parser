MAKEFLAGS += --always-make --jobs --max-load=3 --output-sync=target

.PHONY: ALL pylint mypy isort black vulture pytype poetryprep

OBJS=dtvprocessing.py resultParser.py stringprocessing.py topturnierprocessing.py tpsprocessing.py singleResultParser.py

ALL: pylint mypy formatting vulture pytype

testruns: BlausBand2018.txt BlausBand2019.txt BlausBand2022.txt

BlauesBand2018.txt:
	poetry run python -OO ./resultParser.py http://www.blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm > BlauesBand2018.txt 2> BlauesBand2018.err

BlauesBand2019.txt:
	poetry run python -OO ./resultParser.py http://www.blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm > BlauesBand2019.txt 2> BlauesBand2019.err

BlauesBand2022.txt:
	poetry run python -OO ./resultParser.py https://turniere.btc-gruen-gold.de/bb2022/index.htm > BlauesBand2022.txt 2> BlauesBand2022.err

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
	poetry run stubgen $^

formatting:
	poetry run isort --python-version 39 --profile black $(OBJS)
	poetry run black $(OBJS)

vulture:
	-poetry run vulture $(OBJS)

pytype:
	-poetry run pytype --keep-going --protocols --precise-return $(OBJS)

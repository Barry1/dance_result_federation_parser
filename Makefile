MAKEFLAGS += --always-make --jobs --max-load=3 --output-sync=target

.PHONY: ALL pylint mypy isort black vulture pytype poetryprep bindeps

OBJS=dtvprocessing.py resultParser.py stringprocessing.py topturnierprocessing.py tpsprocessing.py singleResultParser.py

runme=poetry run python -OO ./resultParser.py

ALL: pylint mypy formatting vulture pytype

testruns: BlausBand2018.txt BlausBand2019.txt BlausBand2022.txt HolmOstern2022.txt

DSF_2022.txt:
	$(runme) https://ergebnisse.ggcbremen.de/2022-06-03.DSF/index.htm > $@ 2> $(@:.txt=.err)

GLM_HGR_SENI_D-B_STD_2022.txt:
	$(runme) http://tps.1sc-norderstedt-tsa.de/20220528/index.htm > $@ 2> $(@:.txt=.err)

HessenTanzt2022.txt:
	$(runme) https://www.hessen-tanzt.de/media/ht2022/index.htm > $@ 2> $(@:.txt=.err)

BlauesBand2018.txt:
	$(runme) http://www.blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm > $@ 2> $(@:.txt=.err)

BlauesBand2019.txt:
	$(runme) http://www.blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm > $@ 2> $(@:.txt=.err)

BlauesBand2022.txt:
	$(runme) https://turniere.btc-gruen-gold.de/bb2022/index.htm > $@ 2> $(@:.txt=.err)

HolmOstern2022.txt:
	$(runme) https://www.die-ostsee-tanzt.de/turnierergebnisse/ostsee-ostern-2022/freitag/index.htm > $@ 2> $(@:.txt=.err)
	$(runme) https://www.die-ostsee-tanzt.de/turnierergebnisse/ostsee-ostern-2022/samstag/index.htm >> $@ 2>> $(@:.txt=.err)
	$(runme) https://www.die-ostsee-tanzt.de/turnierergebnisse/ostsee-ostern-2022/sonntag/index.htm >> $@ 2>> $(@:.txt=.err)
	$(runme) https://www.die-ostsee-tanzt.de/turnierergebnisse/ostsee-ostern-2022/montag/index.htm >> $@ 2>> $(@:.txt=.err)


poetryprep:
	sudo apt install python3-distutils
	poetry env use $$(which python3)
	poetry update
	poetry install

pylint:
	-poetry run pylint $(OBJS)

mypy:
	-poetry run mypy --install-types --non-interactive $(OBJS)

out/%.pyi: %.py
	poetry run stubgen $^

formatting:
	poetry run isort --python-version 310 --profile black $(OBJS)
	poetry run black $(OBJS)

vulture:
	-poetry run vulture $(OBJS)

pytype:
	-poetry run pytype --keep-going --protocols --precise-return $(OBJS)

bindeps:
	sudo apt-get install --assume-yes libxml2-dev libxslt1-dev patchelf

nuitka/resultParser.bin: resultParser.py
	niceload poetry run nuitka3 --follow-imports --output-dir=nuitka --show-progress resultParser.py
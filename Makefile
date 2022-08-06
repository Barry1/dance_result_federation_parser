MAKEFLAGS += --always-make --jobs --max-load=3 --output-sync=target

.PHONY: ALL pylint mypy isort black vulture pytype poetryprep bindeps

OBJS=dtvprocessing.py resultParser.py stringprocessing.py topturnierprocessing.py tpsprocessing.py singleResultParser.py

runme=poetry run python -OO ./resultParser.py
runmesingle=poetry run python -OO ./singleResultParser.py

ALL: pylint mypy formatting vulture pytype

testruns: BlauesBand2018.txt BlauesBand2019.txt BlauesBand2022.txt HolmOstern2022.txt

Enzkloesterle_2022.txt:
	$(runme) https://www.tbw.de/turnierergebnisse/2022/2022_07_30-31_Enzkloesterle/index.htm > $@ 2> $(@:.txt=.err)

danceComp_2022.txt:
	$(runme) https://ergebnisse.dancecomp.de/2022/index.htm > $@ 2> $(@:.txt=.err)

BalSen_2022.txt:
	$(runme) https://tanzen-in-sh.de/ergebnisse/2022/2022-06-18-19_BalticSenior/index.htm > $@ 2> $(@:.txt=.err)

DC_HGR-A_LAT_2022.txt:
	$(runmesingle) https://www.boston-club.de/ergebnis/dchgralat2022/index.htm > $@ 2> $(@:.txt=.err)

DM_SENII_STD_2022.txt:
	$(runmesingle) https://tanzsport-glinde-ergebnisse.de/mediapool/Turniere-2022/0-dm_sen2sstd/index.htm > $@ 2> $(@:.txt=.err)

BadBevensen_2022.txt:
	$(runme) https://www.tanzsport-biedermann.de/results/pfingsten22/index.html > $@ 2> $(@:.txt=.err)

DSF_2022.txt:
	$(runme) https://ergebnisse.ggcbremen.de/2022-06-03.DSF/index.htm > $@ 2> $(@:.txt=.err)

GLM_HGR_SENI_D-B_STD_2022.txt:
	$(runme) http://tps.1sc-norderstedt-tsa.de/20220528/index.htm > $@ 2> $(@:.txt=.err)

HessenTanzt2022.txt:
	$(runme) https://www.hessen-tanzt.de/media/ht2022/index.htm > $@ 2> $(@:.txt=.err)

BlauesBand2018.txt:
	$(runme) http://www.blauesband-berlin.de/Ergebnisse/2018/blauesband2018/index.htm > $@ 2> $(@:.txt=.err)

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

monkeytype.sqlite3:
	poetry run monkeytype run ./resultParser.py

monkeytypeapply:
	for a in `poetry run monkeytype list-modules` ; do poetry run monkeytype apply $a ; done

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

vermin:
	poetry run vermin --eval-annotations --backport asyncio --backport typing *.py

thewholetoolchain: prospector pytype vulture
	poetry run autopep8 $(OBJS)
	-poetry run flake8 $(OBJS)
	-poetry run mypy $(OBJS)
	-poetry run pycodestyle $(OBJS)
	poetry run pyflakes $(OBJS)
	-poetry run pylama $(OBJS)
	-poetry run pylint $(OBJS)
	-poetry run pyright $(OBJS)

prospector:
	-poetry run prospector -X $(OBJS)

dtv_ass_par_check: dtv_associations.parquet
	@echo "5e86bc0d7eb6d3ef8b29cd54c11defe4  dtv_associations.parquet" | md5sum --check

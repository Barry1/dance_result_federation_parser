MAKEFLAGS += --always-make --jobs --max-load=3 --output-sync=target

.PHONY: ALL pylint mypy isort black vulture pytype poetryprep bindeps tpstestruns testruns pyright

#OBJS=dtvprocessing.py dance_result_federation_parser.py  stringprocessing.py topturnierprocessing.py tpsprocessing.py single_result_parser.py 
OBJS=$(shell git ls-files *.py *.pyi)

runme=poetry run python -OO ./dance_result_federation_parser.py
runmesingle=poetry run python -OO ./single_result_parser.py 

ALL: pylint mypy formatting vulture pytype

testruns: BlauesBand2018.txt BlauesBand2019.txt BlauesBand2022.txt HolmOstern2022.txt tpstestruns

tpstestruns: GLM_Sen_IV_und_Sen_V_2022.txt GLM_KIN-JUG_LAT_2022.txt

# https://www.gnu.org/software/make/manual/make.html#Double_002dColon

.PHONY: http\://hatv.de/wrapper/2023/GLM_HGRMAS-D-B-HSV/index.html
GLM_HGR_MASI_D-B_STD_2023.txt: http\://hatv.de/wrapper/2023/GLM_HGRMAS-D-B-HSV/index.html
	$(runme) $< > $@ 2> $(@:.txt=.err)

.PHONY: https\://ergebnisse.tnw.de/vereine/912/2023-02-25/index.htm
RL_DUS_2023.txt: https\://ergebnisse.tnw.de/vereine/912/2023-02-25/index.htm
	$(runme) $< > $@ 2> $(@:.txt=.err)

.PHONY: https\://hatv.de/wrapper/2023/RL_Glinde_2023/index.htm
RL_GLINDE_2023.txt: https\://hatv.de/wrapper/2023/RL_Glinde_2023/index.htm
	$(runme) $< > $@ 2> $(@:.txt=.err)

.PHONY: https\://tanzen-in-sh.de/ergebnisse/2023/2023-02-12_GLM_HGR_MAS_A-S_LAT/index.htm
GLM_HGR-MAS_A-S_LAT_2023.txt: https\://tanzen-in-sh.de/ergebnisse/2023/2023-02-12_GLM_HGR_MAS_A-S_LAT/index.htm
	$(runme) $< > $@ 2> $(@:.txt=.err)

.PHONY: https\://www.clubsaltatio.de/Ergebnisse/glmjugend2022/index.html
GLM_KIN-JUG_LAT_2022.txt: https\://www.clubsaltatio.de/Ergebnisse/glmjugend2022/index.html
	$(runme) $< > $@ 2> $(@:.txt=.err)

.PHONY: https\://tsc-casino-oberalster.de/wp-content/uploads/turnierergebnisse/2022-05-07_GLM_Sen_II-A-S
GLM_SEN_II_A-S_STD_2022.txt: https\://tsc-casino-oberalster.de/wp-content/uploads/turnierergebnisse/2022-05-07_GLM_Sen_II-A-S
	$(runme) $< > $@ 2> $(@:.txt=.err)

.PHONY: https\://tanzen-in-sh.de/ergebnisse/2022/2022-09-24_DP_SENIII_S_STD/index.htm
DP_SEN_III_S_STD_2022.txt: https\://tanzen-in-sh.de/ergebnisse/2022/2022-09-24_DP_SENIII_S_STD/index.htm
	$(runmesingle) $< > $@ 2> $(@:.txt=.err)

.PHONY: http\://www.hatv.de/wrapper/2022/glm_sen-d-b-hsv
GLM_SEN_II+III_D-B_STD_2022.txt: http\://www.hatv.de/wrapper/2022/glm_sen-d-b-hsv
	$(runme) $< > $@ 2> $(@:.txt=.err)

.PHONY: https\://www.ntv-tanzsport.de/fileadmin/ntv/ergebnisse/2022/2022_glm_kin-jug_std/2022_glm_kin-jug_std/index.htm
GLM_KIN-JUG_STD_2022.txt: https\://www.ntv-tanzsport.de/fileadmin/ntv/ergebnisse/2022/2022_glm_kin-jug_std/2022_glm_kin-jug_std/index.htm
	$(runme) $< > $@ 2> $(@:.txt=.err)

.PHONY: https\://www.htv.de/media/22_10_02/index.htm
DM-DP_KIN-JUG_STD_2022.txt: https\://www.htv.de/media/22_10_02/index.htm
	$(runme) $< > $@ 2> $(@:.txt=.err)

Enzkloesterle_2022.txt:
	$(runme) http://www.tbw.de/turnierergebnisse/2022/2022_07_30-31_Enzkloesterle/index.htm > $@ 2> $(@:.txt=.err)

danceComp_2022.txt:
	$(runme) http://ergebnisse.dancecomp.de/2022/index.htm > $@ 2> $(@:.txt=.err)

BalSen_2022.txt:
	$(runme) http://tanzen-in-sh.de/ergebnisse/2022/2022-06-18-19_BalticSenior/index.htm > $@ 2> $(@:.txt=.err)

.PHONY: http\://tanzsport-glinde-ergebnisse.de/mediapool/Turniere-2022/GLM_Sen_IV_und_Sen_V/index.html
GLM_Sen_IV_und_Sen_V_2022.txt: http\://tanzsport-glinde-ergebnisse.de/mediapool/Turniere-2022/GLM_Sen_IV_und_Sen_V/index.html
	$(runme) $< > $@ 2> $(@:.txt=.err)

DC_HGR-A_LAT_2022.txt:
	$(runmesingle) http://www.boston-club.de/ergebnis/dchgralat2022/index.htm > $@ 2> $(@:.txt=.err)

DM_SENII_STD_2022.txt:
	$(runmesingle) http://tanzsport-glinde-ergebnisse.de/mediapool/Turniere-2022/0-dm_sen2sstd/index.htm > $@ 2> $(@:.txt=.err)

BadBevensen_2022.txt:
	$(runme) http://www.tanzsport-biedermann.de/results/pfingsten22/index.html > $@ 2> $(@:.txt=.err)

DSF_2022.txt:
	$(runme) http://ergebnisse.ggcbremen.de/2022-06-03.DSF/index.htm > $@ 2> $(@:.txt=.err)

GLM_HGR_SENI_D-B_STD_2022.txt:
	$(runme) http://tps.1sc-norderstedt-tsa.de/20220528/index.htm > $@ 2> $(@:.txt=.err)

HessenTanzt2022.txt:
	$(runme) http://www.hessen-tanzt.de/media/ht2022/index.htm > $@ 2> $(@:.txt=.err)

BlauesBand2018.txt:
	$(runme) http://www.blauesband-berlin.de/Ergebnisse/2018/blauesband2018/index.htm > $@ 2> $(@:.txt=.err)

BlauesBand2019.txt:
	$(runme) http://www.blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm > $@ 2> $(@:.txt=.err)

BlauesBand2022.txt:
	$(runme) http://turniere.btc-gruen-gold.de/bb2022/index.htm > $@ 2> $(@:.txt=.err)

HolmOstern2022.txt:
	$(runme) http://www.die-ostsee-tanzt.de/turnierergebnisse/ostsee-ostern-2022/freitag/index.htm > $@ 2> $(@:.txt=.err)
	$(runme) http://www.die-ostsee-tanzt.de/turnierergebnisse/ostsee-ostern-2022/samstag/index.htm >> $@ 2>> $(@:.txt=.err)
	$(runme) http://www.die-ostsee-tanzt.de/turnierergebnisse/ostsee-ostern-2022/sonntag/index.htm >> $@ 2>> $(@:.txt=.err)
	$(runme) http://www.die-ostsee-tanzt.de/turnierergebnisse/ostsee-ostern-2022/montag/index.htm >> $@ 2>> $(@:.txt=.err)

poetryprep:
	sudo apt install python3-distutils
	poetry env use $$(which python3)
	poetry update
	poetry install

monkeytype.sqlite3:
	poetry run monkeytype run ./dance_result_federation_parser.py 

monkeytypeapply:
	for a in `poetry run monkeytype list-modules` ; do poetry run monkeytype apply $a ; done

pylint:
	-poetry run pylint $(OBJS)

mypy:
	-poetry run mypy --install-types --non-interactive $(OBJS)

out/%.pyi: %.py
	poetry run stubgen $^

formatting: isort black

isort:
	poetry run isort --python-version 311 --profile black $(OBJS)

black:
	poetry run black $(OBJS)

vulture:
	-poetry run vulture $(OBJS)

pytype:
	-poetry run pytype --keep-going --protocols --precise-return $(OBJS)

pytypediffcheck:
	for a in *.py ; do echo $$a ; poetry run merge-pyi --diff $$a .pytype/pyi/$${a}i ; done

bindeps:
	sudo apt-get install --assume-yes libxml2-dev libxslt1-dev patchelf

nuitka/resultParser.bin: dance_result_federation_parser.py 
	niceload poetry run nuitka3 --follow-imports --output-dir=nuitka --show-progress dance_result_federation_parser.py 

vermin:
	poetry run vermin --eval-annotations --backport asyncio --backport typing *.py

thewholetoolchain: prospector pytype vulture pyright
	poetry run autopep8 $(OBJS)
	-poetry run flake8 $(OBJS)
	-poetry run mypy $(OBJS)
	-poetry run pycodestyle $(OBJS)
	poetry run pyflakes $(OBJS)
	-poetry run pylama $(OBJS)
	-poetry run pylint $(OBJS)

typings/joblib:
	-poetry run pyright $(OBJS) --createstub joblib

typings/pandas:
	-poetry run pyright $(OBJS) --createstub pandas

typings/lxml:
	-poetry run pyright $(OBJS) --createstub lxml

pyright:
	-poetry run pyright $(OBJS)

pyre:
	poetry run pyre --source-directory . check

pysa:
	poetry run pyre --source-directory . analyze

prospector:
	-poetry run prospector -X $(OBJS)

md5sumsave.md5: dtv_associations.parquet
	md5sum $^ > $@ 

dtv_ass_par_check: dtv_associations.parquet
	md5sum --check md5sumsave.md5

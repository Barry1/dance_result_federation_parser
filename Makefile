MAKEFLAGS += --always-make --jobs --max-load=3 --output-sync=target
include Makefile.competitions
.PHONY: ALL pylint mypy isort black vulture pytype poetryprep bindeps tpstestruns testruns pyright pylyze pipdeptree

#<https://stackoverflow.com/questions/4219255/how-do-you-get-the-list-of-targets-in-a-makefile/26339924#26339924>
.PHONY: list
list:
	@LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'

#OBJS=dtvprocessing.py dance_result_federation_parser.py stringprocessing.py topturnierprocessing.py tpsprocessing.py single_result_parser.py 
OBJS=$(shell git ls-files *.py *.pyi)

runme=poetry run python -OO ./dance_result_federation_parser.py https\://$< > $@ 2> $(@:.txt=.err)
rungoc=poetry run python -OO ./goc_parser.py $(subst GOC_,,$(@:.txt=)) https\://$< > $@ 2> $(@:.txt=.err)
cpldb=DanceCouplesData/couples_clubs_federations.sqlite3


$(@:.txt=.err)


runmesingle=poetry run python -OO ./single_result_parser.py https\://$< > $@ 2> $(@:.txt=.err)

ALL: pylint mypy formatting vulture pytype sourcery

.PHONE: multicouplecheck
multicouplecheck:
	sqlite3 -readonly -markdown DanceCouplesData/couples_clubs_federations.sqlite3 "select * from CoupleClubFederation where Paar like \"%Ebeling%\";"
	sqlite3 -readonly -markdown DanceCouplesData/couples_clubs_federations.sqlite3 "select count(*) from CoupleClubFederation;"
	sqlite3 -readonly -markdown DanceCouplesData/couples_clubs_federations.sqlite3 "select count(*) from CoupleClubFederation where Paar like \"%,%/%,%\";"


.PHONY: dbreset
dbreset:
	sqlite3 $(cpldb) "delete from COUPLES;"
	sqlite3 $(cpldb) "delete from CLUBS;"
	sqlite3 $(cpldb) "delete from sqlite_sequence;"
	sqlite3 $(cpldb) "VACUUM;"
	rm -rf dtv_associations.parquet
	rm -rf *_*.txt *.err

.PHONY: dbcare
dbcare:
	sqlite3 $(cpldb) "VACUUM;"

.PHONY: dbevals
dbevals: $(cpldb)
	sqlite3 -markdown $(cpldb) "select * from Fed_Club_Count;"
	sqlite3 -markdown $(cpldb) "select * from activCouplesFederation;"

pipdeptree:
	poetry run pipdeptree --packages=aiofiles,bs4,fastparquet,html5lib,joblib,lxml,pyarrow,pytype,requests,typing

pylyze:
	poetry run pylyzer $(OBJS)

sourcery:
	poetry run sourcery review $(OBJS) --summary --fix --verbose

testruns: BlauesBand2018.txt BlauesBand2019.txt BlauesBand2022.txt HolmOstern2022.txt tpstestruns

tpstestruns: GLM_Sen_IV_und_Sen_V_2022.txt GLM_KIN-JUG_LAT_2022.txt

# https://www.gnu.org/software/make/manual/make.html#Double_002dColon

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

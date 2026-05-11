MAKEFLAGS += --always-make --jobs=1 --max-load=3 --output-sync=target
# all geht nicht parallel
include Makefile.competitions
.PHONY: alltools pylint mypy isort black vulture pytype poetryprep bindeps tpstestruns testruns pyright pylyze pipdeptree formatting clean test

# --- Konfiguration ---
PYTHON_SCRIPT = ./dance_result_federation_parser.py
ifndef GITHUB_ACTION
#$(info Not in a GITHUB Action)
PYTHON_CALL = poetry run python -OO $(PYTHON_SCRIPT)
else
#$(info Within a GITHUB Action)
PYTHON_CALL = python3 -OO $(PYTHON_SCRIPT)
endif
HASH_DIR = .hashes
RESULTS_DIR = Results
MD_RESULTS_DIR = mdResults
# --- AUTO-COMPLETION ---
# 1. Wir extrahieren alle Dateinamen aus den URL-Definitionen aller Makefiles
# Das Ergebnis ist eine Liste wie: 2026_HessenTanzt.txt 2025_Andere.txt
ALL_POSSIBLE_TXT = $(shell grep -h "^URL_.*\.txt =" $(MAKEFILE_LIST) | sed 's/^URL_\(.*\) =.*/$(RESULTS_DIR)\/\1/' | sort | uniq)
ALL_POSSIBLE_MD = $(patsubst %.txt,%.md,$(shell grep -h "^URL_.*\.txt =" $(MAKEFILE_LIST) | sed 's/^URL_\(.*\) =.*/$(MD_RESULTS_DIR)\/\1/' | sort | uniq))
# 2. Wir definieren diese Dateien als explizite Ziele, aber ohne eigene Befehle.
# Dadurch "sieht" die Bash-Completion diese Targets.
# Die eigentliche Arbeit erledigt weiterhin die Pattern-Rule %.txt:
$(ALL_POSSIBLE_TXT):
$(ALL_POSSIBLE_MD):
# --- AUTO-COMPLETION ---

.PHONY: all
all: $(ALL_POSSIBLE_TXT) $(ALL_POSSIBLE_MD)

.PHONY: info
info:
	$(info Mögliche .txt-Ziele:)
	$(info $(ALL_POSSIBLE_TXT))
	$(info Mögliche .md-Ziele:)
	$(info $(ALL_POSSIBLE_MD))
#%.md: %.txt
#	mv $< $@

%.md:
	@# 1. Sicherstellen, dass das Hash-Verzeichnis existiert
	@mkdir -p $(HASH_DIR) $(MD_RESULTS_DIR)
	
	@# 2. Die URL für das aktuelle Target dynamisch auflösen
	$(eval CURRENT_URL := $(URL_$(@F:.md=.txt)))
	@URL="$(CURRENT_URL)"; \
	HASH_FILE="$(HASH_DIR)/.$(@F:.md=.sha256)"; \
	\
	if [ -z "$$URL" ]; then \
		echo "Error: No URL defined for $(@F) (Variable URL_$(@F) is empty)"; \
		exit 1; \
	fi; \
	\
	CURRENT_HASH=$$(curl -s "$$URL" | sha256sum | cut -d' ' -f1); \
	\
	if [ -f "$$HASH_FILE" ] && [ "$$CURRENT_HASH" = "$$(cat $$HASH_FILE)" ] && [ -f $@ ]; then \
		echo "No changes for $@. Skipping..."; \
	else \
		echo "Change detected or file missing. Updating $@..."; \
		echo "$$CURRENT_HASH" > $$HASH_FILE; \
		mv config.toml versteckt_config.toml; \
		$(PYTHON_CALL) "$$URL" > $@; \
		mv versteckt_config.toml config.toml; \
	fi

%.txt:
	@# 1. Sicherstellen, dass das Hash-Verzeichnis existiert
	@mkdir -p $(HASH_DIR) $(RESULTS_DIR)
	
	@# 2. Die URL für das aktuelle Target dynamisch auflösen
	$(eval CURRENT_URL := $(URL_$(@F)))
	@URL="$(CURRENT_URL)"; \
	HASH_FILE="$(HASH_DIR)/.$(@F:.txt=.sha256)"; \
	\
	if [ -z "$$URL" ]; then \
		echo "Error: No URL defined for $(@F) (Variable URL_$(@F) is empty)"; \
		exit 1; \
	fi; \
	\
	CURRENT_HASH=$$(curl -s "$$URL" | sha256sum | cut -d' ' -f1); \
	\
	if [ -f "$$HASH_FILE" ] && [ "$$CURRENT_HASH" = "$$(cat $$HASH_FILE)" ] && [ -f $@ ]; then \
		echo "No changes for $@. Skipping..."; \
	else \
		echo "Change detected or file missing. Updating $@..."; \
		echo "$$CURRENT_HASH" > $$HASH_FILE; \
		$(PYTHON_CALL) "$$URL" > $@; \
	fi

#<https://stackoverflow.com/questions/4219255/how-do-you-get-the-list-of-targets-in-a-makefile/26339924#26339924>
.PHONY: list
list:
	@#LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'
	@#echo "Erzeugbare .txt-Dateien (mit definierter URL):"
	@# Wir nutzen 'grep', um im aktuellen Makefile (und ggf. include-Dateien) 
	@# alle Zeilen zu finden, die mit 'URL_' beginnen und auf '.txt' enden.
	@# Dann extrahieren wir den Variablennamen und entfernen das 'URL_' Präfix.
	@grep -r "^URL_.*\.txt =" $(MAKEFILE_LIST) | sed 's/.*URL_\(.*\) =.*/Results\/\1/' | sort | uniq
	@#echo ""
	@#echo "Tipp: Nutzen Sie 'make <dateiname>.txt', um eine Datei zu erzeugen."
#OBJS=dtvprocessing.py dance_result_federation_parser.py stringprocessing.py topturnierprocessing.py tpsprocessing.py single_result_parser.py 
OBJS=$(shell git ls-files *.py *.pyi)

runme=poetry run python -OO ./dance_result_federation_parser.py https\://$< > $@ 2> $(@:.txt=.err)
rungoc=poetry run python -OO ./goc_parser.py $(subst GOC_,,$(@:.txt=)) > $@ 2> $(@:.txt=.err)
cpldb=DanceCouplesData/couples_clubs_federations.sqlite3

runmesingle=poetry run python -OO ./single_result_parser.py https\://$< > $@ 2> $(@:.txt=.err)

alltools: pylint mypy formatting vulture pytype sourcery

Pipfile.lock: Pipfile
	pipenv lock

.PHONY: pyupgrade
pyupgrade:
	poetry run pyupgrade --py312-plus $(OBJS)

.PHONY: multicouplecheck
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
	poetry run python -OO sqlitedatabase.py
	sqlite3 $(cpldb) "VACUUM;"

.PHONY: dbevals
dbevals: $(cpldb)
	sqlite3 -markdown $(cpldb) "select * from Fed_Club_Count;"
	sqlite3 -markdown $(cpldb) "select * from activCouplesFederation;"

pipdeptree:
	poetry run pipdeptree --packages=aiofiles,bs4,fastparquet,html5lib,joblib,lxml,pyarrow,pytype,requests,typing

pylyze:
	poetry run pylyzer dance_result_federation_parser.py single_result_parser.py

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

dance_result_federation_parser.bin: dance_result_federation_parser.py
	sudo nala install patchelf ccache
	nice poetry run nuitka --onefile --lto=yes --follow-imports dance_result_federation_parser.py --include-package=fastparquet

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

MAKEFLAGS += --always-make --jobs --max-load=3 --output-sync=target

.PHONY: ALL pylint mypy isort black vulture pytype poetryprep bindeps tpstestruns testruns pyright pylyze pipdeptree

#OBJS=dtvprocessing.py dance_result_federation_parser.py stringprocessing.py topturnierprocessing.py tpsprocessing.py single_result_parser.py 
OBJS=$(shell git ls-files *.py *.pyi)

runme=poetry run python -OO ./dance_result_federation_parser.py
runmesingle=poetry run python -OO ./single_result_parser.py 

ALL: pylint mypy formatting vulture pytype sourcery

pipdeptree:
	poetry run pipdeptree --packages=aiofiles,bs4,fastparquet,html5lib,joblib,lxml,pyarrow,pytype,requests,typing

pylyze:
	poetry run pylyzer $(OBJS)

.PHONY: ltvb.de/wp-content/uploads/results/15209/index.htm
DM_HGR_S_Kombi_2024.txt: ltvb.de/wp-content/uploads/results/15209/index.htm
	$(runmesingle) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: ltvb.de/wp-content/uploads/results/15218/index.htm
DC_HGR_A_LAT_2024.txt: ltvb.de/wp-content/uploads/results/15218/index.htm
	$(runmesingle) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: hannoversche-tanzsporttage.de/wp-content/uploads/ergebnisse/hatatas2024/index.htm
HaTaTa2024.txt: hannoversche-tanzsporttage.de/wp-content/uploads/ergebnisse/hatatas2024/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.gruen-weiss-aachen.de/files/ergebnisse/3le-2024/3le-2024/3-1506_dm_mas2sstd/index.htm#www.gruen-weiss-aachen.de/files/ergebnisse/3le-2024/3le-2024/index.htm
DM_MASII_S_STD_2024.txt: www.gruen-weiss-aachen.de/files/ergebnisse/3le-2024/3le-2024/3-1506_dm_mas2sstd/index.htm
#	$(runme) https\://$< > $@ 2> $(@:.txt=.err)
	$(runmesingle) https\://$< > $@ 2> $(@:.txt=.err)


.PHONY: hatv.de/wrapper/2024/GLM-Savoy/index.html
GLM_HGRII_MASI-III_LAT_2024.txt: hatv.de/wrapper/2024/GLM-Savoy/index.html
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: ergebnisse.ggcbremen.de/2024-05-31.DSF/
DSF_2024.txt: ergebnisse.ggcbremen.de/2024-05-31.DSF/
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: ltvb.de/wp-content/uploads/results/15138/index.htm
RL_Fuerth_2024.txt: ltvb.de/wp-content/uploads/results/15138/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.equalitydancing.de/files/Ergebnisse/240518u19_DM2024-Koeln/index.htm
DM_Equality_2024.txt: www.equalitydancing.de/files/Ergebnisse/240518u19_DM2024-Koeln/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.tsz-stuttgart.de/fileadmin/01_TSZ_Stuttgart/ergebnisse/2024_DM_MAS_U21/index.htm
DM_Kombi_U18MASIV_STD_2024.txt: www.tsz-stuttgart.de/fileadmin/01_TSZ_Stuttgart/ergebnisse/2024_DM_MAS_U21/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.hessen-tanzt.de/media/ht2024/index.htm
HessenTanzt_2024.txt: www.hessen-tanzt.de/media/ht2024/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)


.PHONY: www.ntv-tanzsport.de/fileadmin/ntv/ergebnisse/2024/GLM_OL_2024/GLM_OL_2024/index.htm
GLM_HGR_MAS_D-B_STD_2024.txt : www.ntv-tanzsport.de/fileadmin/ntv/ergebnisse/2024/GLM_OL_2024/GLM_OL_2024/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: berlin-dance-festival.de/files/bdf/results/2024/index.htm
BDF_2024.txt: berlin-dance-festival.de/files/bdf/results/2024/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.tanzclub-bernau.de/Tunierergebnisse/DM2024/16032024/index.htm
DM_Latein_2024.txt: www.tanzclub-bernau.de/Tunierergebnisse/DM2024/16032024/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2024/2024-02-24_GLM_MasIV_STD/
GLM_MasIV_STD_2024.txt: tanzen-in-sh.de/ergebnisse/2024/2024-02-24_GLM_MasIV_STD/
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.ntv-tanzsport.de/fileadmin/ntv/ergebnisse/2024/2024_lm_mas_ii_b-s_std/2024_lm_mas_ii_b-s_std/index.htm
GLM_MasII_BAS_STD_2024.txt: www.ntv-tanzsport.de/fileadmin/ntv/ergebnisse/2024/2024_lm_mas_ii_b-s_std/2024_lm_mas_ii_b-s_std/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: app.ceronne.de/ergebnisse/994_Landesmeisterschaft%20Nord%20Latein/
GLM_HGR_A+S_MAS_S_LAT_2024.txt: app.ceronne.de/ergebnisse/994_Landesmeisterschaft%20Nord%20Latein/
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: app.ceronne.de/ergebnisse/993_GM_Nord_2024/
GBM_Kombi_2024.txt: app.ceronne.de/ergebnisse/993_GM_Nord_2024/
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: hatv.de/wrapper/2024/RL_Glinde/index.htm
RL_GLINDE_2024.txt: hatv.de/wrapper/2024/RL_Glinde/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-11-25-26_BYO/
BYO_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-11-25-26_BYO/
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.owl-tanzt.de/turniere/2023/
OWL_2023.txt: www.owl-tanzt.de/turniere/2023/
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: ltvb.de/wp-content/uploads/results/13941/index.htm
DM_Kin-Jug_STD_2023.txt: ltvb.de/wp-content/uploads/results/13941/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-09-24_GLM5_HGR_A-S_STD/
GLM5_HgrMasI_AS_STD_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-09-24_GLM5_HGR_A-S_STD/
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-09-16_GLM5_Kin-Jug_STD/index.html
GLM5_Kin-Jug_STD_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-09-16_GLM5_Kin-Jug_STD/index.html
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-11-04_DM_HGR_S_STD/index.htm
DM_HGRSSTD_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-11-04_DM_HGR_S_STD/index.htm
	$(runmesingle) https\://$< > $@ 2> $(@:.txt=.err)


.PHONY: www.hatv.de/wrapper/2023/dm_mas_iii_s_std_2023/0-dm_mas3sstd/index.htm
DM_MAS3SSTD_2023.txt: www.hatv.de/wrapper/2023/dm_mas_iii_s_std_2023/0-dm_mas3sstd/index.htm
	$(runmesingle) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.ntv-tanzsport.de/fileadmin/ntv/ergebnisse/2023/3-1006_dc_hgralat/3-1006_dc_hgralat/index.htm
DC_HGR-A-LAT_2023.txt: www.ntv-tanzsport.de/fileadmin/ntv/ergebnisse/2023/3-1006_dc_hgralat/3-1006_dc_hgralat/index.htm
	$(runmesingle) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-06-10_DM_MAS-II_S_STD/0-dm_mas2sstd/index.htm
dm_mas2sstd_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-06-10_DM_MAS-II_S_STD/0-dm_mas2sstd/index.htm
	$(runmesingle) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-09-09_GLM4_HGR_D-B_LAT/index.htm
GLM4_HGR_D-B_LAT_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-09-09_GLM4_HGR_D-B_LAT/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-09-02_GLM_HGRII_D-S_STD/index.htm
GLM_HGRII_D-S_STD_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-09-02_GLM_HGRII_D-S_STD/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-09-03_GLM4_MASII-III_D-B_STD/index.htm
GLM4_MASII-III_D-B_STD_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-09-03_GLM4_MASII-III_D-B_STD/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: ergebnisse.dancecomp.de/2024/index.htm
danceComp_2024.txt: ergebnisse.dancecomp.de/2024/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: ergebnisse.dancecomp.de/2023/index.htm
danceComp_2023.txt: ergebnisse.dancecomp.de/2023/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: ergebnisse.ggcbremen.de/2023-06-02.Dance.Sport.Festival/index.htm
DSF_2023.txt: ergebnisse.ggcbremen.de/2023-06-02.Dance.Sport.Festival/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

sourcery:
	poetry run sourcery review $(OBJS) --summary --fix --verbose

testruns: BlauesBand2018.txt BlauesBand2019.txt BlauesBand2022.txt HolmOstern2022.txt tpstestruns

tpstestruns: GLM_Sen_IV_und_Sen_V_2022.txt GLM_KIN-JUG_LAT_2022.txt

.PHONY: www.hessen-tanzt.de/media/ht2023/index.htm
HessenTanzt_2023.txt: www.hessen-tanzt.de/media/ht2023/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: ltvb.de/wp-content/uploads/results/13347/index.htm
Nuernberg_2023.txt: ltvb.de/wp-content/uploads/results/13347/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: berlin-dance-festival.de/files/bdf/results/2023/index.htm
BeDaFe_2023.txt: berlin-dance-festival.de/files/bdf/results/2023/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: turniere.btc-gruen-gold.de/bb2024/index.htm
BlauesBand2024.txt: turniere.btc-gruen-gold.de/bb2024/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: turniere.btc-gruen-gold.de/bb2023/index.htm
BlauesBand2023.txt: turniere.btc-gruen-gold.de/bb2023/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.tanzsportclub-dortmund.de/ergebnisse/2023/dmkamen23/
Kamen_2023.txt: www.tanzsportclub-dortmund.de/ergebnisse/2023/dmkamen23/
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

# https://www.gnu.org/software/make/manual/make.html#Double_002dColon

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-03-11_GBM_Kombi/index.htm
GBM_Kombi_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-03-11_GBM_Kombi/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)


.PHONY: www.goc-stuttgart.de/programm/ergebnis-archiv-kopie-1
GOC_ALLTIME.txt: www.goc-stuttgart.de/programm/ergebnis-archiv-kopie-1
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)


.PHONY: hatv.de/wrapper/2023/GLM-MAS-IIA-IIS-MAS-V-Std-TSVBuchholz/index.html
GLM4_MASII_AS_MASV_S_STD_2023.txt: hatv.de/wrapper/2023/GLM-MAS-IIA-IIS-MAS-V-Std-TSVBuchholz/index.html
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: hatv.de/wrapper/2023/GLM_HGRMAS-D-B-HSV/index.html
GLM_HGR_MASI_D-B_STD_2023.txt: hatv.de/wrapper/2023/GLM_HGRMAS-D-B-HSV/index.html
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: ergebnisse.tnw.de/vereine/912/2023-02-25/index.htm
RL_DUS_2023.txt: ergebnisse.tnw.de/vereine/912/2023-02-25/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: hatv.de/wrapper/2023/RL_Glinde_2023/index.htm
RL_GLINDE_2023.txt: hatv.de/wrapper/2023/RL_Glinde_2023/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-02-12_GLM_HGR_MAS_A-S_LAT/index.htm
GLM_HGR-MAS_A-S_LAT_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-02-12_GLM_HGR_MAS_A-S_LAT/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.clubsaltatio.de/Ergebnisse/glmjugend2022/index.html
GLM_KIN-JUG_LAT_2022.txt: www.clubsaltatio.de/Ergebnisse/glmjugend2022/index.html
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tsc-casino-oberalster.de/wp-content/uploads/turnierergebnisse/2022-05-07_GLM_Sen_II-A-S
GLM_SEN_II_A-S_STD_2022.txt: tsc-casino-oberalster.de/wp-content/uploads/turnierergebnisse/2022-05-07_GLM_Sen_II-A-S
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2022/2022-09-24_DP_SENIII_S_STD/index.htm
DP_SEN_III_S_STD_2022.txt: tanzen-in-sh.de/ergebnisse/2022/2022-09-24_DP_SENIII_S_STD/index.htm
	$(runmesingle) $< > $@ 2> $(@:.txt=.err)

.PHONY: www.hatv.de/wrapper/2022/glm_sen-d-b-hsv
GLM_SEN_II+III_D-B_STD_2022.txt: www.hatv.de/wrapper/2022/glm_sen-d-b-hsv
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.ntv-tanzsport.de/fileadmin/ntv/ergebnisse/2022/2022_glm_kin-jug_std/2022_glm_kin-jug_std/index.htm
GLM_KIN-JUG_STD_2022.txt: www.ntv-tanzsport.de/fileadmin/ntv/ergebnisse/2022/2022_glm_kin-jug_std/2022_glm_kin-jug_std/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: www.htv.de/media/22_10_02/index.htm
DM-DP_KIN-JUG_STD_2022.txt: www.htv.de/media/22_10_02/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

.PHONY: tanzen-in-sh.de/ergebnisse/2023/2023-03-12_GLM4_MASIV_D-S_STD/index.htm
GLM4_MASIV_STD_2023.txt: tanzen-in-sh.de/ergebnisse/2023/2023-03-12_GLM4_MASIV_D-S_STD/index.htm
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

Enzkloesterle_2022.txt:
	$(runme) http://www.tbw.de/turnierergebnisse/2022/2022_07_30-31_Enzkloesterle/index.htm > $@ 2> $(@:.txt=.err)

danceComp_2022.txt:
	$(runme) http://ergebnisse.dancecomp.de/2022/index.htm > $@ 2> $(@:.txt=.err)

BalSen_2022.txt:
	$(runme) http://tanzen-in-sh.de/ergebnisse/2022/2022-06-18-19_BalticSenior/index.htm > $@ 2> $(@:.txt=.err)

.PHONY: tanzsport-glinde-ergebnisse.de/mediapool/Turniere-2022/GLM_Sen_IV_und_Sen_V/index.html
GLM_Sen_IV_und_Sen_V_2022.txt: tanzsport-glinde-ergebnisse.de/mediapool/Turniere-2022/GLM_Sen_IV_und_Sen_V/index.html
	$(runme) https\://$< > $@ 2> $(@:.txt=.err)

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

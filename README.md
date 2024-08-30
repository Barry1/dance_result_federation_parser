---
title: dance_result_federation_parser
author: Dr. Bastian Ebeling
---

python tool to parse dance competition results for couples of given federation

I use [![GitHub Super-Linter](https://github.com/Barry1/dance_result_federation_parser/actions/workflows/lintme.yml/badge.svg)](https://github.com/marketplace/actions/super-linter)
for code quality.

Further information to follow - but in short - just handover an event URL to `dance_result_federation_parser.py` or a
single competition URL to `single_result_parser.py`.

Some configuration could be done in the file `config.toml` with the following values:

| Value | Type | Sense |
|---|---|---|
|HEADLINELINKS| True, False||
   | IMG_PREP| True, False||
   | PYANNOTATE| True, False||
 |   ESVCOUPLES| True, False||
  |  RUN_ASYNC| True, False||
 |   TOTHREAD| True, False||
  |  RESULTTABLE| True, False||
  |  THEFEDERATION| ||
 |   CHECKINGURLS| list[str]||
 |   RESULTFORMAT| "TSH", "MARKDOWN"||
 |   INFORMEMAIL| str | Email-Address for feedback|
 

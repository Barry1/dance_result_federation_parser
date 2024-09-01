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

| Value         | Type              | Sense                                                                        |
| ------------- | ----------------- | ---------------------------------------------------------------------------- |
| CHECKINGURLS  | list[str]         | place some tournament links for testing purposes                             |
| ESVCOUPLES    | True, **False**   | Try to get couples out of the ESV, user+pass in `.credentials`               |
| HEADLINELINKS | True, **False**   | Should the Headline for each competition directly link to the single result? |
| IMG_PREP      | True, **False**   | Do you want placeholders for images?                                         |
| INFORMEMAIL   | str               | Email-Address for feedback                                                   |
| PYANNOTATE    | True, **False**   | Development - Annotation of Types                                            |
| RESULTFORMAT  | "TSH", "MARKDOWN" | export for TSH=Joomla or Markdown. More to come                              |
| RESULTTABLE   | **True**, False   | Result as Table of Bullet-List                                               |
| RUN_ASYNC     | **True**, False   | Use asynchronous methods for better performance                              |
| THEFEDERATION | str               | Abbreviation for the national federation, like "TSH" or "HATV"               |
| TOTHREAD      | True, **False**   | Parallelization by THREADS or TASKS                                          |

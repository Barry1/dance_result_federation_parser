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
| HEADLINELINKS | True, False       | Should the Headline for each competition directly link to the single result? |
| IMG_PREP      | True, False       | Do you want placeholders for images?                                         |
| PYANNOTATE    | True, False       | Development - Annotation of Types                                            |
| ESVCOUPLES    | True, False       | Try to get couples out of the ESV, user+pass in `.credentials`               |
| RUN_ASYNC     | True, False       | Use asynchronous methods for better performance                              |
| TOTHREAD      | True, False       | Parallelization by THREADS or TASKS                                          |
| RESULTTABLE   | True, False       | Result as Table of Bullet-List                                               |
| THEFEDERATION | str               | Abbreviation for the national federation, like "TSH" or "HATV"               |
| CHECKINGURLS  | list[str]         | place some tournament links for testing purposes                             |
| RESULTFORMAT  | "TSH", "MARKDOWN" | export for TSH=Joomla or Markdown. More to come                              |
| INFORMEMAIL   | str               | Email-Address for feedback                                                   |

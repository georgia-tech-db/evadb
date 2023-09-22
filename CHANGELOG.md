# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

##  [Unreleased]
### [Added]
### [Changed]
### [Deprecated]
### [Removed]

##  [0.3.6] - 2023-09-21

* PR #1181: releass: bump a version further to skip cached wheel 
* PR #1179: fix: release change log 
* PR #1177: fix: release action 
* PR #1176: fix: release 
* PR #1174: fix: trigger build 
* PR #1173: fix: release on success only and credential to pass protection rule 
* PR #1172: Release v0.3.5 
* PR #1169: fix: hotfix for the failing staging build 
* PR #1159: Load query exception for invalid file format  
* PR #1164: Fix model train with Ludwig on Colab 
* PR #1155: feat: add support for enabling ORDER BY on non projected columns 
* PR #1158: Adding Algolia search to Eva-DB Docs 
* PR #1146: `CREATE OR REPLACE FUNCTION` 
* PR #1154: feat: add github actions to sync and release wheel 
* PR #1123: Updates evadb apps 
* PR #1157: chore
* PR #977: chore
* PR #1137: feat: add support for if not exists in create db  
* PR #1132: docs: add home sale forecast usecase into documentation 
* PR #1136: feat: support order by using the projection columns 
* PR #1030: Add model inference documentation 
* PR #1134: ci: staging build fix 
* PR #1124: fix: third-party test 
* PR #1118: Add a model forecasting notebook in tutorials 
* PR #1125: feat: create table in integration table from evadb select query 
* PR #1122: fix: flaky ci unit tests 
* PR #1113: fix: update docs and notebooks 
* PR #1114: feat: Improve db integration 
* PR #1108: Set the right output column type for forecast functions 
* PR #1107: Added null handling and tests for case insensitive string matching 
* PR #1087: Support `SELECT expr;` which does not require `FROM table`  
* PR #1090: Making `Ludwig` and `HuggingFace` case insensitive 
* PR #1027: Adding support for MariaDb as backend for EvaDB 
* PR #1101: Fix forecasting integration test 
* PR #1094: Fixes date and frequency issues in forecasting 
* PR #1096: Rename l_plan and p_plan 
* PR #1091: fix: evadb is now consistent with lowercase 
* PR #1092: feat: Drop database 
* PR #1082: feat: create index if exists 
* PR #1088: fix: df merging issues when multiple predicates  
* PR #1086: Update parameters documentation for forecast 
* PR #1084: Fix column name related issue for Forecast functions 
* PR #1073: fix: create index from single document 
* PR #1080: `pandas.DataFrame.fillna` is deprecated 
* PR #1060: Bump v0.3.5+dev 
* PR #1062: Update UDF to function in model-forecasting.rst 

##  [0.3.4] - 2023-09-06

* PR #1057: fix: staging build fix 
* PR #1056: fix: update notebook outputs 
* PR #1053: docs: AI powered join 
* PR #1054: fix: lint for notebooks 
* PR #1051: fix: create function forecast due to incorrect merging 
* PR #1047: fix: update udf to function in notebooks and docs 
* PR #1046: fix: add missing needed file 
* PR #1043: Hot fix forecasting 
* PR #1026: Removing quotes from udf_metadata_key 
* PR #969: Forecasting in EVA 
* PR #1034: feat: UDF migrates to Function 
* PR #1035: Fix all doc issues 
* PR #1029: Fix the link in new-data-source.rst 
* PR #1023: Feat : Sqlite Database Handler 
* PR #1019: feat: add CI for MySQL 
* PR #1025: Add mysql as an available data source into documentation 
* PR #965: msyql integration added 
* PR #1018: fix: install pkg and ignore tutorials 
* PR #1016: Revamp getting started.  
* PR #1014: Extend the circle ci link check to include README.md 
* PR #1015: Enable Coverage Check 
* PR #1008: fix: CREATE TABLE persists entry in the catalog even if the query fails 
* PR #1007: fix: create Table fails when projecting column from native table 
* PR #1006: fix: update more verbose message for creating database 
* PR #991: feat: add use case of LLM on food review running on colab 
* PR #997: fix: improve error msg 
* PR #996: Fix all BUILD warning and link validation in the documentation 
* PR #986: docs: Update README.md 
* PR #983: doc: fix nav bar 

##  [0.3.3] - 2023-08-29

* PR #983: doc: fix nav bar 
* PR #982: fix: batch merge causing redundant row 
* PR #981: fix: use the same interface 
* PR #979: docs: added logo 
* PR #980: docs: Update README.md 
* PR #975: Simplify the ludwig dependency 
* PR #972: feat: improve dev doc 
* PR #971: Revert "feat: Integrating thirdy party Slack API " 
* PR #967: feat: Integrating thirdy party Slack API  
* PR #966: Developer guide for new structure data source integration 
* PR #949: feat: improve circle ci 
* PR #946: Support `SELECT Func

##  [0.3.2] - 2023-08-25

* PR #953: docs: Fix User Reference and Dev Guide 
* PR #952: docs: Update PULL_REQUEST_TEMPLATE.md 
* PR #951: docs: updated overview and usecases 
* PR #950: docs: improve the docs 
* PR #943: Auto drop row id for `CREATE UDF xxx FROM 
* PR #945: fix: circle ci pip + setuptools conflict 
* PR #942: feat: select from native database 
* PR #921: fix: more detailed YouTube QA app blog generator 
* PR #940: feat: update ci test for third party integration 
* PR #941: chore
* PR #935: Ludwig-based model train and tune support. 
* PR #937: feat: integration for pg_handler added 
* PR #939: Hot Fix for Fuzzy Join 
* PR #936: Use statement 
* PR #938: pydantic > 2 conflicts with ray 
* PR #932: feat: postgres integration - create database   
* PR #931: Revert "Revert "Fix benchmark documentation 
* PR #931: Revert "Fix benchmark documentation 
* PR #931: Fix benchmark documentation 
* PR #930: Text summarization benchmark with MindsDB and EvaDB 
* PR #929: Fix problems found when running hugging face text summariztion model on large input. 
* PR #928: feat: improve the use case doc 
* PR #927: chore
* PR #925: chore
* PR #926: chore
* PR #924: fix tutorials 11-similarity-search-for-motif-mining.ipynb 
* PR #922: feat : Run EvaDB on Postgres 
* PR #919: chore: redirect to evadb 
* PR #918: docs: updates 
* PR #916: Bump v0.3.2+dev 
* PR #915: Release 0.3.1 

##  [0.3.1] - 2023-06-30

* PR #913: fix: motif_mining query 
* PR #895: fix: Renaming Cursor Functions 
* PR #911: Added comments for ChatGPT UDF. 
* PR #908: feat: migrate to sqlalchemy 2.0 
* PR #910: Bump v0.3.1+dev 
* PR #907: feat: table filtering based on multiple keywords UDF 

##  [0.3.0] - 2023-06-27

* PR #907: feat: table filtering based on multiple keywords UDF 
* PR #906: ci: add 3.11 
* PR #905: feat: remove ocr 
* PR #904: feat: chatgpt prompt arg 
* PR #903: Bump v0.3.0+dev 

##  [0.2.15] - 2023-06-26

* PR #898: fix: index creation better error msg 
* PR #817: fix: GPU ids and degree of parallelism 
* PR #897: feat: add support for 3.11 
* PR #885: feat: pandas qa sample app 
* PR #896: app: youtube channel qa app 
* PR #893: feat: cleanup create mat view 
* PR #892: feat: update notebooks 
* PR #894: fix: Youtube app 

##  [0.2.14] - 2023-06-24

* PR #887: fix: Notebooks fix 
* PR #889: fix: ocr donut model  
* PR #886: doc: improve youtube qa app doc 
* PR #878: feat: make ray optional 
* PR #884: test: disable reuse tests 
* PR #883: test: update tests 
* PR #880: feat: pandas qa 
* PR #882: feat: adding more functions to Python API 
* PR #881: docs: minor updates 
* PR #863: feat: youtube qa app support analyzing a local video 
* PR #877: notebooks: updates 
* PR #875: Bump v0.2.14+dev 
* PR #873: notebooks: update notebooks 

##  [0.2.13] - 2023-06-17

* PR #873: notebooks: update notebooks 
* PR #872: Bump v0.2.13+dev 
* PR #836: feat: OCR UDF based on Donut Hugging Face Model 

##  [0.2.12] - 2023-06-16

* PR #836: feat: OCR UDF based on Donut Hugging Face Model 
* PR #865: feat: reduce package dependencies 
* PR #870: refactor: Moved `col_name` -> `name` in `TupleValueExpression` 
* PR #867: fix: minor fix to the catalog utils. 
* PR #866: feat: app testing 
* PR #864: test: support for testing apps 
* PR #860: Summary :  'progressive' filter while downloding streams in youtube_qa app. 
* PR #861: feat: add chunk_size and chunk_overlap similar to langchain 
* PR #859: ci: Macos build 
* PR #853: feat: chatgpt test with real API key 
* PR #858: Bump v0.2.12+dev 

##  [0.2.11] - 2023-06-10

* PR #856: Bump v0.2.11+dev 
* PR #855: Release 0.2.10 
* PR #854: fix: update sentence transformer udf 

##  [0.2.10] - 2023-06-10

* PR #852: feat: optional import of decord, fix for sentence feature extractor 
* PR #851: Bump v0.2.10+dev 

##  [0.2.9] - 2023-06-09

* PR #849: app: add a text and mp4 file 
* PR #833: app: Youtube qa app now supports long videos 
* PR #848: app: minor updates 
* PR #847: app: minor updates to privateGPT app 
* PR #841: app: private gpt 
* PR #845: docs: Index.rst docs 
* PR #844: Bump v0.2.9+dev 

##  [0.2.8] - 2023-06-09

* PR #842: docs: add pdf qa picture 
* PR #840: docs: update docs 
* PR #839: docs: updates 
* PR #838: Summary : Added missing API documentation 
* PR #834: refactor: move 'EVA' to 'EvaDB' 
* PR #814: feat: benchmark question answering v1 
* PR #831: Bump v0.2.8+dev 
* PR #819: feat: update tutorials to use Python API 

##  [0.2.7] - 2023-06-07

* PR #819: feat: update tutorials to use Python API 
* PR #828: feat: drop index 
* PR #830: docs: updating docs based on Python API 
* PR #826: fix: orderby bug 
* PR #821: feat: adding python API drop and drop_udf 
* PR #810: feat: grouping paragraphs in documents and samples in audio 
* PR #800: test: api testing  -> similarity between text and relevance keyword 
* PR #818: fix: update youtube qa app with new api updates 
* PR #803: feat: saliency maps 
* PR #815: chore
* PR #816: docs: renamed apis 
* PR #804: feat: create udf interface for pythonic api 
* PR #813: feat: Expose apis 
* PR #795: Import config should persist nothing 
* PR #808: Bump v0.2.7+dev 

##  [0.2.6] - 2023-06-02

* PR #807: Bump v0.2.6+dev 

##  [0.2.5] - 2023-06-02

* PR #801: feat / doc: example app that summarizes any youtube video with Python api 
* PR #796: docs: Updating Docs based on feedback 
* PR #787: feat: enable ray by default 
* PR #777: feat: Hugging face entity extraction 
* PR #789: feat: create table from select query 
* PR #794: docs: bump python for docs 
* PR #793: refactor: Create .git-blame-ignore-revs  
* PR #784: feat: support relational apis 
* PR #774: Improve create mat 
* PR #785: fix: update mnist notebook 
* PR #781: docs: minor updates 
* PR #780: feat: add mnistCNN as builtin udf 
* PR #779: docs: many minor updates 
* PR #776: docs: update getting started page 
* PR #775: docs: style updates 
* PR #773: fix: gracefully handle missing config values 
* PR #771: chore: improve logging of error messages  
* PR #768: feat: create materialized view infers column name 
* PR #770: tutorials: hugging face text summarizer, text classifier, + pdf loader 
* PR #769: feat: load pdf 
* PR #767: ci: improve docker support 
* PR #751: feat: integration with langchain 
* PR #764: feat: db apis made more pythonic 
* PR #765: test: fix test case 
* PR #753: chore
* PR #748: feat: common image transformation UDFs 
* PR #731: feat: extensible parallel execution 
* PR #750: release: automating the release script 
* PR #745: fix docs build 
* PR #744: docs: fix links 
* PR #743: fix: hot fix for similarity notebook 
* PR #700: docs: similarity search tutorial 
* PR #741: docs: test links in documentation with linkcheck 
* PR #740: docs: minor updates to read-the-docs 
* PR #707: feat: add support for third party vector stores 
* PR #738: feat: allow users to specify host and port while launching server 
* PR #733: docs: enable spellcheck on all python files, notebooks, and docs  
* PR #566: feat: object tracking 
* PR #720: fix: similarity test 
* PR #726: ci: bump up oldest python version from 3.7 to 3.8 
* PR #729: docs: update notebooks on landing page 
* PR #724: release: Bump v0.2.3+dev 

##  [0.2.4] - 2023-05-17
### [Added]

* PR #700: docs: similarity search tutorial 
* PR #741: docs: test links in documentation with linkcheck 
* PR #707: feat: add support for third party vector stores 
* PR #738: feat: allow users to specify host and port while launching server 
* PR #733: docs: enable spellcheck on all python files, notebooks, and docs  
* PR #566: feat: object tracking 
* PR #720: fix: similarity test 
* PR #726: ci: bump up oldest python version from 3.7 to 3.8 

### [Changed]

* PR #740: docs: minor updates to read-the-docs 
* PR #729: docs: update notebooks on landing page

##  [0.2.3] - 2023-05-11
### [Added]

* PR #708: tutorial: toxicity classifier
* PR #694: tutorials: ChatGPT + Whisper + Hugging Face tutorial notebook  
* PR #690: feat: make keywords case insensitive in parser 
* PR #679: feat: support for Yolov8 pipelines 
* PR #676: fix: Enable image and video tables to project Identifier column 
* PR #663: feat: add caching support for udfs in projection 
* PR #659: feat: Add support for audio based hf models 
* PR #655: feat: LLM-based remote UDFs -- support for OpenAI Chat Completion 
* PR #651: tutorial: license plate detection notebook to demonstrate fuzzy join  
* PR #645: feat: logical filter cache 
* PR #644: chore: Add optimizer timeout 
* PR #643: feat: Add audio sampling rate

### [Changed]

* PR #712: fix: image loading 
* PR #719: fix: speed up testcases 
* PR #717: ci: updates to ci pipeline 
* PR #718: bug: move from yolo to HF for reuse testcases 
* PR #711: docs: Update README.md / typo fix 
* PR #706: bug: catalog reset  
* PR #704: test: add message to help debug an issue 
* PR #701: bug: modify the catalog reset method  
* PR #702: fix: stop raising error if category or key missing in config. 
* PR #698: docs: improve UDF creation documentation 
* PR #699: chore: rename ChatGPT UDF 
* PR #696: docs: updated UDF documentation based on decorators 
* PR #697: misc: add github templates 
* PR #695: docs: typo in executor_utils.py 
* PR #691: fix: cache indices after filtering 
* PR #689: style: removing gender detection nb 
* PR #686: ci: reduce number of cache shards 
* PR #687: docs: Add link to HuggingFace demo application -- image segmentation pipeline 
* PR #684: ci: upgrades to ci pipeline 
* PR #681: ci: add model cache for linux builds 
* PR #678: fix: HF GPU support 
* PR #675: bug: opencv now returns rgb 
* PR #674: fix: ray ci fix 


##  [0.2.1] - 2023-04-25
### [Added]

* PR #664: Add Tutorial Notebook for HuggingFace 
* PR #668: fix: Remove detoxify to fix pip install evadb 
* PR #660: Bump Eva-Decord to Not Need ffmpeg 
* PR #657: docs: benefit of caching and predicate reordering 

##  [0.2.0] - 2023-04-16
### [Added]

* PR #647: feat: LOAD CSV Notebook 
* PR #626: docs: Documentation for creating UDFs using Decorators. 
* PR #599: feat: EvaDB x HuggingFace 
* PR #621: feat: Ray integration

### [Changed]

* PR #649: fix: Expr bugs 
* PR #628: test: adding support for pytest-xdist 
* PR #633: fix: Install Decord from EvaDB-Fork 
* PR #642: Build fix 
* PR #641: fix: Unnest bug  

##  [0.1.6] - 2023-04-05
### [Added]

### [Changed]

* PR #636: fix: Timeout Error #636 
* PR #635: fix: updates to restore build
* PR #634: fix: Pandas deprecated append call
* PR #632: fix: Minor code refactor

##  [0.1.5] - 2023-04-03
### [Added]

* PR #623: feat: Adding support for AudioStorageEngine 
* PR #550: feat: support key-value cache for function expressions 
* PR #604: feat: LIKE operator  
* PR #622: feat: sqlalchemy tests 
* PR #618: feat: Predicate UDF Reordering Optimization 
* PR #617: feat: Add UDF Cost Catalog 
* PR #616: feat: Add support for iframe based video sampling 
* PR #606: feat: Add metadata to UDFs in catalog 
* PR #589: feat: Fuzzy Join support in EvaDB 
* PR #601: feat: Decorators for UDF 
* PR #619: chore: reducing coverage loss 
* PR #595: doc: Adding CatalogManager, INSERT and DELETE documentation 
* PR #605: feat: verify udf consistency by matching the file checksum 
* PR #600: feat: allow UDF's to be created with any name 
* PR #583: feat: Add symlinks to data files instead of copying 
* PR #580: feat: enable loading videos from s3 
* PR #587: feat: Delete and Insert operators for structured data 
* PR #582: server: asyncio refactoring 
* PR #579: fix: directory of eva-arch 
* PR #578: docs: update project name 

### [Changed]

* PR #581: fix: debugging issuse in yolov5
* PR #625: Bug: Reader fixes 
* PR #611: fix: insert and delete executor 
* PR #615: fix: dropbox links fixed  
* PR #614: Fix: updated dropbox links 
* PR #602: fix: EvaDB on Ray bugs 
* PR #596: fix: Raise Error on Missing Files during Load 
* PR #593: fix: Windows path error in S3 testcases 
* PR #584: Rename Array_Count to ArrayCount 
* PR #581: fix: debugging issue in yolov5 

### [Deprecated]

* PR #609: refactor: removing upload code and bug fixes 

### [Removed]

##  [0.1.4] - 2023-01-28
### [Added]

* PR #559: Added Order By + Limit to FaissIndexScan optimization rule.
* PR #552: Added expression signature.
* PR #551: Added support for aggregation, toxicity detection, and querying based on video timestamps.
* PR #557: Update documentation for notebook.
* PR #562: Added benchmark and server tests.
* PR #565: Updated rule and expression implementations.
* PR #560: Added UDF for ASL recognition.

### [Changed]

* PR #558: fix: emotion analysis colab link.
* PR #561: fix: Circlie CI error.
* PR #553: fix: secondary index and udf expression signature in index.

### [Deprecated]

### [Removed]

##  [0.1.3] - 2023-01-02
### [Added]

* PR #506: Added support for windows and macos
* PR #492: Moved to a lark-based parser
* PR #536: Lateral function call to linear data flow
* PR #535: Similarity UDF

### [Changed]

* PR #544: fix: catalog improved file and function names
* PR #543: fix: server relaunch does not load metadata tables

### [Deprecated]

### [Removed]

## [0.1.2] - 2022-12-17
### [Added]

* PR #533: feat: load img support 
* PR #514: feat: Add support open command 
* PR #513: feat: Load regex support
* PR #508: feat: Yolov5 Object detector UDF 
* PR #505: fix: support multiple evadb version. 
* PR #477: feat: Load syntax change

## [0.1.1] - 2022-11-20
### [Added]

* PR #498: docs: more details
* PR #495: docs: improve read-the-docs 
* PR #488: docs: fix notebooks
* PR #486: docs: update notebooks + banner
* PR #476: feat: GPU Jenkins support

## [0.1.0] - 2022-11-12
### [Added]

* PR #474: feat: Support for action queries in Eva 
* PR #472: feat: Replace Json with Pickle Serialization
* PR #462: ci: Enable GPU support for Jenkins CI
* PR #454: docs: adding gifs to readme 
* PR #445: feat: Replace Spark+Petastorm with Sqlite+SqlAlchemy
* PR #444: feat: Explain command support
* PR #426: feat: Simplify PytorchAbstractClassifierUDF interface

### [Removed]
* PR #445: feat: Replace Spark+Petastorm with Sqlite+SqlAlchemy

## [0.0.12] - 2022-10-18
### [Added]

* PR #424: Jenkins CI
* PR #432: Emotion palette notebook
* PR #419: Updated Dockerfile
* PR #407: Movie analysis notebook
* PR #404: feat: Lateral join + sampling
* PR #393: feat: EvaDB config updates

### [Contributors]

Thanks to @gaurav274, @xzdandy, @LordDarkula, @jarulraj, @Anirudh58, @Aryan-Rajoria for contributions!

## [0.0.10] - 2022-09-22
### [Added]

* PR #373: Reduce number of file transactions in configuration (#373)
* PR #372: bugfix: Make ConfigurationManager read and update operate on eva.yml (#372)
* PR #367: Dataset support (#367)
* PR #362: Automatically adding Tutorial Notebooks to docs (#362) 
* PR #359: Layout for EvaDB Documentation (#359)
* PR #355: docs: Adding instructions for setup on M1 Mac (#355)
* PR #344: Updated the tutorial notebooks (#344)
* PR #342: Support for NOT NULL (#342)
* PR #340: Tutorial: Gender analysis (#340) 
* PR #339: Bug: Fix CROP UDF (#339) 
* PR #334: bug: fix face detector (#334)
* PR #331: Simplify Environment Configuration  
* PR #316: feat: Predicate Pushdown across join and Fix Materialization Bugs

### [Contributors]

Thanks to @gaurav274, @jarulraj, @xzdandy, @LordDarkula, @Anirudh58, @Aryan-Rajoria, @adarsh2397, and @IshSiva for contributions!

## [0.0.9] - 2022-08-13
### [Added]

* PR #323: Fix EvaDB Configuration
* PR #321: CI: Caching dependencies
* PR #315: Unified load 
* PR #313: Logo update
* PR #309: UNNEST operator
* PR #307: Feature extractor UDF
* PR #303: Face detector and OCR extractor UDFs

### [Contributors]

Thanks to @gaurav274, @jarulraj, @xzdandy, @LordDarkula, @eloyekunle, and @devshreebharatia for contributions!

## [0.0.6] - 2022-08-05
### [Added]

* PR #295: Improve Error Messages and Query responses 
* PR #292: Updating read the docs + website
* PR #288: Update README.md


## [0.0.3] - 2022-07-31
### [Added]

* PR #283: Updated README
* PR #278: Updated development guide
* PR #275: Updated setup.py
* PR #273: Predicate pushdown for video table
* PR #272: Add support for DROP and SHOW UDFs
* PR #262: Error message enhancement
* PR #276: Website updates
* PR #257: Interpreter updates

### [Contributors]

Thanks to @gaurav274, @jarulraj, @xzdandy, @EDGAhab, and @kaushikravichandran for contributions!

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

##  [Unreleased]
### [Added]
### [Changed]
### [Deprecated]
### [Removed]


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
* PR #727: docs: "recogizing" in index.rst 
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
* PR #599: feat: EVA x HuggingFace 
* PR #621: feat: Ray integration

### [Changed]

* PR #649: fix: Expr bugs 
* PR #628: test: adding support for pytest-xdist 
* PR #633: fix: Install Decord from EVA-Fork 
* PR #646: update doc for extending eva 
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
* PR #589: feat: Fuzzy Join support in EVA 
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
* PR #602: fix: EVA on Ray bugs 
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
* PR #393: feat: EVA config updates

### [Contributors]

Thanks to @gaurav274, @xzdandy, @LordDarkula, @jarulraj, @Anirudh58, @Aryan-Rajoria for contributions!

## [0.0.10] - 2022-09-22
### [Added]

* PR #373: Reduce number of file transactions in configuration (#373)
* PR #372: bugfix: Make ConfigurationManager read and update operate on eva.yml (#372)
* PR #367: Dataset support (#367)
* PR #362: Automatically adding Tutorial Notebooks to docs (#362) 
* PR #359: Layout for EVA Documentation (#359)
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

* PR #323: Fix EVA Configuration
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

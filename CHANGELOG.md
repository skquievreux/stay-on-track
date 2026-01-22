## [1.4.2](https://github.com/skquievreux/stay-on-track/compare/v1.4.1...v1.4.2) (2026-01-18)


### Bug Fixes

* combine release and build steps in single workflow to ensure asset upload ([61303b9](https://github.com/skquievreux/stay-on-track/commit/61303b9c82272f302b1727a393b8f1c27be63b2c))

## [1.4.1](https://github.com/skquievreux/stay-on-track/compare/v1.4.0...v1.4.1) (2026-01-18)


### Bug Fixes

* resolve module import error by using absolute path and add EXE metadata ([4df2f87](https://github.com/skquievreux/stay-on-track/commit/4df2f87986d16143e0d96f2afa2ceff1983e72b3))

# [1.4.0](https://github.com/skquievreux/stay-on-track/compare/v1.3.1...v1.4.0) (2026-01-18)


### Bug Fixes

* prevent multiple instances application-wide and streamline installer process ([e70690f](https://github.com/skquievreux/stay-on-track/commit/e70690fb4573467ff44c141ebc91137ebe7c9151))


### Features

* Automate version injection into Inno Setup installer and Python `version.py` via semantic-release. ([f4acd9e](https://github.com/skquievreux/stay-on-track/commit/f4acd9e7146734bd591775b0c402232eda8469ca))

## [1.3.1](https://github.com/skquievreux/stay-on-track/compare/v1.3.0...v1.3.1) (2026-01-17)


### Bug Fixes

* **ci:** use wildcard pattern for installer upload ([4d08b39](https://github.com/skquievreux/stay-on-track/commit/4d08b39dff3ada9bc99078e62ede5cdc86966968))

# [1.3.0](https://github.com/skquievreux/stay-on-track/compare/v1.2.1...v1.3.0) (2026-01-17)


### Features

* **ci:** automatically upload installer to GitHub Releases ([92f7e81](https://github.com/skquievreux/stay-on-track/commit/92f7e818460db165893f8923a322246b752d5158))

## [1.2.1](https://github.com/skquievreux/stay-on-track/compare/v1.2.0...v1.2.1) (2026-01-17)


### Bug Fixes

* **ci:** fix artifact upload path using wildcard ([cf6f348](https://github.com/skquievreux/stay-on-track/commit/cf6f348cbc5faec0aa9fc028d4cc22fc0bf1631f))

# [1.2.0](https://github.com/skquievreux/stay-on-track/compare/v1.1.0...v1.2.0) (2026-01-17)


### Features

* professional installer with Quievreux Consulting branding ([9134fa8](https://github.com/skquievreux/stay-on-track/commit/9134fa8b987adb361f056777ec00fe4d985a4a68))

# [1.1.0](https://github.com/skquievreux/stay-on-track/compare/v1.0.2...v1.1.0) (2026-01-17)


### Bug Fixes

* **build:** improve PyInstaller configuration for customtkinter ([4df6a7e](https://github.com/skquievreux/stay-on-track/commit/4df6a7ef3dd9b5b7450702e181b0b16b93fcce0d))
* **ci:** add GitHub permissions for semantic-release ([7976f62](https://github.com/skquievreux/stay-on-track/commit/7976f626a0289e19d0772fdc786c23b68699292f))
* **ci:** add missing pyinstaller and pylint dependencies ([126217b](https://github.com/skquievreux/stay-on-track/commit/126217b7513fa1d3e9b8bbb4a3b4868eca892e5d))
* **ci:** disable Poetry cache until poetry.lock is generated ([da123ef](https://github.com/skquievreux/stay-on-track/commit/da123ef5881f196e3cc7dfcc58595b3446fc5fbd))
* **ci:** relax pylint checks to allow build to proceed ([8b4f513](https://github.com/skquievreux/stay-on-track/commit/8b4f513547c4eee2e7500b164cb11726464a5fe3))
* **deps:** add dill dependency for pylint ([35e1a0a](https://github.com/skquievreux/stay-on-track/commit/35e1a0ae27ac8c6e288ca8d2e3e654d8c1b9f628))
* **deps:** constrain Python version to <3.13 for PyInstaller compatibility ([1e61a47](https://github.com/skquievreux/stay-on-track/commit/1e61a47df919ed36d8f02f059b5c8d1bd633e777))


### Features

* **analytics:** add multi-day analytics dashboard with date navigation ([4b70885](https://github.com/skquievreux/stay-on-track/commit/4b70885f1a390ec23a4c20d16368de6550820183)), closes [#1](https://github.com/skquievreux/stay-on-track/issues/1) [#2](https://github.com/skquievreux/stay-on-track/issues/2) [#3](https://github.com/skquievreux/stay-on-track/issues/3)
* **clustering:** add activity categorization with auto-learning ([bf07065](https://github.com/skquievreux/stay-on-track/commit/bf07065a34ac7cc5a118d40d69e35324d374428a))

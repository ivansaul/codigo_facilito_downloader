# CHANGELOG

## v0.1.0 (2024-11-23)

### Chore

* chore: disable upload to PyPI by setting `upload_to_pypi` to false ([`2d93def`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2d93def8b110228cb0f81d37de0e827ac551002d))

* chore: update version to 0.5 to reflect the current release state ([`a93e140`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a93e1404d18c89f682515676529285b2f1d376c5))

* chore: updates dependencies and settings ([`0798799`](https://github.com/ivansaul/codigo_facilito_downloader/commit/07987993949c044d11078ed1ea0cc49ca4ebe7f5))

* chore: move unit type detection logic to utils.py ([`0504482`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0504482384aadd6a214e48ea1e9c27f3a59b1d1a))

* chore: updates dependencies

Update various dependencies to newer versions, add  tools for code quality, testing, debugging and introduces colorlog, unidecode, and playwright-stealth ([`50cbd5b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/50cbd5b9dfe9a2b769b845a53bc88bc83bd1d79a))

* chore: improve unit tests helper functions

Adds tests for `clean_string`, `hashify`, and `slugify` functions. ([`1793045`](https://github.com/ivansaul/codigo_facilito_downloader/commit/17930457a3d530e59ea2607f2ebb17b47266f3a4))

* chore: improve collectors functions

Implements asynchronous functions for fetching course, unit, and video data from the Facilito platform. ([`97dd66c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/97dd66cf393e06405fc6b7d0c79abd1879a11855))

* chore: improve configuration constants for Facilito app

Add necessary constants for the Facilito application, including URLs for different endpoints and the session directory. ([`56ce594`](https://github.com/ivansaul/codigo_facilito_downloader/commit/56ce594133b814cb28e2d4a2e24a7cc9f7acae4f))

* chore: improve utility functions

Add functions for handling login, asynchronous requests, saving and loading browser state, progressive scrolling, and saving web pages as mhtml. ([`f6808f0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f6808f0fd4097d46341ace6f8f932047f750ffaf))

* chore: improve custom error classes for facilito

Introduces a hierarchy of custom error classes (BaseError, LoginError, VideoError, UnitError, CourseError) for improved error handling and clarity. ([`c1ca651`](https://github.com/ivansaul/codigo_facilito_downloader/commit/c1ca6512b613ebc994e23d1463da8fc5a5f79095))

* chore: improve resource models for facilito

Add models for `Resource`, `Video`, `Lecture`, `Unit`, `Chapter`, and `Course` to represent facilito resources.
Includes `Quality` and `TypeUnit` enums for better data organization. ([`f79a16f`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f79a16fb09e7a9abd78d4d4bbbd5bfb260dec770))

* chore: improves helper functions

Improves helper functions for better readability and maintainability, replaces legacy functions with cleaner alternatives and removes redundant comments and unused code. ([`5c89b1b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5c89b1bab506cb234eaeda9e22e5d8dba8e00b4c))

* chore: improve logging functionality with color formatting ([`1c198d3`](https://github.com/ivansaul/codigo_facilito_downloader/commit/1c198d399e968890fb42865f6ce1744527bd7963))

* chore: delete all previous files and reset project structure ([`a65cbd4`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a65cbd490e1648eaf93a1339bab1a9241fe9ce5b))

* chore: add bug-report and request-feature markdown templates ([`4aab76f`](https://github.com/ivansaul/codigo_facilito_downloader/commit/4aab76fae25441e047d08a6ab4138cc241e9f40b))

* chore(vscode): add spanish spell checker ([`506d894`](https://github.com/ivansaul/codigo_facilito_downloader/commit/506d894fab6fcc9f4407865ec3c249d02ce670af))

* chore(vscode): add extension.json

added recomendations extensions ([`53011c5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/53011c5a05f73371b055cd3e2a5afa56a3af1ffc))

* chore: add pre-commit config file ([`af58b89`](https://github.com/ivansaul/codigo_facilito_downloader/commit/af58b899e2f20db39b3e7136f49bf112d7789650))

* chore: remove requirements.txt ([`a7e97ba`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a7e97ba524e7da2e9c139815dcb965ab8bc934d8))

* chore: change version in pyproject.toml

-  change from 0.1.0 to 0.5.0 ([`abb2fd9`](https://github.com/ivansaul/codigo_facilito_downloader/commit/abb2fd94d4c30b4fdf3c1f1c0b4deae2993c254a))

* chore: add .vscode  to git tracking ([`5b6a0b1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5b6a0b192c255b77595e82437c49f486f7b774e1))

* chore: integrate Poetry for dependency management ([`a65dca2`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a65dca2937da14bd95b132facb7cf4d5c8899d65))

* chore(git): stop tracking cookies.txt ([`399d181`](https://github.com/ivansaul/codigo_facilito_downloader/commit/399d181f69964daa300b6f473d9eadcc3afa2f67))

### Documentation

* docs: update installation instructions to use GitHub instead of PyPI ([`08711c1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/08711c11843323264cda951bd889f9b341687977))

* docs(readme): remove cheat-sheets testing banner ([`e39524c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/e39524cf4a925fb036c903b5d82306f9e2088ca6))

* docs(readme): add cheat-sheets testing banner ([`8dd68c5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/8dd68c5001019005d3a37a9fb4dc67d1177b85e2))

* docs(readme): fix scoop python installation command ([`0cc8f63`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0cc8f63047305cbf37780299f60c4749a679c5ac))

* docs(readme): update instructions and fix typo

- add instructions to install git
- add important quote for update repo ([`554511d`](https://github.com/ivansaul/codigo_facilito_downloader/commit/554511dc2a2996e928d17afc574b88c209127c5d))

* docs(readme): update windows important quote

- added scoop youtube tutorial link ([`69671c7`](https://github.com/ivansaul/codigo_facilito_downloader/commit/69671c72909750007ad43fd4b953a95115ee2cc5))

* docs(readme): update header readme

- change repo banner image
- add demo.gif ([`432c26b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/432c26b9a0401399b80d7983307a3fe88ebfbfa4))

* docs(readme): update readme

- add playwright deps install instructions
- add output download command example ([`771b62e`](https://github.com/ivansaul/codigo_facilito_downloader/commit/771b62e2909c0d39874599f3b3293e4695104221))

* docs(readme): improve code block formatting

Updated code block from &#39;```bash&#39; to &#39;```console&#39; for better rendering. ([`96b7473`](https://github.com/ivansaul/codigo_facilito_downloader/commit/96b7473360140838d050f2fba63394fd15fbf80a))

* docs(readme): fix formatting in [!IMPORTANT] ([`2d24522`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2d24522a8941b3068d8406b8aefee712e04f9c9d))

* docs: update README

- add important blockquote ([`140b28f`](https://github.com/ivansaul/codigo_facilito_downloader/commit/140b28f8b7768b68b18bedee6359e5e812632a6b))

* docs: update README with new github blockquotes ([`0a7040e`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0a7040ed209baaf75e267f7b78b9602b46eb6317))

* docs: fix Discord channel link ([`636c7a0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/636c7a071131826c3af836a65c4e2a55255cd567))

* docs: update README with maintenance notice ([`5227962`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5227962547795dd22b74de9b0045e2ad3a61829c))

### Feature

* feat: add thread control to downloaders

Improve download performance by introducing a configurable number of threads. Allows users to control the number of concurrent downloads from 1 to 16. ([`37d4fb1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/37d4fb17e522179ee7bd015ae0b70166f15f0442))

* feat: add source.mhtml file downloading for courses ([`6624bb2`](https://github.com/ivansaul/codigo_facilito_downloader/commit/6624bb2b3c7ee5254756c6920b7e932e8d5b9f11))

* feat: adds CI/CD pipeline for automated releases

Adds GitHub Actions workflows for testing and releasing packages, Integrates semantic-release for automated versioning and PyPI uploads. ([`2931277`](https://github.com/ivansaul/codigo_facilito_downloader/commit/293127753759b965292e9ea37d88e3143a185c00))

* feat: add CLI commands for facilito

Implements `login`, `logout`, and `download` commands for interacting with the facilito API.
These commands provide a command-line interface for common tasks. ([`86c9a21`](https://github.com/ivansaul/codigo_facilito_downloader/commit/86c9a21ab7a11a388bae55d1da4042c226be1fac))

* feat: add video downloader and course downloader functionality ([`a39ef49`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a39ef491716ba528c6bcb4073564a9d714400ece))

* feat: Add AsyncFacilito API class

Implements an asynchronous API class for interacting with the Facilito platform, using Playwright for browser automation. Includes methods for login, fetching units and courses, and handling authentication. ([`30af9ba`](https://github.com/ivansaul/codigo_facilito_downloader/commit/30af9baf4a40aeb5e94196eb9f9bc73282bda85c))

* feat: add default prefix to sections title ([`bd76d0c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/bd76d0c4f6876d784f4f9737ca5d00cc65e74507))

* feat: add prefix_name argument to video.download() method ([`9964c65`](https://github.com/ivansaul/codigo_facilito_downloader/commit/9964c65099e7c5642ea52542f81335871e6611c8))

* feat(cli): updete download command

- implement download course by url
- add headless mode option ([`99122cf`](https://github.com/ivansaul/codigo_facilito_downloader/commit/99122cfb6fb6e35dd83499891e668c8743b9da07))

* feat: add new logger(cli_logger) ([`64ae708`](https://github.com/ivansaul/codigo_facilito_downloader/commit/64ae708cad4467534a1cae60ebed6d5aa4ddcfac))

### Fix

* fix: course fetching

Add handling to expand all course chapters ([`b13c639`](https://github.com/ivansaul/codigo_facilito_downloader/commit/b13c639d2fd7141a90fc1f9d2aeb91c3fa4bd04f))

* fix: helper is_ffmpeg_installed()

- was caching wrong exception ([`f98b041`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f98b041ae38c6d00dc2a150937aded162a0e09e3))

### Refactor

* refactor: remove unnecessary file ([`0de0d07`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0de0d073f6a65d0834e9a926d2c5ac2e106da6a9))

* refactor: WIP update multiple files ([`c0d99f5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/c0d99f537c84c5327c1a83b6b35f35d8c9c491fa))

* refactor: remove unnecessary files ([`d946bb4`](https://github.com/ivansaul/codigo_facilito_downloader/commit/d946bb4de0b665f833cc20f41acfada203c9b496))

* refactor: WIP add test ([`5d8f7a6`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5d8f7a6f2c6d7cbd7d7228e14a52559a5afa972d))

* refactor: WIP rewrite code ([`e555880`](https://github.com/ivansaul/codigo_facilito_downloader/commit/e555880e60f592944df0ab41daf403d89e0cdf2d))

* refactor: migrate to Playwright(WIP) ([`2985a44`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2985a44caa9c1cd173ec87859a19d6060f36d58f))

* refactor: migrate to Playwright(WIP) ([`14f3b7a`](https://github.com/ivansaul/codigo_facilito_downloader/commit/14f3b7a0d22f09a507c6c7281db8f56721d11468))

### Style

* style(format): apply style formatting with Black.

- run all pre-commits. ([`cefaa66`](https://github.com/ivansaul/codigo_facilito_downloader/commit/cefaa66a80430ee616c7cd00b3664531ba908463))

### Unknown

* Merge pull request #44 from ivansaul/refactor

refactor: add asynchronous api ([`d6d7d91`](https://github.com/ivansaul/codigo_facilito_downloader/commit/d6d7d91a3dc6a8c4242574b2a86f7d52aad31cb3))

* update README with updated installation and usage instructions. ([`2627e64`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2627e64a2a0581bd062799bf8ec36064764e996f))

* Merge pull request #33 from ivansaul/pre-commit-ci-update-config

[pre-commit.ci] pre-commit autoupdate ([`9062ca9`](https://github.com/ivansaul/codigo_facilito_downloader/commit/9062ca92c1a45b8e4a89de63f85cfb47280efa59))

* [pre-commit.ci] pre-commit autoupdate

updates:
- [github.com/pre-commit/pre-commit-hooks: v2.3.0 → v4.5.0](https://github.com/pre-commit/pre-commit-hooks/compare/v2.3.0...v4.5.0)
- [github.com/pycqa/isort: 5.12.0 → 5.13.2](https://github.com/pycqa/isort/compare/5.12.0...5.13.2)
- [github.com/hadialqattan/pycln: v2.3.0 → v2.4.0](https://github.com/hadialqattan/pycln/compare/v2.3.0...v2.4.0) ([`9722812`](https://github.com/ivansaul/codigo_facilito_downloader/commit/972281260cc9d22bfec61eb7f476186d1be4918f))

* Merge pull request #32 from Ronald3217/fix/multi-input

fix(collectors):   locator find multiple elements with course_id name ([`597648e`](https://github.com/ivansaul/codigo_facilito_downloader/commit/597648e56c7c54e206c5c632c047b75669bae0ff))

* FIX: Error finding multiple elements

Error when finding multiple elements with the id &#34;course_id&#34; is fixed ([`f9a84a5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f9a84a505c35eed4996a9e34a2b59fcd6f8d68e7))

* Merge branch &#39;rewrite&#39; v.0.5.0 ([`7a39af0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/7a39af01b91f92b6dc5333a37be3bf6ce4412479))

* doc: update readme ([`acbe5ad`](https://github.com/ivansaul/codigo_facilito_downloader/commit/acbe5ad7094b2e01e0d9da99c3598e3b092773d5))

* rename src files ([`1673af5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/1673af50a703cd2dead355cf82cced2ad64b6f37))

* WIP: add docstrings ([`4c45da7`](https://github.com/ivansaul/codigo_facilito_downloader/commit/4c45da7678d809844d2364eb3a4a7282135ecc2c))

* Merge pull request #29 from Ronald3217/master

FEAT: Descargar en lote ([`8766800`](https://github.com/ivansaul/codigo_facilito_downloader/commit/87668000275c6e3efcd3e299b5a4df5af7e00ceb))

* FEAT: Descargar en lote

Se agrega la funcion para descargar en lote, Leer README.md ([`c7071ad`](https://github.com/ivansaul/codigo_facilito_downloader/commit/c7071adf5e92d37db1c172e91ba13189269a75eb))

* Merge branch &#39;master&#39; of github.com:ivansaul/codigo_facilito_downloader ([`3f0265b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/3f0265b6e02a33345fa30f14d7f0a14c3e396c1e))

* set number of threads for yt-dlp ([`874878c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/874878c982f60372e3fd135591d42bd09fc5f706))

* Merge pull request #19 from Ronald3217/master

FEAT:  Obtener info del bootcamp ([`ed29079`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ed290792ca3ea607905f2fc5d1d9069d9d3c6b5d))

* FEAT:  Obtener info del bootcamp

Obtener la información del bootcamp, y almacenarla en &#34;bootcamp.json&#34; ([`0f373c1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0f373c141d806d8f906f59e9a8b5cdb7a2f268c2))

* remove demo ([`df7d6c8`](https://github.com/ivansaul/codigo_facilito_downloader/commit/df7d6c8f357f1cd2d912010254ca5afe7cac5437))

* implement FacilitoCookies ([`19daacf`](https://github.com/ivansaul/codigo_facilito_downloader/commit/19daacf879074581e22f170577edb5f8551c6a72))

* implement FacilitoCookies ([`809df90`](https://github.com/ivansaul/codigo_facilito_downloader/commit/809df903f4d07240579b8d8fb6872bc59b4d32e0))

* update readme ([`5fc09e5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5fc09e5b61435e8a685f973e2583674a0edad055))

* update readme ([`d8eb634`](https://github.com/ivansaul/codigo_facilito_downloader/commit/d8eb63486634d05174deff2db396fccc0b0c6f1e))

* implement quality, external_dowloader selections options ([`2892d43`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2892d435b89c9e818b5271c2cbc4ab2f2d0540f8))

* add click package ([`ffe14dc`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ffe14dc4656135d9c110e9261a1f2cc5f2cd423d))

* fix -&gt; remove all empty videos and articles ([`1821c7c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/1821c7cef68c4ff9ecfee5bdf60b0d79641086d0))

* move check aria2 and geckodriver to utils ([`82498d0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/82498d076aa596fd307c816e03978b4b17ef05f3))

* add &#39;articulos&#39; conditional checker ([`a887ab0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a887ab0214e5adff54e5252267de772da3608ba7))

* add encoding utf-8 ([`4c88d77`](https://github.com/ivansaul/codigo_facilito_downloader/commit/4c88d7738630e3a483d7a18708c8e178f698121a))

* implement input_credentials utils ([`86c9def`](https://github.com/ivansaul/codigo_facilito_downloader/commit/86c9def3b621854d07b2ebe330487aa9b389cf2d))

* Update README.md ([`49ba1f9`](https://github.com/ivansaul/codigo_facilito_downloader/commit/49ba1f960c315d393b89455922c402874f3b9a93))

* fix local_driver_path in check_aria2 method ([`b52c721`](https://github.com/ivansaul/codigo_facilito_downloader/commit/b52c721fab0ad70c79f9d055eb773557e4906bc9))

* implement check_aria2() method ([`f0bfcd6`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f0bfcd6b9ce7dd2779b99470483c82dae9cdb85d))

* extract release version to variable &#34;release&#34; ([`3e25bc1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/3e25bc1672694dfb24b7a1c5c5e9969ff416c7a3))

* update readme ([`ad379a2`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ad379a2ba0bc4ca4c05e96ea6923763a01862ce3))

* set headless to True ([`f137b0c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f137b0c6afae0de9cb6192285a4149b7540f0628))

* add support for win and mac ([`5049167`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5049167c5eaacf0405aadb4d2c0dee81703dc3a3))

* Update README.md ([`f24910d`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f24910dd2572bcb3cbcb24bcc56fcc5afb80a59b))

* Update README.md ([`d426bb2`](https://github.com/ivansaul/codigo_facilito_downloader/commit/d426bb28ba53b3ded043611710cf2e344052e18a))

* fix -&gt; remove pop up promo banner ([`06c3fea`](https://github.com/ivansaul/codigo_facilito_downloader/commit/06c3feacdd52d70ab41ee983b55b490a213490f2))

* fix -&gt; remove pop up promo banner ([`ff9722d`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ff9722dbd843f9a685072279bc5e0a6f01b5bfa6))

* Update README.md ([`9b85dbd`](https://github.com/ivansaul/codigo_facilito_downloader/commit/9b85dbd472558b8b0c05d3966f85d8fef8cdbdbc))

* Update README.md ([`e45b23c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/e45b23cb2a464ee5e49567e27b700e1f32a5c995))

* fix counter video name ([`c516d64`](https://github.com/ivansaul/codigo_facilito_downloader/commit/c516d64ef7930270880cce1863c8b7775e1d6b1b))

* add counter [1-&gt;n] ([`936c91d`](https://github.com/ivansaul/codigo_facilito_downloader/commit/936c91daa5c3d4735fec5f83c4bbcd2daf2d91c4))

* Update README.md ([`efbdfab`](https://github.com/ivansaul/codigo_facilito_downloader/commit/efbdfabb255efc3793dbab5e945bf3e807038871))

* Update README.md ([`88e69cc`](https://github.com/ivansaul/codigo_facilito_downloader/commit/88e69cc6a436f44a714803273dcbfaac9ad74575))

* update readme ([`f64d6f4`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f64d6f442cd390f92bc58f6dad1a0c8bbe644cbc))

* initial commit ([`14b3554`](https://github.com/ivansaul/codigo_facilito_downloader/commit/14b3554276cec4d005ff65c94bbdbc78e90075a7))

* initial commit ([`7c1a441`](https://github.com/ivansaul/codigo_facilito_downloader/commit/7c1a441ce1759410d8a6b98c670b44719a45a053))

* initial commit ([`bf3f9e3`](https://github.com/ivansaul/codigo_facilito_downloader/commit/bf3f9e378ec19869a34181cc938dd5bf563515fb))

* initial commit ([`602c18b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/602c18b29a9bb369a62787628a6f30022f37e446))

* initial commit ([`acdd065`](https://github.com/ivansaul/codigo_facilito_downloader/commit/acdd0659ee916396fd8b530f4986d9fe8baea4e6))

* initial commit ([`e85e2a7`](https://github.com/ivansaul/codigo_facilito_downloader/commit/e85e2a725d5dae9de844c3636f9a6c843fd8c04c))

* Initial commit ([`7920136`](https://github.com/ivansaul/codigo_facilito_downloader/commit/7920136ff5809f1b4039ae56c755d5b5820eabdd))

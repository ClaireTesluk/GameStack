# Third-party components

- **PyYAML**, runtime dependency (`>=6.0.2,<7`), MIT license. Upstream: https://github.com/yaml/pyyaml ; license: https://github.com/yaml/pyyaml/blob/main/LICENSE . Installed through the package manager with its own license notice; not vendored. It supplies safe YAML parsing and emission without a custom parser.
- **setuptools**, build dependency (`>=68`), MIT license. Upstream and license: https://github.com/pypa/setuptools . Not vendored; used only for Python package construction.
- **Docker Engine and Docker Compose**, externally installed host prerequisites, not redistributed by this repository. Upstream: https://github.com/moby/moby and https://github.com/docker/compose (Apache-2.0). Docker Desktop has separate terms and is not a declared hosting target.

No upstream game server, image, proprietary license, or game software is included. The example pack contains a placeholder image. Each real GamePack must document and review its own upstream terms before release.

Implementation references: [Compose up](https://docs.docker.com/reference/cli/docker/compose/up/), [Compose interpolation](https://docs.docker.com/reference/compose-file/interpolation/), [PyYAML safe loading](https://pyyaml.org/wiki/PyYAMLDocumentation).

## Standalone build components

Build tooling is pinned in `scripts/requirements-ci.txt` and is separate from runtime installation. `build` (MIT), `twine` (Apache-2.0), `packaging` (Apache-2.0/BSD-2-Clause), `wheel` (MIT), and setuptools provide packaging/validation. PyInstaller (GPL-2.0-or-later with its bootloader exception) builds standalone distributions; its hooks have their own accompanying notices. Upstream: https://pyinstaller.org/ and https://github.com/pyinstaller/pyinstaller-hooks-contrib . Python is redistributed under its included PSF license and historical notices.

Native bundles include discovered dependency license files, the interpreter's license, and the notices under `scripts/licenses`. These cover common runtime libraries which may be collected depending on OS/Python distribution: OpenSSL (Apache-2.0), zlib (zlib license), bzip2 (its BSD-style license), libffi/libyaml/Brotli (MIT), mpdecimal and Zstandard (BSD-style), and liblzma (XZ's public-domain/0BSD terms). Some notices cover optional libraries absent from a particular build. Review native dependency changes when updating build tools or Python distributions.

The vendored OpenSSL and zlib notices were fetched from upstream commits `036cbb6bbf30955abdcffaf6e52cd926d8d8ee75` and `9e35567064baded660f61732b247ef5abc809014`; XZ notices from upstream `v5.8.1`. Other runtime-library notices were copied from their installed distribution license files under `/usr/share/licenses` during initial packaging setup. Upstreams: https://openssl.org/ , https://zlib.net/ , https://sourceware.org/bzip2/ , https://tukaani.org/xz/ , https://sourceware.org/libffi/ , https://pyyaml.org/wiki/LibYAML , https://github.com/google/brotli , https://www.bytereef.org/mpdecimal/ , https://github.com/facebook/zstd . Native archives contain a build-environment package list for troubleshooting.

The Docker integration fixture uses the official nginx `stable-alpine` image pinned by manifest digest in `tests/integration/test_docker.py`. Nginx uses a BSD-2-Clause license; upstream: https://nginx.org/ . Its image includes separately licensed Alpine components. The workflow pulls this image for disposable tests and does not publish or redistribute it as a GamePack.

## Experimental Minecraft Paper GamePack — reviewed 2026-09-05

GameStack distributes its own YAML, Python integration, and original documentation.
It does **not** redistribute the container, Java runtime, Minecraft/Paper JARs,
plugins, or game assets. Users pull the unmodified image and download the server
on their own host after explicit Minecraft EULA acceptance. GameStack's AGPL license
does not grant rights to Minecraft or relicense these separate upstream programs.

The selected stack supports this external-orchestration model under the licenses
below. This is not approval to redistribute a combined server image or sell game
software. Commercial branding/packaging and a full transitive artifact review remain
release gates; no supported/sellable GamePack is claimed.

| Component | Selected version / license | Use and obligations |
|---|---|---|
| itzg/minecraft-server wrapper | Image source `82d89ee4eb5410509109c58263f2883b685f1cd8`; Apache-2.0 | External pull; retain license/NOTICE and modification notices if later redistributed or modified. [License](https://github.com/itzg/docker-minecraft-server/blob/82d89ee4eb5410509109c58263f2883b685f1cd8/LICENSE). |
| Paper | 26.2 build 121, source `a2a42c5b12249aaba42a347327fd930a1f94af06`; GPLv3 with some MIT contributions | Separate server process. GPL permits commercial use; redistribution brings source/license obligations. Do not treat selected MIT contributions as relicensing all Paper. [License](https://github.com/PaperMC/Paper/blob/a2a42c5b12249aaba42a347327fd930a1f94af06/LICENSE.md). |
| Paperclip | 3.0.4; MIT | Paper bootstrap downloads/patches upstream software; MIT does not license Minecraft itself. [License](https://github.com/PaperMC/Paperclip/blob/v3.0.4/license.txt). Version is declared by the pinned Paper build source. |
| spark (included by Paper) | 1.10.180, API 0.1-20240720.200737-2; GPLv3 | Built into upstream Paper, not an added GameStack plugin. [License](https://github.com/lucko/spark/blob/master/LICENSE.txt); exact published-artifact/transitive review remains a release gate. |
| Eclipse Temurin/OpenJDK | 25.0.4+7; GPLv2 with Classpath exception, assembly exception and separate third-party notices | Supplied inside upstream image. Inspected `/opt/java/openjdk/release` and `/opt/java/openjdk/legal/`; commercial runtime use is permitted under its terms. No Oracle proprietary JDK distribution is added. [OpenJDK legal source](https://github.com/openjdk/jdk25u/tree/master/src/java.base/share/legal). |
| mc-image-helper / mc-monitor / easy-add | 1.67.1 / 0.17.1 / 0.8.17; MIT | Upstream image tools; license/copyright preservation on redistribution. |
| mc-server-runner / rcon-cli / restify / gosu | 1.15.2 / 1.7.7 / 1.7.17 / 1.19; Apache-2.0 | Startup/shutdown and bundled utilities. RCON and optional remote services disabled; binaries remain separately licensed in upstream image. |
| Log4jPatcher | 1.0.1; MIT | Upstream bundled compatibility utility; no separate GameStack copy. |
| knock | 0.8.1; GPLv2 | Bundled upstream utility; not enabled as a GameStack networking feature. No automatic router/port-knocking setup. |
| Base-system packages | 297 installed dpkg entries; multiple licenses | Actual package/version/copyright paths and hashes recorded in inventory. Includes GPL/LGPL, Apache/MIT/BSD, font/data/documentation and other separate notices; the wrapper's license does not cover these. |

Exact version-tagged helper license URLs and text hashes are in
[packs/minecraft-paper/license-inventory.json](packs/minecraft-paper/license-inventory.json).
The registry layer digests were verified before reading the package database and
license files. Copyright symlinks were resolved. One broken OpenSSL notice link
points at obsolete `libssl3`; the inventory records the equivalent `libssl3t64`
notice from the same OpenSSL source/version. JRE legal notice paths and hashes are
also included. This inventory is not a complete dependency-level SBOM; source
copyright labels are not automatically equivalent to installed binary licensing.

The committed [upstream lock](packs/minecraft-paper/upstream-lock.json) identifies
the Linux amd64 image digest, its source/config/layer revisions, Paper build and
artifact checksum. No floating game version/build is used by the pack. Keep license
review and compatibility checks coupled to any future pin change.

### Minecraft terms and presentation

Minecraft is proprietary. Its [EULA](https://www.minecraft.net/en-us/eula) allows
third-party tools/services subject to its terms and prohibits unauthorized
redistribution/commercial use of Mojang's work. Every installation requires explicit
agreement; the default is rejection. Customers provide their own legitimate Java
Edition accounts. GameStack adds no offline-mode authentication bypass.

Follow the [Minecraft Usage Guidelines](https://www.minecraft.net/en-us/usage-guidelines):
use GameStack as the primary brand, Minecraft descriptively, no official game logos
or copied assets, and a prominent non-affiliation notice. Before a paid listing,
review the actual listing and provide the publisher/contact details required by
those guidelines. Server monetization permission is not blanket permission to sell
Minecraft software or brand assets.

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

Official [Paper documentation](https://docs.papermc.io/paper/),
[itzg Paper configuration](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/server-types/paper/),
[player properties](https://docker-minecraft-server.readthedocs.io/en/latest/configuration/server-properties/),
[ownership/shutdown options](https://docker-minecraft-server.readthedocs.io/en/latest/configuration/misc-options/),
and [healthcheck](https://docker-minecraft-server.readthedocs.io/en/latest/misc/healthcheck/)
were consulted directly because Context7 was unavailable. Documentation is written
in GameStack's own words; no upstream documentation or artwork is vendored.

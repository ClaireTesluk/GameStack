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

# Third-party components

- **PyYAML**, runtime dependency (`>=6.0.2,<7`), MIT license. Upstream: https://github.com/yaml/pyyaml ; license: https://github.com/yaml/pyyaml/blob/main/LICENSE . Installed through the package manager with its own license notice; not vendored. It supplies safe YAML parsing and emission without a custom parser.
- **setuptools**, build dependency (`>=68`), MIT license. Upstream and license: https://github.com/pypa/setuptools . Not vendored; used only for Python package construction.
- **Docker Engine and Docker Compose**, externally installed host prerequisites, not redistributed by this repository. Upstream: https://github.com/moby/moby and https://github.com/docker/compose (Apache-2.0). Docker Desktop has separate terms and is not a declared hosting target.

No upstream game server, image, proprietary license, or game software is included. The example pack contains a placeholder image. Each real GamePack must document and review its own upstream terms before release.

Implementation references: [Compose up](https://docs.docker.com/reference/cli/docker/compose/up/), [Compose interpolation](https://docs.docker.com/reference/compose-file/interpolation/), [PyYAML safe loading](https://pyyaml.org/wiki/PyYAMLDocumentation).

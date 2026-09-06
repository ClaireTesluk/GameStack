# Repository boundaries and separation plan

Build the first two real GamePacks together with the engine in the public
`gamestack` repository. Minecraft Paper is the first pack. Its playable milestone
has passed user-confirmed manual acceptance; backup, restore, safe updates, and
final release acceptance remain pending. The second game is not selected.

## Where work belongs today

| Location | Responsibility |
|---|---|
| `src/gamestack/` | Generic CLI, schema validation, configuration, paths, Docker orchestration, and future recovery tooling |
| `packs/<id>/` | Game settings, image/game pins, upstream records, game-specific guides, and acceptance evidence |
| `packs/example/` | Non-runnable schema reference; does not count as a real pack |
| `tests/` | Runtime and pack tests, with Docker tests in `tests/integration/` |
| `docs/gamepacks.md` | Provisional schema contract, maintained with the runtime validator |
| `docs/` | Shared CLI, architecture, planning, and release documentation |
| `scripts/` and `.github/` | Shared build, test, and release automation |

Keep pack-specific tests identifiable by game, as the Paper tests already are.
They remain in the shared suite until extraction. New games should use declarative
pack settings; extend generic behavior only for concrete requirements. Do not
introduce a plugin framework or split runtime modules merely to match future repo
names. Add a candidate's directory when implementation begins.

The CLI already accepts a pack file path and snapshots the definition into the
instance. Runtime operation does not require a built-in pack catalog or imports
from `packs/`. Preserve that boundary and existing instance paths.

## Current distribution

The Python wheel contains the runtime package. The source archive also includes
the example and experimental Paper pack; native bundles explicitly include those
packs and documentation through `scripts/ci.py`. `MANIFEST.in` lists source-pack
content explicitly. Keep these inclusions deliberate when adding a second pack;
do not automatically bundle every future directory under `packs/`.

This cleanup retains the current root license and distribution behavior. The
planned Apache-2.0 specification and commercial official packs are future outputs;
this document does not relicense existing files or make current packs private.
Preserve third-party notices throughout any later extraction.

## Future repositories

After the interface stabilizes, the intended organization is `gamestackhq`:

| Repository | Visibility | Planned license / terms | Contents |
|---|---|---|---|
| `gamestack` | Public | AGPL-3.0 | Engine, CLI, generic tests, runtime documentation and releases |
| `pack-spec` | Public | Apache-2.0 | Versioned pack format, authoring contract, examples and conformance requirements |
| `community-packs` | Public | AGPL-3.0 | Community definitions, game-specific documentation and tests |
| `official-packs` | Private | Commercial | Polished official pack products, verification records and game-specific guides |
| `gamestack-site` | Private | Proprietary | Website and sales content |

The engine and ecosystem interface stay open to support trust, adoption, and
contributions. Official packs are the repeatable commercial products. Shared
backup, restore, and update implementations belong in the open engine.

## Gates before extraction

1. Complete the first pack's v0.1 release gates, including recovery and updates.
2. Build and validate a second real pack in this repository. Identify shared
   behavior from both implementations; the synthetic example is insufficient.
3. Document the interface both packs actually use, including schema versions,
   validation, configuration, storage, lifecycle, and recovery expectations.
   Resolve concrete game-specific exceptions and protect behavior with tests.
4. Prepare extraction as a separate reviewed change: identify files and their
   applicable licenses, preserve notices and history, assign tests to their new
   owners, and define runtime/pack compatibility and release checks.
5. Verify independently delivered packs work with the released runtime. Update
   packaging, CI, and documentation links, and verify installed instances still
   operate from their existing snapshots without moving user data.

Repository creation and extraction are LATER work. They do not block v0.1 and do
not require a registry, marketplace, payment system, or license-key enforcement
today.

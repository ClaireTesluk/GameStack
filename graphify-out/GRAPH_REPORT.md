# Graph Report - GameStack  (2026-09-10)

## Corpus Check
- 48 files · ~52,217 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 443 nodes · 1008 edges · 25 communities (13 shown, 12 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 56 edges (avg confidence: 0.88)
- Token cost: unmeasured (host session agents).

## Community Hubs (Navigation)
- Product and GamePack Design
- Restore Safety Tests
- Configuration and CLI
- Runtime Validation Tests
- Backup and Restore Operations
- Runtime State and Errors
- Release and Artifact Tests
- Documented Data Safety
- Backup Safety Tests
- Paper Configuration Tests
- CI and Packaging
- XZ Component Licensing
- Build Tool Dependencies
- CLI Help Tests
- Docker Lifecycle Integration
- Apache License Terms
- Paper Save Evidence
- Brotli Attribution
- Bzip2 Attribution
- Libffi Attribution
- LibYAML Attribution
- Mpdecimal Attribution
- Zlib Attribution
- Zstandard Attribution
- Package Entry Point

## God Nodes (most connected - your core abstractions)
1. `GameStackError` - 60 edges
2. `RestoreTests` - 43 edges
3. `Runtime` - 40 edges
4. `EngineTests` - 34 edges
5. `main()` - 25 edges
6. `BackupTests` - 24 edges
7. `PaperTests` - 19 edges
8. `run()` - 16 edges
9. `ReleaseTests` - 16 edges
10. `safe_child()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Synthetic nginx Docker acceptance` --semantically_similar_to--> `Opt-in Paper Docker acceptance harness`  [INFERRED] [semantically similar]
  docs/releases.md → packs/minecraft-paper/acceptance.md
- `BackupTests` --uses--> `GameStackError`  [INFERRED]
  tests/test_backup.py → src/gamestack/pack.py
- `EngineTests` --uses--> `GameStackError`  [INFERRED]
  tests/test_engine.py → src/gamestack/pack.py
- `PaperTests` --uses--> `GameStackError`  [INFERRED]
  tests/test_paper.py → src/gamestack/pack.py
- `RestoreTests` --uses--> `GameStackError`  [INFERRED]
  tests/test_restore.py → src/gamestack/pack.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Restore stages and recovery safeguards** — docs_cli_restore, docs_cli_backup_archive, docs_cli_restore_marker, docs_cli_interrupted_restore_recovery, docs_cli_health_gate [EXTRACTED 1.00]
- **First-pack release readiness gates** — packs_minecraft_paper_acceptance_playable_acceptance, packs_minecraft_paper_acceptance_scenario_acceptance, docs_v0_1_plan_retention_pending, docs_v0_1_plan_updates_pending, third_party_commercial_clearance, docs_v0_1_plan_release_gates [EXTRACTED 1.00]

## Communities (25 total, 12 thin omitted)

### Community 0 - "Product and GamePack Design"
Cohesion: 0.06
Nodes (53): Weekly Actions and monthly pip build-tool updates, CI and release workflow, Isolated release publishing job, Python 3.11–3.14 cross-platform test matrix, Verified wheel/source/native artifact set, GamePack install/lifecycle/persistence/recovery acceptance, Explicit HTTPS agreement acceptance, Explicit numeric bind address (+45 more)

### Community 1 - "Restore Safety Tests"
Cohesion: 0.11
Nodes (3): skipUnless, RestoreTests, start()

### Community 2 - "Configuration and CLI"
Cohesion: 0.09
Nodes (30): ArgumentParser, Explicit entrypoint for the standalone CLI bundle., BackupHelp, command_parser(), configure(), parser(), Beginner-facing commands; logging and interactive input live here., Show focused help without reserving instance names list and verify. (+22 more)

### Community 3 - "Runtime Validation Tests"
Cohesion: 0.09
Nodes (5): main(), load_pack(), Path, read_yaml(), EngineTests

### Community 4 - "Backup and Restore Operations"
Cohesion: 0.13
Nodes (33): BackupRecord, create(), folder(), HashReader, inventory(), visit(), list_backups(), preflight() (+25 more)

### Community 5 - "Runtime State and Errors"
Cohesion: 0.15
Nodes (20): Exception, GameStackError, An expected error safe to display to the user., require_no_transaction(), checked_root(), child(), Path, List locally valid instances without contacting Docker or changing files. (+12 more)

### Community 6 - "Release and Artifact Tests"
Cohesion: 0.11
Nodes (8): ArtifactSmokeTests, Test the exact publishing program embedded in the privileged workflow., ReleaseTests, api(), api(), api(), api(), api()

### Community 7 - "Documented Data Safety"
Cohesion: 0.15
Nodes (22): Failure preserves recoverable data copies, Validate-stop-snapshot-restore-start-health workflow, Private persisted secrets and masked output, Stopped-state manual backup, Private uncompressed .tar backup, Offline backup integrity verification, Side-effect-free nested command help, Docker and instance diagnostics (+14 more)

### Community 10 - "CI and Packaging"
Cohesion: 0.29
Nodes (9): native(), package_smoke(), Portable build and artifact checks. Run from the repository root., Remove synthetic files, allowing briefly held Windows handles to close., Exercise the installed artifact from outside the checkout, with synthetic input., run(), smoke(), smoke_workspace() (+1 more)

### Community 11 - "XZ Component Licensing"
Cohesion: 0.31
Nodes (10): BSD Zero Clause License (0BSD), xz, xzdec, lzmadec, lzmainfo, GNU Autotools build system, GNU getopt_long, GNU gzip, GNU GPLv2+, xzgrep, xzdiff, xzless, xzmore, GNU LGPLv2.1+ (+2 more)

### Community 12 - "Build Tool Dependencies"
Cohesion: 0.20
Nodes (10): build==1.6.0, Build and test tools, packaging==26.3, pyinstaller==6.22.2, pyinstaller-hooks-contrib==2026.7, pyproject.toml runtime dependencies, PyYAML==6.0.3, setuptools==84.0.0 (+2 more)

### Community 14 - "Docker Lifecycle Integration"
Cohesion: 0.29
Nodes (3): DockerIntegration, skipUnless, Explicit opt-in tests using only synthetic data and a disposable CI container.

### Community 15 - "Apache License Terms"
Cohesion: 0.33
Nodes (6): Apache License 2.0, Copyright license grant, NOTICE attribution file, Patent license grant, Redistribution conditions, Trademark restrictions

## Knowledge Gaps
- **30 isolated node(s):** `gamestack`, `Brotli license notice`, `Brotli Authors`, `bzip2/libbzip2 1.0.8 license notice`, `Julian R Seward` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 105 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameStackError` connect `Runtime State and Errors` to `Restore Safety Tests`, `Configuration and CLI`, `Runtime Validation Tests`, `Backup and Restore Operations`, `Backup Safety Tests`, `Paper Configuration Tests`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `Runtime` connect `Runtime State and Errors` to `Restore Safety Tests`, `Configuration and CLI`, `Runtime Validation Tests`, `Backup and Restore Operations`, `Backup Safety Tests`, `Paper Configuration Tests`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `RestoreTests` connect `Restore Safety Tests` to `Configuration and CLI`, `Runtime Validation Tests`, `Runtime State and Errors`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `GameStackError` (e.g. with `Runtime` and `PaperIntegration`) actually correct?**
  _`GameStackError` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `RestoreTests` (e.g. with `GameStackError` and `Runtime`) actually correct?**
  _`RestoreTests` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Runtime` (e.g. with `run()` and `GameStackError`) actually correct?**
  _`Runtime` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `EngineTests` (e.g. with `GameStackError` and `Runtime`) actually correct?**
  _`EngineTests` has 2 INFERRED edges - model-reasoned connections that need verification._

Extraction accounting: semantic extraction used the host session agents. Token usage and cost were not measured; zero counters are placeholders, not zero usage.

Graph integrity warning: raw extraction has 149 dangling-endpoint edges, 2 self-loops, and 58 same-endpoint edges collapsed by the undirected build. These are extraction limitations, not confirmed repository defects. Raw extraction retained in `.graphify_extract.json`.

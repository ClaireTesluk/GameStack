# Experimental GamePack schema 1

Use [packs/example/pack.yaml](../packs/example/pack.yaml) as the format reference. It intentionally names a nonexistent image and healthcheck: validation proves structure, not deployability. It is not a supported game or a distributable server.

```bash
gamestack pack validate packs/example/pack.yaml
```

Expected result: `GamePack is valid (schema 1)` with a reminder that image availability and game behavior are untested. Invalid YAML, duplicate/unknown fields, unsupported versions, or unsafe paths return exit status 1 with guidance. Error output omits source lines that might contain credentials.

## Fields

| Field | Meaning |
|---|---|
| `schema_version` | Integer `1`; other versions fail explicitly |
| `id` | Lowercase letter followed by lowercase letters, digits, or hyphens; at most 40 characters |
| `version` | Quoted nonempty GamePack version; retained with the installation |
| `name` | Human-readable display name |
| `image` | Full image reference ending in `@sha256:` and a 64-character lowercase digest; no floating tags |
| `data_path` | Normalized absolute Linux container path below `/`; all persistent data must live here |
| `stop_timeout` | Integer seconds, 10–600; choose based on verified upstream graceful shutdown behavior |
| `user` | Optional quoted non-root numeric `UID:GID`; only set if upstream supports it and storage is provisioned accordingly |
| `ports` | List of `host` and `container` integer ports, `protocol` (`tcp`/`udp`), and human-readable `purpose`; localhost-only in this milestone |
| `environment` | Mapping of uppercase environment names to `prompt`, boolean `secret`, and optional quoted `default`; defaults cannot be secrets |
| `healthcheck` | Nonempty list of executable and arguments present in the image; executed without a shell |

All settings are required; defaults satisfy non-secret settings when running noninteractively. Quote string values, including numeric settings and versions. There are no templates, environment substitution, arbitrary Compose fragments, scripts, multiple services, or host storage paths in packs. Every field shown in the example is required, even when ports/environment are empty collections.

The single `data/` folder must contain all saves needed for recovery. Pack authors must independently test that an image actually uses that location. The engine does not yet implement backup or restore.

## Configuration and credentials

Installation prompts for declared settings. Secret prompts hide input. For noninteractive preparation, use `--values /path/outside/repository/values.yaml` containing a plain mapping:

```yaml
SERVER_NAME: Friends server
SERVER_PASSWORD: "replace-with-your-own-password"
```

Protect this input file yourself (on Linux, `chmod 600 /path/to/values.yaml`). Never commit it. The engine stores values inside the generated `compose.yaml`, with mode 0600 under a private 0700 instance directory on POSIX. Credentials are plaintext on disk and visible to accounts with Docker access. Dollar signs are escaped for Compose so literal input survives interpolation. Debug mode does not print configuration or subprocess output.

An installation snapshots `pack.yaml`, creates `data/` and `compose.yaml`, then writes `instance.yaml` as its completion marker. Paths remain stable across lifecycle operations. Do not move directories or hand-edit generated files; the engine rejects mismatches. Editing/upgrading existing configurations requires future migration tooling.

## Before calling a real GamePack supported

Document the upstream project, image digest, upstream license/notices, game software licensing, supported game version, hardware recommendations, exposed port purposes/protocols, storage and ownership, healthcheck, shutdown behavior, backup/update behavior, and known limitations. Run all GamePack acceptance criteria in AGENTS.md on the supported host. Schema validation is only the first check.

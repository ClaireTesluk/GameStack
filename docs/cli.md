# Using the development CLI

This is the first engine milestone, version `0.1.0.dev1`. No game is supported yet. Manual backup creation, listing, and integrity verification are implemented. Restore, retention, updates, and scheduled maintenance are pending; use synthetic data for development.

## Setup

From the repository, using Python 3.11 or newer:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
gamestack --help
```

On Windows development machines, activate `.venv\Scripts\Activate.ps1` in PowerShell. Development portability is intended, but Windows/macOS have not been validated. Hosting targets Ubuntu Server LTS on x86-64 and is awaiting actual host acceptance. Docker access and Compose supporting `up --wait-timeout` must already be installed for server operations.

If doctor reports that Docker is reachable but Docker Compose is unavailable, install or repair your distribution's Compose plugin and verify `docker compose version`. Docker Engine alone does not supply this capability in every distribution. See [Docker's Compose installation guide](https://docs.docker.com/compose/install/linux/).

## Try the foundation without Docker

```bash
gamestack pack validate packs/example/pack.yaml
gamestack install packs/example/pack.yaml --name sandbox --prepare-only
```

Installation prompts for server name and password. It creates configuration and an empty world folder under `~/.local/share/gamestack/sandbox`. It does not start a container with `--prepare-only`. The bundled example cannot be started; replace its placeholder image and healthcheck in your own pack before testing hosting.

Use `gamestack --root /srv/gamestack ...` to choose a dedicated writable storage directory. Specify the same root for subsequent commands. No command elevates privileges or changes ownership. Do not put instance storage inside a source checkout.

## Commands

| Purpose | Syntax/example | Expected result | Common failures and action |
|---|---|---|---|
| Validate pack | `gamestack pack validate packs/example/pack.yaml` | Schema-valid message | Correct YAML/types/required fields using gamepacks.md |
| Configure and launch | `gamestack install /path/to/pack.yaml --name friends` | Prepared location, then healthy server | Run doctor for host tooling; inspect pack image/permissions/ports/healthcheck; prepared files remain on startup failure |
| Prepare only | `gamestack install /path/to/pack.yaml --name friends --prepare-only --values /private/values.yaml` | Files created, no Docker call | Supply missing settings; choose a new name if instance exists |
| List configured instances | `gamestack list` | Alphabetically sorted names with container state and health | Invalid instances are skipped with a warning; use doctor to investigate |
| Start | `gamestack start friends` | Healthy after healthcheck | Check pack healthcheck and data-folder permissions; failed start may leave server running |
| Remove instance | `gamestack rm friends` | Confirms, stops and removes container; retains files and hides instance from list | Check Docker access or instance lock; failed removal retains configuration for retry |
| Stop | `gamestack stop friends` | Stopped; worlds retained | Check Docker access; inspect server state before retrying a timeout |
| Restart | `gamestack restart friends` | Stopped then healthy | Failed stop prevents start; failed health leaves data in place |
| Status | `gamestack status friends` | Container state and health, or not created | Correct missing/incomplete configuration; run doctor |
| Check prerequisites | `gamestack doctor` | Docker access and Compose capability pass | Install/start Docker and grant the operating account access |
| Create backup | `gamestack backup friends` | Verified archive location and final server state | Check disk space, permissions, and clean shutdown; partial artifacts retained |
| List backups | `gamestack backup list friends` | Newest-first IDs, UTC dates, and sizes; no integrity recheck | Check instance name, root, and backup folder access |
| Verify backup | `gamestack backup verify friends BACKUP-ID` | Full archive integrity verified without extraction | Keep corrupt/incomplete archives and select another copy |
| Check instance | `gamestack doctor friends` | Also validates saved configuration and world-folder existence | Restore missing configuration/data; do not bypass safety checks |

Global options precede the command: `gamestack --debug --root /srv/gamestack status friends`. Debug logs include safe operation boundaries, elapsed subprocess time, and failure type, never raw server output. There is no logs command yet because arbitrary upstream logs can expose credentials.

Doctor does not establish available capacity, port reachability, save consistency, or game support. The first pack's acceptance work will expand these checks.

## Find configured instances

```bash
gamestack list
gamestack --root /srv/gamestack list
```

The command lists instance names (including installations made with `--prepare-only`), rather than available pack files. Use these names with `start`, `stop`, `restart`, and `status`. It reads local configuration and queries Docker for a quick status snapshot without changing files or taking operation locks. Use the same `--root` for listing and lifecycle commands.

Example output:

```text
Configured instances:
  friends: started (healthy)
  sandbox: stopped (not created)
```

Running containers show `started`, with `healthy`, `unhealthy`, or `starting` in parentheses when Docker reports a healthcheck result. Otherwise the container state is shown: `stopped` for a clean exit or a container that has not started, and `crashed (nonzero exit)` for an unsuccessful exit. This label is an exit-code heuristic; a forced stop can also produce a nonzero exit. Dead containers show `crashed`; paused, restarting, and removing containers retain those states. Stopped containers do not display stale health results. A missing exit code is reported explicitly.

Each instance query has a five-second timeout. If Docker is unavailable or returns an unreadable result, that instance remains listed as `unknown (status unavailable)` with a warning to run doctor. Listing still returns exit status 0 when discovery succeeds, even if live status is unavailable. Health describes a snapshot, not a guarantee that the game is ready for players. The schema still requires a pack healthcheck; the fallback covers containers without a reported health result.

Docker state, health, and exit code come from [Compose ps JSON output](https://docs.docker.com/reference/cli/docker/compose/ps/).

A missing or empty storage directory returns a friendly message and exit status 0. Incomplete, invalid, inaccessible, or symlinked instances are skipped with warnings while valid instances are still listed. Unrelated files and invalid directory names are ignored. Failure to read the storage directory returns exit status 1; check its permissions.

## Remove a configured instance

```bash
gamestack rm friends
gamestack --root /srv/gamestack rm friends --yes
```

`rm` removes an installed instance, not the original GamePack YAML file. It asks for confirmation with a default of No. Noninteractive use requires `--yes`. This is a USEFUL SOON feature included in the current release scope by request.

Removal validates the instance paths/configuration, takes its operation lock, stops the server using the pack shutdown timeout, removes its container, and verifies that no server container remains. It then writes `removed.yaml` inside the instance directory. Removed instances disappear from `list` and cannot be started through lifecycle commands.

World data in `data/`, backups, and configuration remain at their existing paths, which the command prints. The instance name stays reserved; a new install must use a different name. Images, volumes, and the project network are retained. There is no data-purge option. Data stored only in the container's writable layer is lost on removal: packs must put all persistent saves in the declared data mount, as required by the schema. [Docker container removal behavior](https://docs.docker.com/reference/cli/docker/compose/rm/).

Docker must be accessible, even for an instance created with `--prepare-only`, so GameStack can verify whether a container exists. A failed stop prevents removal; a failed removal or verification does not mark the instance removed. If writing the marker fails, the container may already be gone; retained configuration permits retry. Interrupted operations may leave a lock, as described below.

To reactivate a removed instance during development, verify that no operation is running and that its original configuration and data paths remain intact, then delete only its `removed.yaml` marker. Run `gamestack doctor friends` and `gamestack start friends` with the original root. No automated recovery or deletion of retained files is provided yet.

## Recovering from interrupted development work

An existing instance is never overwritten by install. If preparation fails, its files remain and the missing completion marker prevents use. Inspect them and choose a fresh instance name; preserve any world files before manual cleanup.

Operations use `.operation.lock` inside the instance directory. If interrupted, first verify no GameStack process is still operating on that instance. Only then remove that specific stale lock file and retry. There is no automatic lock breaking or recursive cleanup.

The default published ports bind only to localhost; friends cannot connect remotely in this milestone. Data folders belong to the installing user with private permissions. Packs running another UID require deliberate provisioning as part of the first real pack's setup work.

## Tests

```bash
python3 -m pip install packaging
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

After editable installation, `python -m unittest discover -s tests -v` also works. Tests use temporary synthetic worlds and mock Docker. Passing them does not constitute real Docker or game-server acceptance.

## Experimental Paper installation

`gamestack install packs/minecraft-paper/pack.yaml --bind-address 0.0.0.0`
configures and starts the experimental private Java server. Follow the
[Paper walkthrough](../packs/minecraft-paper/README.md) for EULA acceptance,
profile names, defaults, expected results, networking, and failure recovery.

`--bind-address` is available for schema 2; omitted means localhost unless an
interactive user explicitly chooses exposure. All-interface binding can expose
the game port publicly. Existing schema 1 instances are unchanged.

## Manual backups

```bash
gamestack backup friends
gamestack backup list friends
gamestack backup verify friends BACKUP-ID
```

Replace `BACKUP-ID` with an ID from the listing, without a file extension. Global
options still precede the command. Instance names `list` and `verify` remain valid:
`gamestack backup list` creates a backup of the instance named `list`.

Creation briefly stops a running server without an extra confirmation prompt,
checks its clean exit, captures and verifies its files, then restarts it and checks
health. Players will be disconnected. Previously stopped or never-started instances
remain stopped. Docker must be available even when no container has been created.
Crashes, ambiguous states, and unsuccessful shutdowns block capture; inspect status
and resolve the server problem before retrying.

Success prints a verified ID, absolute location, and final server state. Archives
live in `<root>/<instance>/backups/` as timestamped, uniquely identified `.tar` files.
They contain the entire `data/` folder and saved instance, pack, and Compose
configuration. Modes and modification times are retained; links and special files
are rejected. Backup files are private (`0600`) inside a private folder (`0700`) on
Linux. They are **unencrypted and may contain credentials**; keep them private.
Do not modify source data through other tools while capture runs.

Archives are uncompressed, so allow approximately the full data/configuration size
plus headers, manifest allowance, and at least 64 MiB of free-space reserve. All
backups are retained. There is no automatic pruning, restore command, scheduling,
custom destination, exclusion list, or compression option in this milestone.

Listing works without Docker, displays IDs, UTC timestamps and sizes newest first,
and does not recheck integrity. Empty listings succeed. Verification reads every
archived file and checks its hash, metadata, and archive structure without extracting
anything. Both commands remain available after `rm`, or if the active data folder
is missing, provided the instance and backup folders remain at their original paths.
Verification detects corruption; it neither authenticates an archive nor proves
that Minecraft can restore it. Restore acceptance remains pending.

Failures return exit status 1, and interrupts return 130:

- Insufficient space or unsafe source paths found before shutdown leave the server
  running. Free space or correct the source layout and retry.
- Failed/unverified shutdown prevents capture and automatic restart. Check
  `gamestack status friends` and `gamestack doctor friends` before restarting.
- Capture failure after verified shutdown still attempts to resume an initially
  running server; the backup command remains unsuccessful.
- Failed restart after a verified backup retains the archive and prints its usable
  location. Check status/doctor before retrying `gamestack start friends`.
- Partial `.partial` artifacts are retained and warned about in listings, never
  treated as completed backups. Older backups and source files are preserved.
- Interrupts retain created artifacts and do not automatically restart the server.
  Check status before acting. Abrupt termination may leave the existing operation
  lock; follow the interrupted-operation instructions above.

A nonzero result can coexist with a valid retained backup. Read the result before
retrying. Do not manually remove partial files or stale locks while an operation is
still running. No backup deletion is performed by GameStack.

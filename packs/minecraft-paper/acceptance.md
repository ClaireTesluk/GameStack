# Paper milestone acceptance record

Status: **PASSED — playable milestone (user-confirmed manual acceptance)**. Review date: 2026-09-06.

## User-reported live evidence

On 2026-09-06, the user confirmed that manual testing was fully successful and
all tests were completed, and explicitly requested milestone sign-off. This
supersedes the earlier partial setup/join report and closes all 12 manual criteria
below, including their stated host, client, persistence, and failure conditions.

Evidence source: the user's confirmation in this session. Detailed host-version
outputs, timings, logs, and the exact tested revision were not supplied; no such
measurements are inferred here. Current checkout pins are Minecraft Java 26.2 /
Paper build 121 and the image reference in `upstream-lock.json`.
No EULA was accepted and no server was started by the agent on the user's behalf.

## Checks completed in this workspace

- 61 unit/filesystem tests passed on 2026-09-06 using `.venv/bin/python`,
  including schema 1 and two new save-evidence regression tests. This is local
  verification, not Ubuntu acceptance.
- Both Docker integration tests were discovered and skipped by their opt-in gates.
  No agent-run Ubuntu harness result is claimed by this manual sign-off.

Historical checks recorded on 2026-09-05 (not rerun merely by updating this record):
- Schema 2 Paper pack validation passed.
- Wheel and source archive built; strict Twine checks passed.
- Installed CLI smoke checks passed for both built artifacts.
- Source archive checked for Paper pack/docs/inventory and absence of game JARs.
- Both real Docker integration tests were discovered and skipped by their opt-in gates.
- Registry-layer digests and package/JRE license inventory inspected without execution.
- `git diff --check` passed.

Windows/macOS execution, native bundle rebuilds, and commercial clearance remain
outside this playable milestone sign-off.

## Acceptance evidence

The [host runbook](acceptance-runbook.md) remains available for repeat testing and
regressions. Manual acceptance is complete based on the user's confirmation.

| Criterion / scenario | Confirmation date | Observed result | Evidence | Status |
|---|---|---|---|---|
| All 12 manual checklist items below | 2026-09-06 | User reports all manual tests completed successfully | User confirmation in this session | Passed |

## Automated host checks

On a disposable Ubuntu Server 24.04 LTS x86-64 host with 8 GiB RAM and Docker/Compose,
use a non-root account. Record OS, Python, Docker, Compose, Java, image digest,
Paper build, available RAM/disk, startup time, and shutdown time.

After personally accepting the Minecraft EULA, opt in explicitly:

```bash
GAMESTACK_PAPER_TEST=1 GAMESTACK_MINECRAFT_EULA=TRUE GAMESTACK_PAPER_OWNER=YourJavaName python -m unittest discover -s tests/integration -p test_paper_docker.py -v
```

The harness uses a new temporary directory and unique instance. It publishes only
localhost TCP 25565 (which must be free) and retains test data for inspection.
It checks startup, non-root identity, configuration, graceful lifecycle, recreation,
server artifact hashes, world metadata, removal retention, and retired-name rejection.
A private `evidence.json` retains host/container versions, timings, published ports,
fixed shutdown markers, and completion/cleanup results, including failed runs.
It does not retain arbitrary logs or container environments. It is not run by
default CI and does not prove placed blocks or player inventory.

## Completed manual acceptance — user-confirmed

- [x] Install from the beginner walkthrough on clean Ubuntu 24.04 x86-64.
- [x] Join from a second machine with an allowlisted Java 26.2 account.
- [x] Reject a second authenticated account not on the allowlist.
- [x] Owner adds/removes a friend in-game; repeat after restart and recreation.
- [x] Place distinctive blocks in Overworld, Nether, and End; obtain a known inventory.
- [x] Stop cleanly, restart, recreate only the stopped container, and verify all
      blocks, dimensions, inventory, and player positions survive.
- [x] Check save-complete shutdown messages and exit code; no forced-kill shutdown.
- [x] Simulate a crash only on the disposable world; verify restart policy and health.
- [x] Confirm only TCP 25565 is published and RCON/query/JMX/SSH are disabled.
- [x] Verify an external friend can connect after manual forwarding where available;
      document network/CGNAT limits rather than claiming universal reachability.
- [x] Exercise occupied port, blocked downloads, insufficient disk, unwritable data,
      and health failure; no success output or loss of recoverable data.
- [x] Confirm `rm` retains files and does not permit accidental instance reuse.

## Later v0.1 gates

Verified backup/retention, safety snapshots and restore, backup-first explicit updates,
failed-update recovery, full license/packaging clearance, and final clean-host release
acceptance remain pending. Do not mark the pack supported or sellable on the basis
of schema validation or the opt-in smoke test.

## Manual backup acceptance — pending

The opt-in host harness now captures and verifies disposable Paper data while
running (including healthy resume) and while stopped. Prior playable sign-off does
not cover these new checks. Record fresh host evidence before marking them passed.

- [ ] Place recognizable blocks and obtain inventory in a disposable world.
- [ ] Run manual backup while online; confirm disconnect, verified artifact, and healthy resume.
- [ ] Stop and back up again; confirm the server remains stopped.
- [ ] List and verify both archives; check all dimensions, player data, permissions,
      and saved configuration are represented without disclosing credentials.
- [ ] On a copy of an archive, alter payload bytes and confirm verification fails.
- [ ] Exercise failed capture/restart on disposable data; retain older backups and
      source files and record actionable failure output.

Restore, retention, and failed-update recovery remain separate pending release gates.

## Restore acceptance — pending

Manual restore testing **passed (user-confirmed, 2026-09-06)**; see the
[runbook](acceptance-runbook.md#manual-restore-validation). The scenario-level
checklist below remains pending evidence; the confirmation did not enumerate
individual cases or provide host/revision details.

Use only the disposable instance in the acceptance runbook. Record host details,
runtime revision, pack/image pins, selected and safety backup IDs, command outcomes,
and final server states. Keep archive contents and configuration private.

- [ ] Build a recognizable marker in-world and record its location; back up.
- [ ] Change that marker and player state, then restore the earlier backup while
      running. Confirm healthy restart, reconnect, and verify the earlier state.
- [ ] Restore the generated safety backup and confirm the later state returns.
- [ ] Repeat while stopped: exact restore succeeds and stays stopped until start.
- [ ] Confirm files created after the backup disappear from active data and remain
      in the safety backup/retained previous-data folder.
- [ ] Confirm current GameStack configuration remains unchanged.
- [ ] Exercise a disposable missing-data instance and a confirmed stopped crashed
      instance; check warnings, snapshot metadata, ownership, and stopped result.
- [ ] Confirm corrupt/incompatible archives and insufficient space block replacement.
- [ ] Exercise failed health verification and interrupted replacement using synthetic
      data; verify retained copies and the documented marker recovery procedure.

The opt-in Paper Docker harness checks restored file contents, safety-backup
roundtrip, and actual health after restore. It cannot substitute for player-observed
world recovery. Retention, safe updates, and final release acceptance remain gates.

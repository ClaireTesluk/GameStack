"""Local instance storage and a small Docker Compose boundary."""
from contextlib import contextmanager
import hashlib
import json
import logging
import os
from pathlib import Path
import platform
import subprocess
import time

import yaml

from .pack import GameStackError, fields, load_pack, name, read_yaml, require, string

log = logging.getLogger(__name__)


def checked_root(path: Path) -> Path:
    path = path.expanduser().absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise GameStackError("The storage path contains a symbolic link. Choose a dedicated real directory.")
    path = path.resolve()
    if path in (Path.home().resolve(), Path("/srv"), Path("/opt"), Path("/home")) or len(path.parts) < 3:
        raise GameStackError("Storage needs a dedicated subdirectory, such as /srv/gamestack.")
    return path


def child(parent: Path, component: str) -> Path:
    path = parent / component
    if path.is_symlink() or path.resolve().parent != parent.resolve():
        raise GameStackError("An instance path is unsafe. Check for symbolic links before retrying.")
    return path


def write_private(path: Path, value: dict) -> None:
    # Exclusive creation leaves existing configuration untouched, including symlinks.
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as stream:
        yaml.safe_dump(value, stream, sort_keys=False, allow_unicode=True)


def literal(value):
    """Escape Compose interpolation recursively, including passwords and host paths."""
    if isinstance(value, str):
        return value.replace("$", "$$")
    if isinstance(value, list):
        return [literal(v) for v in value]
    if isinstance(value, dict):
        return {k: literal(v) for k, v in value.items()}
    return value


def compose(pack: dict, values: dict, directory: Path) -> dict:
    service = {
        "image": pack["image"], "restart": "unless-stopped",
        "stop_grace_period": f'{pack["stop_timeout"]}s',
        "environment": values,
        "ports": [{"target": p["container"], "published": str(p["host"]),
                   "host_ip": "127.0.0.1", "protocol": p["protocol"]} for p in pack["ports"]],
        "volumes": [{"type": "bind", "source": str(directory / "data"), "target": pack["data_path"],
                     "bind": {"create_host_path": False}}],
        "healthcheck": {"test": ["CMD", *pack["healthcheck"]], "interval": "10s", "timeout": "5s", "retries": 12},
    }
    if "user" in pack:
        service["user"] = pack["user"]
    return literal({"services": {"server": service}})


class Runtime:
    def __init__(self, root: Path):
        self.root = checked_root(root)

    def directory(self, instance: str) -> Path:
        return child(self.root, name(instance))

    def list_instances(self) -> list[str]:
        """List locally valid instances without contacting Docker or changing files."""
        try:
            entries = sorted(self.root.iterdir(), key=lambda path: path.name)
        except FileNotFoundError:
            return []
        instances = []
        for entry in entries:
            try:
                name(entry.name)
            except GameStackError:
                continue
            if not entry.is_symlink() and not entry.is_dir():
                continue
            if not entry.is_symlink() and (entry / "removed.yaml").is_file():
                continue
            try:
                self.inspect(entry.name)
            except (GameStackError, OSError):
                log.warning("Skipping instance=%s: configuration is incomplete, inaccessible, or unsafe. Run gamestack doctor %s to investigate.", entry.name, entry.name)
                continue
            instances.append(entry.name)
        return instances

    def prepare(self, pack: dict, instance: str, values: dict) -> Path:
        require(values.keys() == pack["environment"].keys() and all(string(v) for v in values.values()),
                "Every configuration setting needs a nonempty single-line string.")
        directory = self.directory(instance)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError as exc:
            raise GameStackError("Instance already exists. Choose another name or use its lifecycle commands; no files were replaced.") from exc
        log.info("Preparing instance=%s", instance)
        # Interrupted setup stays in place for inspection. Never recursively clean up user paths.
        (directory / "data").mkdir(mode=0o700)
        write_private(directory / "pack.yaml", pack)
        write_private(directory / "compose.yaml", compose(pack, values, directory))
        write_private(directory / "instance.yaml", {"schema_version": 1, "instance": instance})
        log.info("Prepared instance=%s", instance)
        return directory

    def inspect(self, instance: str) -> tuple[Path, dict]:
        directory = self.directory(instance)
        marker = child(directory, "removed.yaml")
        if marker.exists():
            raise GameStackError("This instance was removed. Its files remain in the instance directory for recovery; choose a new name for a new installation.")
        for filename in ("instance.yaml", "pack.yaml", "compose.yaml", "data"):
            child(directory, filename)
        metadata = read_yaml(directory / "instance.yaml")
        fields(metadata, {"schema_version", "instance"})
        require(type(metadata["schema_version"]) is int and metadata["schema_version"] == 1 and metadata["instance"] == instance,
                "Instance metadata does not match.")
        pack = load_pack(directory / "pack.yaml")
        if not (directory / "data").is_dir():
            raise GameStackError("World folder is missing. Recover it before starting the server.")
        # Reject hand-edited Compose that could introduce arbitrary host mounts or images.
        document = read_yaml(directory / "compose.yaml")
        try:
            escaped = document["services"]["server"]["environment"]
            values = {k: v.replace("$$", "$") for k, v in escaped.items()}
            require(values.keys() == pack["environment"].keys() and all(string(v) for v in values.values()), "Invalid saved settings.")
            require(document == compose(pack, values, directory), "Generated server configuration has changed.")
        except (KeyError, AttributeError, TypeError, RecursionError) as exc:
            raise GameStackError("Saved server configuration is invalid. Recover the original configuration before retrying.") from exc
        return directory, pack

    @contextmanager
    def lock(self, directory: Path):
        path = child(directory, ".operation.lock")
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise GameStackError("Another operation holds this instance's lock. Wait; after an interruption, verify no operation is running before removing .operation.lock.") from exc
        try:
            os.close(fd)
            yield
        finally:
            path.unlink()

    def command(self, args: list[str], timeout: int = 30) -> str:
        started = time.monotonic()
        try:
            result = subprocess.run(args, check=True, capture_output=True, text=True, encoding="utf-8", timeout=timeout)
        except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
            # Docker output and exception strings can expose credentials; never log either.
            log.debug("Server tooling failed type=%s elapsed=%.2fs", type(exc).__name__, time.monotonic() - started)
            raise GameStackError("Server operation failed. Check Docker is installed and running and your account has access; run gamestack doctor. For start failures, also check the pack image, ports, permissions, and healthcheck. Existing data was retained.") from exc
        log.debug("Server tooling completed elapsed=%.2fs", time.monotonic() - started)
        return result.stdout

    def doctor(self) -> None:
        if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
            raise GameStackError("Hosting targets Linux x86-64. Use an Ubuntu Server LTS x86-64 host; local pack validation works on other systems.")
        self.command(["docker", "info", "--format", "{{.ServerVersion}}"])
        try:
            self.command(["docker", "compose", "version"])
        except GameStackError as exc:
            raise GameStackError("Docker is reachable, but Docker Compose is unavailable. Install or repair the Docker Compose plugin for your distribution, verify with docker compose version, then retry.") from exc
        help_text = self.command(["docker", "compose", "up", "--help"])
        if "--wait-timeout" not in help_text:
            raise GameStackError("Docker Compose is too old. Install a Compose version with up --wait-timeout support.")

    def compose_command(self, directory: Path) -> list[str]:
        project = "gamestack-" + hashlib.sha256(str(directory).encode()).hexdigest()[:16]
        return ["docker", "compose", "--project-name", project, "--project-directory", str(directory),
                "--file", str(directory / "compose.yaml")]

    def remove(self, instance: str) -> Path:
        """Remove the server container and retire its configuration, retaining all files."""
        directory, pack = self.inspect(instance)
        with self.lock(directory):
            self.inspect(instance)
            self.doctor()
            base = self.compose_command(directory)
            log.warning("Removing instance=%s container; retaining files at %s", instance, directory)
            self.command(base + ["stop", "--timeout", str(pack["stop_timeout"]), "server"], pack["stop_timeout"] + 30)
            self.command(base + ["rm", "--force", "server"])
            remaining = self.command(base + ["ps", "--all", "--quiet", "server"])
            if remaining.strip():
                raise GameStackError("Container removal could not be verified. Run gamestack status and retry rm with the instance name. All instance files were retained.")
            # Written only after confirmed removal. Keep paths stable for recovery.
            write_private(directory / "removed.yaml", {"schema_version": 1, "instance": instance})
            log.info("Removed instance=%s; retained files at %s", instance, directory)
        return directory

    def quick_status(self, instance: str) -> str:
        """Read a bounded status snapshot without locks or host preflight."""
        try:
            directory = self.directory(instance)
            raw = self.command(self.compose_command(directory) +
                               ["ps", "--all", "--format", "json", "server"], timeout=5)
            rows = json.loads(raw) if raw.strip().startswith("[") else [
                json.loads(line) for line in raw.splitlines() if line.strip()]
            if not rows:
                return "stopped (not created)"
            if len(rows) != 1 or not isinstance(rows[0], dict):
                raise ValueError("Unexpected container count or format")
            row = rows[0]
            state, health, code = row.get("State"), row.get("Health"), row.get("ExitCode")
            if state == "running":
                return f"started ({health})" if health in ("healthy", "unhealthy", "starting") else "started"
            if state == "exited":
                if type(code) is int and code >= 0:
                    return "stopped" if code == 0 else "crashed (nonzero exit)"
                return "stopped (exit code unavailable)"
            if state == "dead":
                return "crashed"
            if state == "created":
                return "stopped"
            if state in ("restarting", "paused", "removing"):
                return state
            raise ValueError("Unknown container state")
        except (GameStackError, OSError, ValueError, TypeError, RecursionError):
            log.warning("Status unavailable for instance=%s. Check Docker access with gamestack doctor.", instance)
            return "unknown (status unavailable)"

    def lifecycle(self, action: str, instance: str) -> str:
        directory, pack = self.inspect(instance)
        base = self.compose_command(directory)
        with self.lock(directory):
            self.inspect(instance)
            self.doctor()
            log.info("Operation=%s instance=%s started", action, instance)
            if action == "status":
                # Only query fixed state fields; never return raw container output or labels.
                raw = self.command(base + ["ps", "--all", "--format", "json"])
                try:
                    rows = json.loads(raw) if raw.strip().startswith("[") else [json.loads(line) for line in raw.splitlines() if line.strip()]
                    states = []
                    for row in rows:
                        state, health = row.get("State"), row.get("Health")
                        states.append(f"{state if state in ('running', 'exited', 'created', 'restarting', 'paused', 'dead') else 'unknown'} / {health if health in ('healthy', 'unhealthy', 'starting') else 'health unavailable'}")
                    return ", ".join(states) or "not created"
                except (ValueError, AttributeError, TypeError) as exc:
                    raise GameStackError("Cannot read server status. Check your Docker Compose installation.") from exc
            if action not in ("start", "stop", "restart"):
                raise GameStackError("Unknown operation. Run gamestack --help.")
            if action in ("stop", "restart"):
                self.command(base + ["stop", "--timeout", str(pack["stop_timeout"])], pack["stop_timeout"] + 30)
            if action in ("start", "restart"):
                self.command(base + ["up", "--detach", "--no-recreate", "--pull", "missing", "--wait", "--wait-timeout", "180"], 900)
            log.info("Operation=%s instance=%s completed", action, instance)
        return "stopped" if action == "stop" else "healthy"

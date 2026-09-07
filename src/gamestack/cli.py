"""Beginner-facing commands; logging and interactive input live here."""
import argparse
import getpass
import logging
from pathlib import Path
import sys

from . import __version__
from .pack import GameStackError, load_pack, read_yaml, string, validate_value, bind_address
from .runtime import Runtime


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="gamestack", description="Manage local game servers using GamePacks (experimental).")
    result.add_argument("--version", action="version", version=__version__)
    result.add_argument("--debug", action="store_true")
    result.add_argument("--root", type=Path, default=Path.home() / ".local" / "share" / "gamestack", help="Dedicated instance storage directory")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List configured instances with container state and health")
    backup = commands.add_parser("backup", help="Create, list, or verify private full-data backups")
    backup.add_argument("arguments", nargs="+", metavar="ARG", help="INSTANCE | list INSTANCE | verify INSTANCE BACKUP-ID")
    remove = commands.add_parser("rm", help="Remove an instance's container, retaining worlds, backups, and configuration")
    remove.add_argument("instance")
    remove.add_argument("--yes", action="store_true", help="Confirm container removal without prompting")
    pack = commands.add_parser("pack", help="Check a GamePack before installation")
    sub = pack.add_subparsers(dest="pack_command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("file", type=Path)
    install = commands.add_parser("install", help="Configure a local GamePack and start its server")
    install.add_argument("file", type=Path)
    install.add_argument("--bind-address", help="Schema 2: numeric host IP; default localhost. 0.0.0.0 exposes game ports on all IPv4 interfaces.")
    install.add_argument("--name", help="Instance name (defaults to pack id)")
    install.add_argument("--values", type=Path, help="YAML mapping of configuration values; keep secrets outside the repository")
    install.add_argument("--prepare-only", action="store_true", help="Write configuration without starting a server or requiring Docker")
    for action in ("start", "stop", "restart", "status"):
        command = commands.add_parser(action)
        command.add_argument("instance")
    doctor = commands.add_parser("doctor", help="Check host prerequisites and optional instance configuration")
    doctor.add_argument("instance", nargs="?")
    return result


def configure(pack: dict, supplied: dict) -> dict:
    if supplied.keys() - pack["environment"].keys():
        raise GameStackError("Unknown configuration settings. Use the environment keys declared in the GamePack.")
    if any("value" in pack["environment"][key] for key in supplied):
        raise GameStackError("Fixed GamePack settings cannot be supplied through --values. Remove those keys.")
    values = {}
    for key, setting in pack["environment"].items():
        if "value" in setting:
            values[key] = setting["value"]
            continue
        if "agreement" in setting and key not in supplied and sys.stdin.isatty():
            answer = input(f"{setting['prompt']}\n{setting['agreement']}\nAccept? [y/N] ")
            values[key] = validate_value(key, setting, "TRUE" if answer.strip().lower() in ("y", "yes") else "FALSE")
            continue
        if key in supplied:
            value = supplied[key]
        elif "default" in setting and not sys.stdin.isatty():
            value = setting["default"]
        else:
            if not sys.stdin.isatty():
                raise GameStackError("Required settings are missing. Run interactively or provide --values with every required setting.")
            default = setting.get("default")
            prompt = setting["prompt"] + (f" [{default}]" if default else "") + ": "
            value = (getpass.getpass(prompt) if setting["secret"] else input(prompt)) or default
        if not string(value):
            raise GameStackError("Settings must be nonempty single-line strings. Quote numbers and booleans in your values file.")
        values[key] = validate_value(key, setting, value)
    return values


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    logger = logging.getLogger("gamestack")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if args.debug else logging.WARNING)
    logger.propagate = False
    try:
        if args.command == "pack":
            pack = load_pack(args.file)
            print(f"GamePack is valid (schema {pack['schema_version']}). Image availability and game behavior have not been tested.")
            return 0
        runtime = Runtime(args.root)
        if args.command == "backup":
            from . import backup
            parts = args.arguments
            if len(parts) == 1:
                instance = parts[0]
                print("Backup will stop a running server temporarily and restart it after capture.", flush=True)
                artifact, state = runtime.backup(instance)
                print(f"Verified backup: {artifact.stem}\nLocation: {artifact}\n{instance}: {state}")
            elif len(parts) == 2 and parts[0] == "list":
                records = backup.list_backups(runtime.directory(parts[1]))
                print("Completed backups (listing does not recheck integrity):")
                for record in records:
                    print(f"  {record.id}  {record.created_utc}  {record.size} bytes")
                if not records:
                    print("No completed backups found.")
            elif len(parts) == 3 and parts[0] == "verify":
                backup.verify(backup.selected(runtime.directory(parts[1]), parts[2]), parts[1])
                print("Backup integrity verified. This does not authenticate the archive or prove restoration.")
            else:
                raise GameStackError("Use gamestack backup INSTANCE, backup list INSTANCE, or backup verify INSTANCE BACKUP-ID.")
            return 0
        if args.command == "rm":
            directory, _ = runtime.inspect(args.instance)
            if not args.yes:
                if not sys.stdin.isatty():
                    raise GameStackError("Removal needs confirmation. Run interactively or pass --yes to stop and remove the container while retaining its files.")
                answer = input(f"Stop and remove {args.instance}? Files will remain at {directory}. [y/N] ")
                if answer.strip().lower() not in ("y", "yes"):
                    print("Removal cancelled.")
                    return 0
            retained = runtime.remove(args.instance)
            print(f"Removed {args.instance}. World data, backups, and configuration retained at: {retained}")
            return 0
        if args.command == "list":
            instances = runtime.list_instances()
            if instances:
                print("Configured instances:")
                for instance in instances:
                    print(f"  {instance}: {runtime.quick_status(instance)}")
                print("Use an instance name with gamestack start, stop, restart, or status.")
            else:
                print("No configured instances found. Use gamestack install --help to configure a GamePack.")
            return 0
        if args.command == "install":
            pack = load_pack(args.file)
            instance = args.name or pack["id"]
            values = configure(pack, read_yaml(args.values) if args.values else {})
            address = bind_address(args.bind_address or "127.0.0.1")
            if pack["schema_version"] == 2 and args.bind_address is None and sys.stdin.isatty():
                answer = input("Allow players on other machines to connect? This exposes game ports on all IPv4 interfaces, including public interfaces if present. Router/firewall settings stay under your control. [y/N] ")
                if answer.strip().lower() in ("y", "yes"):
                    address = "0.0.0.0"
            if not args.prepare_only:
                runtime.doctor()
            directory = runtime.prepare(pack, instance, values, address)
            print(f"Prepared {instance}. World folder: {directory / 'data'}")
            if not args.prepare_only:
                print(f"{instance}: {runtime.lifecycle('start', instance)}")
            return 0
        if args.command == "doctor":
            if args.instance:
                runtime.inspect(args.instance)
            runtime.doctor()
            print("Host prerequisites passed" + ("; instance configuration and world folder passed." if args.instance else "."))
            return 0
        print(f"{args.instance}: {runtime.lifecycle(args.command, args.instance)}")
        return 0
    except GameStackError as exc:
        print(f"GameStack: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        logger.debug("Filesystem operation failed type=%s errno=%s", type(exc).__name__, exc.errno)
        print("GameStack cannot access its files. Check free disk space and directory permissions, then retry. Any partial installation was retained for inspection.", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("GameStack operation interrupted. Check status before retrying; any created files were retained.", file=sys.stderr)
        return 130
    finally:
        logger.removeHandler(handler)
        handler.close()

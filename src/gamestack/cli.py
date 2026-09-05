"""Beginner-facing commands; logging and interactive input live here."""
import argparse
import getpass
import logging
from pathlib import Path
import sys

from . import __version__
from .pack import GameStackError, load_pack, read_yaml, string
from .runtime import Runtime


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="gamestack", description="Manage local game servers using GamePacks (experimental).")
    result.add_argument("--version", action="version", version=__version__)
    result.add_argument("--debug", action="store_true")
    result.add_argument("--root", type=Path, default=Path.home() / ".local" / "share" / "gamestack", help="Dedicated instance storage directory")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List configured instances with container state and health")
    remove = commands.add_parser("rm", help="Remove an instance's container, retaining worlds, backups, and configuration")
    remove.add_argument("instance")
    remove.add_argument("--yes", action="store_true", help="Confirm container removal without prompting")
    pack = commands.add_parser("pack", help="Check a GamePack before installation")
    sub = pack.add_subparsers(dest="pack_command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("file", type=Path)
    install = commands.add_parser("install", help="Configure a local GamePack and start its server")
    install.add_argument("file", type=Path)
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
    values = {}
    for key, setting in pack["environment"].items():
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
        values[key] = value
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
            load_pack(args.file)
            print("GamePack is valid (schema 1). Image availability and game behavior have not been tested.")
            return 0
        runtime = Runtime(args.root)
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
            if not args.prepare_only:
                runtime.doctor()
            directory = runtime.prepare(pack, instance, values)
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

"""Strict, versioned GamePack loading; no executable YAML or templating."""
from pathlib import Path, PurePosixPath
import re

import yaml


class GameStackError(Exception):
    """An expected error safe to display to the user."""


class UniqueLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise GameStackError("YAML keys must be unique strings. Check your configuration.")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def read_yaml(path: Path) -> dict:
    try:
        if path.stat().st_size > 256_000:
            raise GameStackError("Configuration is too large. Keep it below 256 KB.")
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueLoader)
    except (OSError, UnicodeError, yaml.YAMLError, RecursionError) as exc:
        # Parser errors can contain entire secret-bearing source lines.
        raise GameStackError("Cannot read configuration. Check the file, permissions, and YAML syntax.") from exc
    if not isinstance(value, dict):
        raise GameStackError("Configuration must be a YAML mapping. Check the documented format.")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GameStackError(message + " Check the GamePack format in docs/gamepacks.md.")


def fields(value: dict, required: set[str], optional: set[str] = frozenset()) -> None:
    require(isinstance(value, dict), "Expected a mapping.")
    require(required <= value.keys() and value.keys() <= required | optional,
            "Missing or unknown configuration fields.")


def name(value: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,39}", value) is not None,
            "Names must start with a lowercase letter and contain up to 40 lowercase letters, digits, or hyphens.")
    return value


def string(value: object) -> bool:
    return isinstance(value, str) and bool(value) and all(ord(c) >= 32 for c in value)


def validate(pack: dict) -> dict:
    fields(pack, {"schema_version", "id", "version", "name", "image", "data_path", "ports", "environment", "healthcheck", "stop_timeout"}, {"user"})
    require(type(pack["schema_version"]) is int and pack["schema_version"] == 1, "Unsupported schema version.")
    name(pack["id"])
    require(string(pack["name"]) and string(pack["version"]), "Name and version must be nonempty strings.")
    require(isinstance(pack["image"], str) and re.fullmatch(r"[a-z0-9][a-z0-9./:_-]*@sha256:[a-f0-9]{64}", pack["image"]) is not None,
            "Image must be pinned to a sha256 digest.")
    target = pack["data_path"]
    require(string(target), "Storage path must be a string.")
    p = PurePosixPath(target)
    require(p.is_absolute() and len(p.parts) > 1 and ".." not in p.parts and str(p) == target and "$" not in target,
            "Storage must use a normalized absolute container path below root.")
    require(target != "/var/run/docker.sock", "The container cannot mount the Docker socket.")
    require(type(pack["stop_timeout"]) is int and 10 <= pack["stop_timeout"] <= 600, "Shutdown timeout must be 10–600 seconds.")
    if "user" in pack:
        require(isinstance(pack["user"], str) and re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", pack["user"]) is not None,
                "User must be a non-root numeric UID:GID string.")
    require(isinstance(pack["ports"], list), "Ports must be a list.")
    seen = set()
    for port in pack["ports"]:
        fields(port, {"host", "container", "protocol", "purpose"})
        require(all(type(port[k]) is int and 1 <= port[k] <= 65535 for k in ("host", "container")), "Port numbers must be 1–65535.")
        require(port["protocol"] in ("tcp", "udp") and string(port["purpose"]), "Ports need a protocol and purpose.")
        binding = (port["host"], port["protocol"])
        require(binding not in seen, "Duplicate host port.")
        seen.add(binding)
    require(isinstance(pack["environment"], dict), "Environment must be a mapping.")
    for key, setting in pack["environment"].items():
        require(re.fullmatch(r"[A-Z_][A-Z0-9_]*", key) is not None, "Invalid environment variable name.")
        fields(setting, {"prompt", "secret"}, {"default"})
        require(string(setting["prompt"]) and type(setting["secret"]) is bool, "Settings require a prompt and boolean secret flag.")
        if "default" in setting:
            require(string(setting["default"]) and not setting["secret"], "Defaults must be nonempty strings and cannot contain secrets.")
    health = pack["healthcheck"]
    require(isinstance(health, list) and bool(health) and all(string(v) for v in health), "Healthcheck must be a nonempty argument list.")
    return pack


def load_pack(path: Path) -> dict:
    return validate(read_yaml(path))

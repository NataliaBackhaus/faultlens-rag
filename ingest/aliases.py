import re
from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.version import Version
from ruamel.yaml import YAML

ALIASES_PATH = Path("corpus/aliases.yaml")


def _normalize(s: str) -> str:
    return re.sub(r"[\s\-.]", "", s).lower()


def load_aliases(path: Path = ALIASES_PATH) -> dict[str, str]:
    """Return {normalized_alias: doc_id} from aliases.yaml."""
    yaml = YAML()
    data = yaml.load(path)
    mapping = {}
    for doc_id, entry in data.items():
        for alias in entry["aliases"]:
            mapping[_normalize(alias)] = doc_id
    return mapping


def resolve(query: str, aliases: dict[str, str] | None = None) -> str | None:
    """Resolve a model string to a doc_id, or None if unknown."""
    if aliases is None:
        aliases = load_aliases()

    norm_query = _normalize(query)
    model = aliases.get(norm_query)
    return model


def parse_version(version_str: str) -> Version:
    """Parse a version string into a comparable Version object."""
    return Version(version_str)


def firmware_in_range(version: str, range_spec: str | None) -> bool:
    """Return True if version satisfies range_spec, or if range_spec is None"""
    if range_spec is None:
        return True
    return SpecifierSet(range_spec).contains(version)

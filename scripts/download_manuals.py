import hashlib
from pathlib import Path

import httpx
from ruamel.yaml import YAML

MANIFEST_PATH = Path("corpus/manifest.yaml")
MANUALS_DIR = Path("data/manuals")


def sha256_of_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def download(manual: dict) -> str:
    """Download PDF, return its sha256."""
    path = MANUALS_DIR / f"{manual['id']}.pdf"
    hasher = hashlib.sha256()

    with httpx.stream("GET", manual["url"], follow_redirects=True, timeout=60) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=8192):
                hasher.update(chunk)
                f.write(chunk)

    return hasher.hexdigest()


def main():
    yaml = YAML()
    manifest = yaml.load(MANIFEST_PATH)
    MANUALS_DIR.mkdir(parents=True, exist_ok=True)

    for manual in manifest["manuals"]:
        path = MANUALS_DIR / f"{manual['id']}.pdf"
        stored_hash = manual.get("sha256")

        if path.exists() and sha256_of_file(path) == stored_hash:
            print(f"skip {manual['id']}")
            continue

        print(f"downloading {manual['id']}...")
        sha = download(manual)
        manual["sha256"] = sha
        print(f"done - sha256: {sha[:12]}...")

    with open(MANIFEST_PATH, "w") as f:
        yaml.dump(manifest, f)


if __name__ == "__main__":
    main()

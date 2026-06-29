#!/usr/bin/env python3
"""Generate SHA256 hashes for all output artifacts."""

import hashlib
import json
import os
import time
from pathlib import Path

RESULTS_DIR = Path("/home/student/SGI-Persistence/results")
HASHES_DIR = RESULTS_DIR / "hashes"


def hash_file(filepath: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_artifacts() -> list:
    """Collect all output artifacts to hash."""
    artifacts = []

    # Figures
    fig_dir = RESULTS_DIR / "figures"
    if fig_dir.exists():
        for ext in ["*.pdf", "*.svg", "*.png"]:
            for f in fig_dir.glob(ext):
                artifacts.append(f)

    # Tables
    tbl_dir = RESULTS_DIR / "tables"
    if tbl_dir.exists():
        for ext in ["*.csv", "*.tex", "*.md"]:
            for f in tbl_dir.glob(ext):
                artifacts.append(f)

    # Canonical JSON results
    for json_file in RESULTS_DIR.rglob("*.json"):
        if "hashes" not in str(json_file):
            artifacts.append(json_file)

    return sorted(artifacts)


def main():
    HASHES_DIR.mkdir(parents=True, exist_ok=True)

    artifacts = collect_artifacts()
    print(f"Hashing {len(artifacts)} artifacts...")

    hashes = []
    for artifact in artifacts:
        rel_path = artifact.relative_to(RESULTS_DIR)
        sha256 = hash_file(artifact)
        hashes.append({
            "file": str(rel_path),
            "sha256": sha256,
            "size_bytes": artifact.stat().st_size,
            "generated_by": "SGI-Persistence",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
        print(f"  {rel_path}: {sha256[:16]}...")

    # Save hashes
    out_path = HASHES_DIR / "artifact_hashes.json"
    with open(out_path, "w") as f:
        json.dump(hashes, f, indent=2)

    print(f"\nHashes saved to {out_path}")
    print(f"Total artifacts: {len(hashes)}")


if __name__ == "__main__":
    main()

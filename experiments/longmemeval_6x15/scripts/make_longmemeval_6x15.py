#!/usr/bin/env python3
"""Create the local 6 x 15 dataset and verify it against the ID-only manifest."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
from pathlib import Path


SEED = 20261116
CATEGORIES = [
    "single-session-user",
    "single-session-assistant",
    "single-session-preference",
    "multi-session",
    "temporal-reasoning",
    "knowledge-update",
]
TAIL_IDS = {
    "58ef2f1c",
    "caf03d32",
    "195a1a1b",
    "4100d0a0",
    "gpt4_70e84552_abs",
    "6ade9755",
    "4c36ccef",
    "e47becba",
}
EXPECTED_SOURCE_SHA256 = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=root / "data/longmemeval/longmemeval_s.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "data/longmemeval/longmemeval_s_6x15_seed20261116.json",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "manifests/question_ids.json",
    )
    args = parser.parse_args()

    source_hash = sha256(args.source)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"source SHA256 mismatch: {source_hash}")

    data = json.loads(args.source.read_text(encoding="utf-8"))
    expected = json.loads(args.manifest.read_text(encoding="utf-8"))
    rng = random.Random(SEED)
    selected = []
    observed_ids: dict[str, list[str]] = {}

    for category in CATEGORIES:
        pool = [
            item
            for item in data
            if item["question_type"] == category
            and item["question_id"] not in TAIL_IDS
        ]
        chosen = rng.sample(pool, 15)
        chosen.sort(key=lambda item: item["question_id"])
        selected.extend(chosen)
        observed_ids[category] = [item["question_id"] for item in chosen]

    ids = [item["question_id"] for item in selected]
    counts = collections.Counter(item["question_type"] for item in selected)
    assert len(selected) == 90
    assert len(set(ids)) == 90
    assert set(ids).isdisjoint(TAIL_IDS)
    assert all(counts[category] == 15 for category in CATEGORIES)
    if observed_ids != expected["ids_by_category"]:
        raise SystemExit("sampled question IDs do not match the checked-in manifest")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(selected, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"selected={len(selected)} unique={len(set(ids))} tail_overlap=0")
    print(f"source_sha256={source_hash}")
    print(f"output_sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

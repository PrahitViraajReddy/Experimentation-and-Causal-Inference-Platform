"""Generate a small, reproducible synthetic A/B reference dataset."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate(seed: int = 42, sample_size_per_arm: int = 500) -> pd.DataFrame:
    if sample_size_per_arm < 10:
        raise ValueError("sample_size_per_arm must be at least 10")
    rng = np.random.default_rng(seed)
    rows = []
    for variant, probability, mean_revenue in (
        ("control", 0.10, 18.0),
        ("treatment", 0.13, 19.5),
    ):
        converted = rng.binomial(1, probability, sample_size_per_arm)
        revenue = np.where(
            converted == 1,
            rng.gamma(shape=2.0, scale=mean_revenue / 2.0, size=sample_size_per_arm),
            0.0,
        )
        rows.append(pd.DataFrame({
            "variant": variant,
            "converted": converted.astype(int),
            "revenue": np.round(revenue, 2),
        }))
    frame = pd.concat(rows, ignore_index=True)
    frame.insert(0, "user_id", [f"synthetic_{i + 1:05d}" for i in range(len(frame))])
    frame["seed"] = seed
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-size-per-arm", type=int, default=500)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "synthetic_ab.csv")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    generate(args.seed, args.sample_size_per_arm).to_csv(args.output, index=False)
    print(f"Wrote {2 * args.sample_size_per_arm} synthetic rows to {args.output}")


if __name__ == "__main__":
    main()

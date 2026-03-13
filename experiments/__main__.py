"""LightRAG Fact-Checking Experiment Runner

Usage:
    python -m experiments                          # Run with default config
    python -m experiments --config custom.yaml     # Custom config
    python -m experiments --phase ingest            # Only run ingestion
    python -m experiments --phase classify          # Only run classification
    python -m experiments --phase evaluate          # Only run evaluation
    python -m experiments --sample 100              # Use subset of data
    python -m experiments --mode hybrid             # Specific query mode
"""

import argparse
import sys
import os

# Add parent dir to path so we can import lightrag
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.main import run_experiment


def parse_args():
    parser = argparse.ArgumentParser(
        description="LightRAG Fact-Checking Experiment Runner"
    )
    parser.add_argument(
        "--config",
        default="experiments/config.yaml",
        help="Path to experiment config YAML (default: experiments/config.yaml)",
    )
    parser.add_argument(
        "--phase",
        choices=["ingest", "classify", "evaluate", "all"],
        default="all",
        help="Which phase to run (default: all)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Number of claims to sample (default: use all)",
    )
    parser.add_argument(
        "--mode",
        choices=["naive", "local", "global", "hybrid", "mix"],
        default=None,
        help="Override query mode (default: from config)",
    )
    parser.add_argument(
        "--working-dir",
        default=None,
        help="Override LightRAG working directory",
    )
    parser.add_argument(
        "--dataset",
        default=None,
        help="Override dataset CSV path",
    )
    # Feature flag overrides
    parser.add_argument(
        "--no-id-prompts",
        action="store_true",
        help="Disable Indonesian prompts (override config)",
    )
    parser.add_argument(
        "--no-fc-entities",
        action="store_true",
        help="Disable fact-check entity types (override config)",
    )
    parser.add_argument(
        "--enable-fc-entities",
        action="store_true",
        help="Enable fact-check entity types (override config)",
    )
    parser.add_argument(
        "--lang",
        choices=["English", "Indonesian"],
        default=None,
        help="Override summary language",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_experiment(args)

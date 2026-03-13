"""Main orchestrator for LightRAG fact-checking experiments."""

import asyncio
import json
import os
import time
import yaml
from datetime import datetime
from pathlib import Path

from experiments.ingest import ingest_evidence
from experiments.classify import classify_claims
from experiments.evaluate import evaluate_predictions


def load_config(config_path: str) -> dict:
    """Load experiment configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def apply_overrides(config: dict, args) -> dict:
    """Apply CLI argument overrides to config."""
    if args.sample is not None:
        config["evaluation"]["sample_size"] = args.sample

    if args.mode is not None:
        config["query"]["default_mode"] = args.mode

    if args.working_dir is not None:
        config["lightrag"]["working_dir"] = args.working_dir

    if args.dataset is not None:
        config["dataset"]["evidence_csv"] = args.dataset

    # Feature flag overrides
    if args.no_id_prompts:
        config["flags"]["use_indonesian_prompts"] = False

    if args.no_fc_entities:
        config["flags"]["use_factcheck_entities"] = False

    if args.enable_fc_entities:
        config["flags"]["use_factcheck_entities"] = True

    if args.lang is not None:
        config["flags"]["summary_language"] = args.lang

    return config


def resolve_dataset_path(config: dict, config_dir: str) -> str:
    """Resolve the dataset CSV path (try preprocessed first, then raw)."""
    csv_path = config["dataset"]["evidence_csv"]

    # Make relative paths relative to config file directory
    if not os.path.isabs(csv_path):
        csv_path = os.path.normpath(os.path.join(config_dir, csv_path))

    if os.path.exists(csv_path):
        return csv_path

    # Fallback to raw CSV
    raw_path = config["dataset"].get("raw_csv", "")
    if raw_path and not os.path.isabs(raw_path):
        raw_path = os.path.normpath(os.path.join(config_dir, raw_path))

    if raw_path and os.path.exists(raw_path):
        print(f"[WARN] Preprocessed CSV not found: {csv_path}")
        print(f"[WARN] Using raw CSV: {raw_path}")
        return raw_path

    raise FileNotFoundError(
        f"Dataset not found: {csv_path}\n"
        f"Run preprocessing first: python -m preprocessing --enable-all --output {csv_path}"
    )


def create_results_dir(config: dict, config_dir: str) -> str:
    """Create timestamped results directory."""
    base_dir = config["output"]["experiments_dir"]
    if not os.path.isabs(base_dir):
        base_dir = os.path.join(config_dir, base_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode = config["query"]["default_mode"]
    flags = config["flags"]

    # Build experiment tag from flags
    tag_parts = [mode]
    if flags.get("use_indonesian_prompts"):
        tag_parts.append("id-prompt")
    if flags.get("use_factcheck_entities"):
        tag_parts.append("fc-entity")
    if flags.get("summary_language", "English") == "Indonesian":
        tag_parts.append("id-lang")

    tag = "_".join(tag_parts)
    results_dir = os.path.join(base_dir, f"{timestamp}_{tag}")
    os.makedirs(results_dir, exist_ok=True)

    return results_dir


def run_experiment(args):
    """Run the full experiment pipeline."""
    config_path = args.config
    config_dir = os.path.dirname(os.path.abspath(config_path))

    # Load and apply overrides
    config = load_config(config_path)
    config = apply_overrides(config, args)

    # Resolve paths
    dataset_path = resolve_dataset_path(config, config_dir)
    results_dir = create_results_dir(config, config_dir)

    # Save effective config
    with open(os.path.join(results_dir, "config_effective.yaml"), "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print("=" * 60)
    print("LightRAG Fact-Checking Experiment")
    print("=" * 60)
    print(f"  Dataset:    {dataset_path}")
    print(f"  Results:    {results_dir}")
    print(f"  Phase:      {args.phase}")
    print(f"  Query mode: {config['query']['default_mode']}")
    print(f"  Flags:")
    for key, val in config["flags"].items():
        print(f"    {key}: {val}")
    print("=" * 60)
    print()

    phase = args.phase
    start_time = time.time()

    try:
        if phase in ("ingest", "all"):
            print("[Phase 1/3] Ingesting evidence into LightRAG...")
            t0 = time.time()
            ingest_stats = asyncio.run(
                ingest_evidence(config, dataset_path, config_dir)
            )
            print(
                f"  Ingestion complete in {time.time() - t0:.1f}s: "
                f"{ingest_stats['documents_inserted']} documents, "
                f"{ingest_stats['unique_evidence']} unique evidence items"
            )
            with open(os.path.join(results_dir, "ingest_stats.json"), "w") as f:
                json.dump(ingest_stats, f, indent=2, ensure_ascii=False)
            print()

        if phase in ("classify", "all"):
            print("[Phase 2/3] Classifying claims...")
            t0 = time.time()
            predictions = asyncio.run(
                classify_claims(config, dataset_path, config_dir)
            )
            print(
                f"  Classification complete in {time.time() - t0:.1f}s: "
                f"{len(predictions)} claims classified"
            )
            # Save predictions
            pred_path = os.path.join(results_dir, "predictions.json")
            with open(pred_path, "w", encoding="utf-8") as f:
                json.dump(predictions, f, indent=2, ensure_ascii=False)
            print()

        if phase in ("evaluate", "all"):
            print("[Phase 3/3] Evaluating predictions...")
            # Load predictions if not from classify phase
            if phase == "evaluate":
                # Look for most recent predictions
                pred_path = os.path.join(results_dir, "predictions.json")
                if not os.path.exists(pred_path):
                    # Try to find in parent results dir
                    base_dir = config["output"]["experiments_dir"]
                    if not os.path.isabs(base_dir):
                        base_dir = os.path.join(config_dir, base_dir)
                    latest = sorted(Path(base_dir).iterdir())[-1]
                    pred_path = os.path.join(latest, "predictions.json")

                with open(pred_path, "r", encoding="utf-8") as f:
                    predictions = json.load(f)

            metrics = evaluate_predictions(predictions, config)
            print(f"  Evaluation results:")
            for metric, value in metrics.items():
                if isinstance(value, float):
                    print(f"    {metric}: {value:.4f}")
                else:
                    print(f"    {metric}: {value}")

            # Save metrics
            with open(os.path.join(results_dir, "metrics.json"), "w") as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"\n[ERROR] Experiment failed: {e}")
        import traceback

        traceback.print_exc()
        # Save error
        with open(os.path.join(results_dir, "error.txt"), "w") as f:
            traceback.print_exc(file=f)
        raise

    elapsed = time.time() - start_time
    print()
    print(f"Total experiment time: {elapsed:.1f}s")
    print(f"Results saved to: {results_dir}")

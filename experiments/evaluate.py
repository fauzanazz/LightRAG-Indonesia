"""Evaluation metrics for fact-checking classification.

Computes accuracy, precision, recall, F1-macro, F1-weighted,
and per-class metrics for Supported/Refuted classification.
"""

from collections import Counter


def evaluate_predictions(predictions: list[dict], config: dict) -> dict:
    """Compute evaluation metrics from predictions.

    Args:
        predictions: list of dicts with 'gold_label' and 'prediction' keys
        config: experiment config (for metric selection)

    Returns:
        dict with computed metrics
    """
    gold_labels = [p["gold_label"] for p in predictions]
    pred_labels = [p["prediction"] for p in predictions]

    # Unique classes
    classes = sorted(set(gold_labels + pred_labels))

    # Build confusion matrix
    confusion = {}
    for cls in classes:
        confusion[cls] = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}

    for gold, pred in zip(gold_labels, pred_labels):
        for cls in classes:
            if gold == cls and pred == cls:
                confusion[cls]["tp"] += 1
            elif gold != cls and pred == cls:
                confusion[cls]["fp"] += 1
            elif gold == cls and pred != cls:
                confusion[cls]["fn"] += 1
            else:
                confusion[cls]["tn"] += 1

    # Per-class metrics
    per_class = {}
    for cls in classes:
        tp = confusion[cls]["tp"]
        fp = confusion[cls]["fp"]
        fn = confusion[cls]["fn"]

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        support = tp + fn

        per_class[cls] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": support,
        }

    # Accuracy
    correct = sum(1 for g, p in zip(gold_labels, pred_labels) if g == p)
    accuracy = correct / len(predictions) if predictions else 0.0

    # F1-macro (unweighted average of per-class F1)
    f1_macro = sum(pc["f1"] for pc in per_class.values()) / len(classes) if classes else 0.0

    # F1-weighted (weighted by support)
    total_support = sum(pc["support"] for pc in per_class.values())
    f1_weighted = (
        sum(pc["f1"] * pc["support"] for pc in per_class.values()) / total_support
        if total_support > 0
        else 0.0
    )

    # Prediction distribution
    pred_dist = dict(Counter(pred_labels))
    gold_dist = dict(Counter(gold_labels))

    metrics = {
        "total_predictions": len(predictions),
        "accuracy": round(accuracy, 4),
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "per_class": per_class,
        "prediction_distribution": pred_dist,
        "gold_distribution": gold_dist,
        "confusion_summary": {
            cls: {
                "tp": confusion[cls]["tp"],
                "fp": confusion[cls]["fp"],
                "fn": confusion[cls]["fn"],
            }
            for cls in classes
        },
    }

    return metrics

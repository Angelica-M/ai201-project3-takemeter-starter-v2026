"""Criterion 2 in one go: ONE macro-F1 number per seed, with a 95% bootstrap confidence interval.

Run it after the notebook has written its results file (unit 6, section 6):

    python macro_f1_ci.py                                   # reads results_three_seeds_before.json
    python macro_f1_ci.py --results results.json            # a single run (seed 42) also works
    python macro_f1_ci.py --results results_three_seeds_after.json

Why this exists: with ~31 posts in a test split, a per-label F1 is mostly noise, and doing 21 of them by hand is
a lot of work for numbers nobody can trust. So criteria.md asks for ONE number: the macro F1 (the average of
per-label F1s) over a fixed, pre-declared set of core technical labels that have enough posts in the dataset.
This script computes it from the confusion matrix the notebook already saved (no retraining, no model needed),
and bootstraps it to show how much of that number is just which 31 posts happened to land in the test split.
"""
import argparse
import json
import sys

import numpy as np
import pandas as pd

# The core technical estimating labels Criterion 2 is about. Fixed BEFORE looking at results, on purpose: picking
# labels after seeing their scores is how a standard quietly moves.
CORE_TECHNICAL_LABELS = [
    "general_construction_non_mechanical",
    "software_benchmarking_technical_workflow",
    "emerging_ai_automation_tools",
    "bid_strategy_scope_gaps_gc_relations",
    "enterprise_erp_bidding_platforms",
]
MIN_POSTS_IN_DATASET = 10   # a label needs at least this many posts in the WHOLE dataset to be judged
F1_TARGET = 0.60            # Criterion 2: macro F1 must reach this on EVERY seed...
MAX_STD_ACROSS_SEEDS = 0.05 # ...and the seeds must agree to within this standard deviation
N_BOOTSTRAP = 2000          # resamples for the confidence interval
CI_LEVEL = 95               # a 95% interval = the middle 95% of the bootstrap results


def confusion_to_pairs(confusion, labels):
    """The notebook saves the confusion matrix as {true: {predicted: count}}. Turn it back into one
    (true_index, predicted_index) pair per test post, which is what a bootstrap needs to resample."""
    index = {label: i for i, label in enumerate(labels)}
    pairs = []
    for true_label, row in confusion.items():
        for predicted_label, count in row.items():
            pairs.extend([(index[true_label], index[predicted_label])] * int(count))
    return np.array(pairs, dtype=int).reshape(-1, 2)


def macro_f1_over(pairs, n_labels, scored):
    """Macro F1 over the label indexes in `scored`, from (true, predicted) pairs.

    Per-label F1 = 2*TP / (2*TP + FP + FN). A label with no true posts AND no predictions in this sample has no F1
    at all (0/0), so it is left out of the average rather than counted as 0 or 1. A label that has no true posts
    but was predicted wrongly scores 0, which is right: the model made mistakes on it."""
    if len(pairs) == 0:
        return float("nan")
    flat = np.bincount(pairs[:, 0] * n_labels + pairs[:, 1], minlength=n_labels * n_labels)
    matrix = flat.reshape(n_labels, n_labels)  # rows = true, columns = predicted
    f1s = []
    for label in scored:
        tp = matrix[label, label]
        fn = matrix[label].sum() - tp
        fp = matrix[:, label].sum() - tp
        denominator = 2 * tp + fp + fn
        if denominator > 0:
            f1s.append(2 * tp / denominator)
    return float(np.mean(f1s)) if f1s else float("nan")


def bootstrap_ci(pairs, n_labels, scored, rng):
    """Resample the test posts WITH replacement, recompute the macro F1 each time, and take the middle 95%.
    The width of that range says how much the number moves just from which posts were in the test split."""
    values = []
    for _ in range(N_BOOTSTRAP):
        sample = pairs[rng.integers(0, len(pairs), len(pairs))]
        values.append(macro_f1_over(sample, n_labels, scored))
    values = np.array([v for v in values if not np.isnan(v)])
    if len(values) == 0:
        return float("nan"), float("nan")
    tail = (100 - CI_LEVEL) / 2
    return float(np.percentile(values, tail)), float(np.percentile(values, 100 - tail))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", default="results_three_seeds_before.json", help="notebook results file")
    parser.add_argument("--data", default="data/labels.csv", help="the full labelled dataset (for label counts)")
    parser.add_argument("--rng-seed", type=int, default=0, help="seed for the bootstrap itself (fixed = repeatable)")
    args = parser.parse_args()

    with open(args.results, encoding="utf-8") as f:
        results = json.load(f)
    if isinstance(results, dict):  # results.json holds one run; the three-seed files hold a list of runs
        results = [results]

    counts = pd.read_csv(args.data)["label"].value_counts()
    scored_names = []
    for label in CORE_TECHNICAL_LABELS:
        n = int(counts.get(label, 0))
        if n >= MIN_POSTS_IN_DATASET:
            scored_names.append(label)
        else:
            print(f"[left out] {label}: only {n} posts in the dataset (needs {MIN_POSTS_IN_DATASET}).")
    if not scored_names:
        sys.exit("No core technical label has enough posts to be judged.")
    print(f"Scoring {len(scored_names)} labels: {', '.join(f'{l} ({int(counts[l])})' for l in scored_names)}\n")

    labels = list(results[0]["confusion"].keys())  # same order the notebook used
    scored = [labels.index(l) for l in scored_names]
    rng = np.random.default_rng(args.rng_seed)

    per_seed = []
    print(f"{'seed':>6} | {'test posts':>10} | {'macro F1':>8} | {CI_LEVEL}% bootstrap interval")
    print("-" * 56)
    for r in results:
        pairs = confusion_to_pairs(r["confusion"], labels)
        value = macro_f1_over(pairs, len(labels), scored)
        low, high = bootstrap_ci(pairs, len(labels), scored, rng)
        per_seed.append(value)
        print(f"{r['seed']:>6} | {len(pairs):>10} | {value:>8.3f} | [{low:.3f}, {high:.3f}]")

    print()
    values = np.array(per_seed)
    if len(values) > 1:
        std = float(np.std(values, ddof=1))  # sample standard deviation across seeds
        print(f"mean macro F1 across seeds: {values.mean():.3f}   standard deviation across seeds: {std:.3f}")
        print(f"target: every seed >= {F1_TARGET} and standard deviation < {MAX_STD_ACROSS_SEEDS}")
        ok_f1 = bool((values >= F1_TARGET).all())
        ok_std = std < MAX_STD_ACROSS_SEEDS
        print(f"  every seed >= {F1_TARGET}: {'yes' if ok_f1 else 'NO'}   spread < {MAX_STD_ACROSS_SEEDS}: {'yes' if ok_std else 'NO'}")
    print("\nHow to read the interval: if it contains the target (0.60), this seed cannot honestly be called a pass")
    print("or a fail - the test split is too small to tell. Report that as a finding rather than rounding it up or down.")


if __name__ == "__main__":
    main()

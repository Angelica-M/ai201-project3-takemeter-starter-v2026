#!/usr/bin/env python3
"""Criterion 4 in one command: Cohen's kappa between your labels and the staff labels on the same 30 posts.

WHEN TO USE IT
    Unit 6, after you have labelled the 30 staff posts (my_staff_labels.csv) and your TF has sent
    data/staff_labels.csv. Run it right after `python agreement.py`.

HOW TO RUN IT (same inputs and flags as agreement.py, so the two always look at the same posts)
    python kappa.py
    python kappa.py --staff-posts data/staff_posts.csv --staff-labels data/staff_labels.csv --mine my_staff_labels.csv
    python kappa.py --staff data/staff_combined.csv --mine my_staff_labels.csv

WHY A SCRIPT, WHEN THE OTHER CRITERIA NEED NONE
    agreement.py reports the raw agreement RATE (how often you matched). Criterion 4 asks for Cohen's kappa, which is
    that rate corrected for the agreement two annotators would get by chance alone. You cannot get kappa back from
    the rate: it needs the full list of label pairs. This script reuses agreement.py's own loading and matching code
    (so the posts are paired exactly the same way) and adds the chance correction.

WHAT KAPPA MEANS
    kappa = (observed agreement - chance agreement) / (1 - chance agreement)
    1.0 = perfect agreement, 0 = no better than chance, negative = worse than chance. Criterion 4 asks for >= 0.70.
    With only 30 posts the number is shaky, so a 95% bootstrap confidence interval is printed next to it: if the
    interval contains 0.70 you cannot honestly call the criterion met or missed.
"""
import argparse
import sys

import numpy as np
import pandas as pd

import agreement  # the starter's own loader/matcher: guarantees we pair the posts exactly as agreement.py does

KAPPA_TARGET = 0.70   # Criterion 4 in criteria.md
N_BOOTSTRAP = 2000    # resamples for the confidence interval
CI_LEVEL = 95


def kappa_from_pairs(a, b):
    """Cohen's kappa for two equally long lists of labels (a[i] and b[i] are the two annotators on post i)."""
    labels = sorted(set(a) | set(b))
    index = {label: i for i, label in enumerate(labels)}
    matrix = np.zeros((len(labels), len(labels)))
    for x, y in zip(a, b):
        matrix[index[x], index[y]] += 1
    n = matrix.sum()
    observed = np.trace(matrix) / n                                   # share of posts where both picked the same label
    expected = (matrix.sum(axis=1) @ matrix.sum(axis=0)) / n ** 2      # share they would match by chance, from each one's label habits
    if expected == 1:                                                  # both always used one single label: kappa is undefined
        return float("nan"), observed, expected
    return (observed - expected) / (1 - expected), observed, expected


def bootstrap_ci(a, b, rng):
    """Resample the 30 posts with replacement 2,000 times, recompute kappa each time, keep the middle 95%."""
    a, b = np.array(a), np.array(b)
    values = []
    for _ in range(N_BOOTSTRAP):
        pick = rng.integers(0, len(a), len(a))
        k, _, _ = kappa_from_pairs(a[pick], b[pick])
        if not np.isnan(k):
            values.append(k)
    if not values:
        return float("nan"), float("nan")
    tail = (100 - CI_LEVEL) / 2
    return float(np.percentile(values, tail)), float(np.percentile(values, 100 - tail))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--staff-posts", default="data/staff_posts.csv", help="the staff posts your TF gives you")
    parser.add_argument("--staff-labels", default="data/staff_labels.csv", help="the staff labels, joined to the posts on `id`")
    parser.add_argument("--staff", default=None, help="both in one file, if you already have it that way")
    parser.add_argument("--mine", default="my_staff_labels.csv", help="the same posts, labelled by you")
    parser.add_argument("--rng-seed", type=int, default=0, help="seed for the bootstrap (fixed = repeatable)")
    args = parser.parse_args()

    staff = agreement.load(args.staff, pd) if args.staff else agreement.load_pair(args.staff_posts, args.staff_labels, pd)
    mine = agreement.load(args.mine, pd)

    shared = [key for key in staff if key in mine]  # posts both of you labelled, matched on their text
    if len(shared) < 2:
        sys.exit("Fewer than 2 posts matched between the two files, so kappa cannot be computed. "
                 "Posts are matched on their text, so paste it unchanged.")
    staff_labels = [staff[key][1] for key in shared]
    my_labels = [mine[key][1] for key in shared]

    kappa, observed, expected = kappa_from_pairs(staff_labels, my_labels)
    low, high = bootstrap_ci(staff_labels, my_labels, np.random.default_rng(args.rng_seed))

    print(f"Compared {len(shared)} posts.\n")
    print(f"  observed agreement           {observed:.3f}   (same as agreement.py's rate)")
    print(f"  agreement expected by chance {expected:.3f}")
    print(f"  Cohen's kappa                {kappa:.3f}   {CI_LEVEL}% bootstrap interval [{low:.3f}, {high:.3f}]")
    print(f"  Criterion 4 target           >= {KAPPA_TARGET}   ->   {'MET' if kappa >= KAPPA_TARGET else 'MISSED'}")
    if low <= KAPPA_TARGET <= high:
        print("\nThe interval contains the target, so with this few posts the call is too close to make honestly.")
        print("Report the number AND the interval in your README rather than a bare MET/MISSED.")


if __name__ == "__main__":
    main()

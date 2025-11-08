#!/usr/bin/env python3
import argparse
import math
from typing import List, Sequence


def precision_at_k(rels: Sequence[int], k: int) -> float:
    k = min(k, len(rels))
    if k <= 0:
        return 0.0
    return sum(rels[:k]) / k


def recall_at_k(rels: Sequence[int], k: int, num_relevant_total: int) -> float:
    if num_relevant_total <= 0:
        return 0.0
    return sum(rels[:k]) / num_relevant_total


def average_precision(rels: Sequence[int]) -> float:
    num_rel = 0
    precisions: List[float] = []
    for i, r in enumerate(rels, start=1):
        if r:
            num_rel += 1
            precisions.append(sum(rels[:i]) / i)
    return sum(precisions) / num_rel if num_rel > 0 else 0.0


def mean_average_precision(list_of_rels: Sequence[Sequence[int]]) -> float:
    if not list_of_rels:
        return 0.0
    return sum(average_precision(rels) for rels in list_of_rels) / len(list_of_rels)


def dcg_at_k(gains: Sequence[float], k: int) -> float:
    k = min(k, len(gains))
    dcg = 0.0
    for i in range(k):
        dcg += gains[i] / math.log2(i + 2)
    return dcg


def ndcg_at_k(gains: Sequence[float], k: int) -> float:
    ideal = sorted(gains, reverse=True)
    denom = dcg_at_k(ideal, k)
    if denom <= 0:
        return 0.0
    return dcg_at_k(gains, k) / denom


def mrr(list_of_rels: Sequence[Sequence[int]]) -> float:
    if not list_of_rels:
        return 0.0
    rr_sum = 0.0
    for rels in list_of_rels:
        rr = 0.0
        for i, r in enumerate(rels, start=1):
            if r:
                rr = 1.0 / i
                break
        rr_sum += rr
    return rr_sum / len(list_of_rels)


def demo():
    # Demo with simple binary relevance lists per query
    q1 = [1, 0, 1, 0, 0]  # relevant at ranks 1 and 3
    q2 = [0, 1, 0, 0, 1]  # relevant at ranks 2 and 5
    q3 = [0, 0, 0, 0, 0]  # no relevant retrieved

    print("Precision@3 q1:", precision_at_k(q1, 3))
    print("Recall@3 q1  (R=2):", recall_at_k(q1, 3, 2))
    print("AP q1:", average_precision(q1))

    print("MAP over q1,q2,q3:", mean_average_precision([q1, q2, q3]))

    # nDCG demo with graded gains
    gains = [3, 0, 2, 1, 0]
    print("nDCG@5 gains:", ndcg_at_k(gains, 5))

    print("MRR over q1,q2,q3:", mrr([q1, q2, q3]))


def main():
    parser = argparse.ArgumentParser(description="IR evaluation metrics demo")
    parser.add_argument("--demo", action="store_true", help="Run built-in demo")
    args = parser.parse_args()

    if args.demo:
        demo()
    else:
        print("Use --demo to run sample outputs, or import this module in your code.")


if __name__ == "__main__":
    main()

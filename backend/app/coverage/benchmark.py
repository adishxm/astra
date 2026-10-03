"""ASTRA - Benchmark Evaluator (Worker 01 - MVP-03).

Executes reproducible evaluation over seeded ground-truth corpora,
calculating precision, recall, and F1 to satisfy AC-06 (>=80% target).
"""

import uuid
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from app.core.config import RULESET_VERSION
from app.coverage.models import (
    BenchmarkEvaluation,
    BenchmarkMetric,
    GroundTruthLabel,
)
from app.discovery.models import Observation


class BenchmarkRunner:
    """Evaluates detection accuracy, false discovery rate, and recall on labeled fixtures."""

    BENCHMARK_CORPUS_VERSION = "2026.10-seeded-ground-truth-v1"

    def evaluate(
        self,
        ground_truth: List[GroundTruthLabel],
        observations: List[Observation],
        benchmark_id: Optional[str] = None,
    ) -> BenchmarkEvaluation:
        """Adjudicate observations against pre-registered ground truth labels."""
        bid = benchmark_id or str(uuid.uuid4())

        # Ground truth expectations: set of (relative_path, normalized_algo)
        expected_items: Set[Tuple[str, str]] = set()
        for gt in ground_truth:
            if not gt.is_negative_fixture:
                expected_items.add((gt.relative_path, gt.expected_algorithm.upper()))

        # Detected items from observations
        detected_items: Set[Tuple[str, str]] = set()
        for obs in observations:
            algo = (obs.algorithm or "UNKNOWN").upper()
            detected_items.add((obs.relative_path, algo))

        # Adjudication
        true_positives = 0
        false_positives = 0
        false_negatives = 0

        # Classes breakdown
        classes_data: Dict[str, Dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

        # Match detected against expected
        for (rel_path, algo) in detected_items:
            # Check for exact or normalized match
            matched = False
            for (exp_path, exp_algo) in expected_items:
                if rel_path == exp_path and (algo == exp_algo or exp_algo in algo or algo in exp_algo):
                    matched = True
                    break

            if matched:
                true_positives += 1
                classes_data[algo]["tp"] += 1
            else:
                false_positives += 1
                classes_data[algo]["fp"] += 1

        # Match expected against detected to find false negatives
        for (exp_path, exp_algo) in expected_items:
            found = False
            for (rel_path, algo) in detected_items:
                if rel_path == exp_path and (algo == exp_algo or exp_algo in algo or algo in exp_algo):
                    found = True
                    break
            if not found:
                false_negatives += 1
                classes_data[exp_algo]["fn"] += 1

        precision = (
            round(true_positives / (true_positives + false_positives), 4)
            if (true_positives + false_positives) > 0
            else 0.0
        )
        recall = (
            round(true_positives / (true_positives + false_negatives), 4)
            if (true_positives + false_negatives) > 0
            else 0.0
        )
        f1 = (
            round(2 * (precision * recall) / (precision + recall), 4)
            if (precision + recall) > 0
            else 0.0
        )

        ac06_achieved = precision >= 0.80 and recall >= 0.80

        per_class_metrics: Dict[str, BenchmarkMetric] = {}
        for cls_name, counts in classes_data.items():
            tp = counts["tp"]
            fp = counts["fp"]
            fn = counts["fn"]
            p = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
            r = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
            score = round(2 * (p * r) / (p + r), 4) if (p + r) > 0 else 0.0
            per_class_metrics[cls_name] = BenchmarkMetric(
                target_class=cls_name,
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                precision=p,
                recall=r,
                f1_score=score,
                target_met=(p >= 0.80 and r >= 0.80),
            )

        return BenchmarkEvaluation(
            benchmark_id=bid,
            corpus_version=self.BENCHMARK_CORPUS_VERSION,
            ruleset_version=RULESET_VERSION,
            total_fixtures=len(ground_truth),
            total_expected_findings=len(expected_items),
            total_detected_findings=len(detected_items),
            overall_precision=precision,
            overall_recall=recall,
            overall_f1=f1,
            ac06_target_achieved=ac06_achieved,
            per_class_metrics=per_class_metrics,
        )

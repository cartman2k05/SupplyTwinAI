from typing import List, Set, Dict, Any

class EvaluationMetricsEngine:
    """
    Programmatic Evaluation Metric Calculation Engine (DECISIONS.md §5).
    Computes precision, recall, F1, hallucination rate, grounding rate,
    recommendation validity, and latency statistics across evaluation runs.
    """

    @staticmethod
    def calculate_precision_recall(
        predicted_entities: List[str],
        ground_truth_entities: List[str]
    ) -> Dict[str, float]:
        if not predicted_entities:
            return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0}

        pred_set = set(predicted_entities)
        gt_set = set(ground_truth_entities)

        intersection = pred_set.intersection(gt_set)
        precision = len(intersection) / len(pred_set) if pred_set else 0.0
        recall = len(intersection) / len(gt_set) if gt_set else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        }

    @staticmethod
    def calculate_hallucination_rate(
        cited_entity_ids: List[str],
        valid_entity_ids: Set[str]
    ) -> float:
        if not cited_entity_ids:
            return 0.0

        invalid_count = sum(1 for eid in cited_entity_ids if eid not in valid_entity_ids)
        return round(invalid_count / len(cited_entity_ids), 4)

    @staticmethod
    def calculate_grounding_rate(
        cited_facts_count: int,
        total_claims_count: int
    ) -> float:
        if total_claims_count == 0:
            return 1.0
        return round(min(1.0, cited_facts_count / total_claims_count), 4)

    @staticmethod
    def calculate_recommendation_validity(
        proposed_action_type: str,
        acceptable_action_class: str
    ) -> float:
        if not proposed_action_type:
            return 0.0
        return 1.0 if proposed_action_type == acceptable_action_class else 0.0

    @staticmethod
    def calculate_latency_stats(latencies_ms: List[float]) -> Dict[str, float]:
        if not latencies_ms:
            return {"mean_ms": 0.0, "p95_ms": 0.0, "max_ms": 0.0}

        sorted_lat = sorted(latencies_ms)
        mean_val = sum(sorted_lat) / len(sorted_lat)
        p95_idx = int(0.95 * len(sorted_lat))
        p95_idx = min(p95_idx, len(sorted_lat) - 1)

        return {
            "mean_ms": round(mean_val, 2),
            "p95_ms": round(sorted_lat[p95_idx], 2),
            "max_ms": round(sorted_lat[-1], 2)
        }

metrics_engine = EvaluationMetricsEngine()

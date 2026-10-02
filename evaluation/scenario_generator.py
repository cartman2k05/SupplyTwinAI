import random
from typing import List, Dict, Any

class ScenarioGenerator:
    """
    Generates 60+ synthetic disruption evaluation scenarios with ground-truth labels
    for programmatic evaluation of Configurations A, B, and C (DECISIONS.md §5).
    """

    def generate_scenarios(self, seed: int = 42, target_count: int = 60) -> List[Dict[str, Any]]:
        random.seed(seed)
        scenarios = []

        categories = [
            ("SUPPLIER_OUTAGE", "supplier", "SWITCH_SUPPLIER"),
            ("SHIPMENT_DELAY", "shipment", "REROUTE_SHIPMENT"),
            ("INVENTORY_DEFICIT", "warehouse", "REALLOCATE_INVENTORY"),
            ("WEATHER_EVENT", "event", "EXPEDITE_SHIPPING"),
            ("GEOPOLITICAL_NEWS", "event", "SWITCH_SUPPLIER")
        ]

        scenarios_per_cat = target_count // len(categories)

        for cat_idx, (event_type, entity_prefix, acceptable_action) in enumerate(categories):
            for i in range(1, scenarios_per_cat + 1):
                scenario_id = f"SCENARIO-{event_type[:3]}-{i:02d}"
                entity_num = ((i - 1) % 15) + 1
                target_global_id = f"{entity_prefix}:{entity_num}"

                if entity_prefix == "supplier":
                    ground_truth_entities = [
                        target_global_id,
                        f"product:{((entity_num - 1) % 10) + 1}",
                        f"warehouse:{((entity_num - 1) % 5) + 1}",
                        f"order:{1000 + entity_num}",
                        f"shipment:{1000 + entity_num}"
                    ]
                    desc = f"Primary supplier {target_global_id} experienced factory outage and high defect rate."
                elif entity_prefix == "shipment":
                    ground_truth_entities = [
                        target_global_id,
                        f"order:{77000 + entity_num}",
                        f"vehicle:{((entity_num - 1) % 8) + 1}"
                    ]
                    desc = f"Shipment {target_global_id} delayed by severe port congestion bottleneck."
                elif entity_prefix == "warehouse":
                    ground_truth_entities = [
                        target_global_id,
                        f"product:{((entity_num - 1) % 10) + 1}",
                        f"order:{2000 + entity_num}"
                    ]
                    desc = f"Warehouse {target_global_id} safety stock buffer depleted below reorder point."
                else:
                    ground_truth_entities = [
                        f"supplier:{((entity_num - 1) % 10) + 1}",
                        f"warehouse:{((entity_num - 1) % 5) + 1}",
                        f"shipment:{1000 + entity_num}"
                    ]
                    desc = f"External {event_type.lower()} event affecting transit corridor in Region {entity_num}."

                scenarios.append({
                    "scenario_id": scenario_id,
                    "event_type": event_type,
                    "target_global_id": target_global_id,
                    "acceptable_action_class": acceptable_action,
                    "ground_truth_impacted_entities": ground_truth_entities,
                    "description": desc,
                    "severity": random.choice(["MEDIUM", "HIGH", "CRITICAL"])
                })

        return scenarios

scenario_generator = ScenarioGenerator()

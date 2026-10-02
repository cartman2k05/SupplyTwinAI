import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.app.models.event import DisruptionEvent

# Catalog of 6 standard disruption scenarios per SRS §4.6 REQ-1 & REQ-2
SCENARIO_CATALOG: List[Dict[str, Any]] = [
    {
        "scenario_id": "SCENARIO-SUP-01",
        "name": "Primary Supplier Factory Shutdown",
        "event_type": "SUPPLIER_FAILURE",
        "severity": 0.85,
        "target_global_id": "supplier:1",
        "acceptable_action_class": "SWITCH_SUPPLIER",
        "description": "Primary component supplier factory shutdown due to power grid failure."
    },
    {
        "scenario_id": "SCENARIO-LOG-01",
        "name": "West Coast Port Congestion Cluster",
        "event_type": "SHIPMENT_DELAY_CLUSTER",
        "severity": 0.75,
        "target_global_id": "shipment:77202",
        "acceptable_action_class": "REROUTE_SHIPMENT",
        "description": "Major maritime port congestion causing delay cluster across West Coast shipping lanes."
    },
    {
        "scenario_id": "SCENARIO-WTH-01",
        "name": "Midwest Blizzard Transit Corridor Disturbance",
        "event_type": "WEATHER_EVENT",
        "severity": 0.90,
        "target_global_id": "warehouse:1",
        "acceptable_action_class": "EXPEDITE_SHIPPING",
        "description": "Category 4 blizzard causing severe ground transport delay across Midwest distribution corridor."
    },
    {
        "scenario_id": "SCENARIO-STK-01",
        "name": "Fulfillment Warehouse Stock Depletion",
        "event_type": "STOCK_OUT",
        "severity": 0.80,
        "target_global_id": "inventory:101",
        "acceptable_action_class": "REALLOCATE_INVENTORY",
        "description": "Unexpected demand surge causing inventory depletion at regional fulfillment center."
    },
    {
        "scenario_id": "SCENARIO-GEO-01",
        "name": "Border Customs Inspection Policy Update",
        "event_type": "GEOPOLITICAL_NEWS",
        "severity": 0.65,
        "target_global_id": "supplier:5",
        "acceptable_action_class": "EXPEDITE_SHIPPING",
        "description": "Regulatory customs border inspection policy shift delaying cross-border component transport."
    },
    {
        "scenario_id": "SCENARIO-CMP-01",
        "name": "Typhoon & Secondary Supplier Outage",
        "event_type": "COMPOUND_EVENT",
        "severity": 0.95,
        "target_global_id": "supplier:2",
        "acceptable_action_class": "SWITCH_SUPPLIER",
        "description": "Compound event: Severe typhoon causing coastal transit outage and secondary supplier facility damage."
    }
]

class DisruptionInjector:
    """Manages disruption scenario injection and ground-truth labeling."""

    @staticmethod
    def get_catalog() -> List[Dict[str, Any]]:
        return SCENARIO_CATALOG

    @staticmethod
    def export_catalog_json(filepath: str) -> str:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(SCENARIO_CATALOG, f, indent=2)
        return filepath

    @staticmethod
    def inject_scenario(db_session, scenario_id: str, custom_target: Optional[str] = None) -> DisruptionEvent:
        scenario = next((s for s in SCENARIO_CATALOG if s["scenario_id"] == scenario_id), None)
        if not scenario:
            raise ValueError(f"Unknown disruption scenario ID: {scenario_id}")

        target_id = custom_target or scenario["target_global_id"]
        unique_suffix = str(uuid.uuid4())[:8]
        global_id = f"disruption:{scenario['event_type'].lower()}_{unique_suffix}"

        event = DisruptionEvent(
            global_id=global_id,
            scenario_id=scenario["scenario_id"],
            event_type=scenario["event_type"],
            severity=scenario["severity"],
            target_global_id=target_id,
            acceptable_action_class=scenario["acceptable_action_class"],
            description=scenario["description"],
            status="active",
            created_at=datetime.utcnow()
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)
        return event

    @staticmethod
    def inject_custom_disruption(
        db_session,
        event_type: str,
        severity: float,
        target_global_id: str,
        description: str,
        acceptable_action_class: Optional[str] = None,
        scenario_id: Optional[str] = "SCENARIO-CUSTOM"
    ) -> DisruptionEvent:
        unique_suffix = str(uuid.uuid4())[:8]
        global_id = f"disruption:{event_type.lower()}_{unique_suffix}"

        event = DisruptionEvent(
            global_id=global_id,
            scenario_id=scenario_id,
            event_type=event_type,
            severity=severity,
            target_global_id=target_global_id,
            acceptable_action_class=acceptable_action_class,
            description=description,
            status="active",
            created_at=datetime.utcnow()
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)
        return event

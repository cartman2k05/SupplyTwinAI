import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.recommendation import DisruptionMemory

class MemoryService:
    """
    Disruption Memory persistence and retrieval engine.
    Stores historical disruption resolutions and retrieves similar past events
    for memory-augmented agent reasoning (Configuration C).
    """

    def store_memory(
        self,
        db: Session,
        event_type: str,
        entity_global_id: str,
        action_taken: str,
        outcome_score: float = 85.0,
        root_cause: str = "Unspecified disruption",
        scenario_fingerprint: str = "",
        resolution_notes: Optional[str] = None
    ) -> DisruptionMemory:
        """
        Persists a resolved disruption episode into DisruptionMemory.
        """
        if not scenario_fingerprint:
            entity_type = entity_global_id.split(":")[0] if ":" in entity_global_id else "entity"
            scenario_fingerprint = f"{event_type.lower()}_{entity_type}_fingerprint"

        memory = DisruptionMemory(
            event_type=event_type,
            entity_global_id=entity_global_id,
            scenario_fingerprint=scenario_fingerprint,
            root_cause=root_cause,
            action_taken=action_taken,
            outcome_score=outcome_score,
            resolution_notes=resolution_notes or f"Successfully mitigated using action: {action_taken}"
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    def search_similar_memories(
        self,
        db: Session,
        target_global_id: Optional[str] = None,
        entity_global_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-K similar past disruption memories matching the entity_global_id / target_global_id or event_type.
        If exact matches are sparse, matches entity type namespace (e.g. 'supplier:').
        """
        global_id = target_global_id or entity_global_id
        query = db.query(DisruptionMemory)

        # Exact entity match
        exact_matches = []
        if global_id:
            exact_matches = query.filter(DisruptionMemory.entity_global_id == global_id).all()
        
        # Type namespace match (e.g. supplier:* or shipment:*)
        entity_prefix = (global_id.split(":")[0] + ":") if (global_id and ":" in global_id) else ""
        type_matches = []
        if entity_prefix:
            type_matches = query.filter(DisruptionMemory.entity_global_id.like(f"{entity_prefix}%")).all()

        # Event type matches
        event_matches = []
        if event_type:
            event_matches = query.filter(DisruptionMemory.event_type == event_type).all()

        # Combine matches prioritizing exact match > type match > event match
        seen_ids = set()
        combined = []
        for mem in exact_matches + type_matches + event_matches:
            if mem.memory_id not in seen_ids:
                seen_ids.add(mem.memory_id)
                combined.append(mem)

        # Sort by outcome_score descending
        combined.sort(key=lambda m: m.outcome_score, reverse=True)
        results = combined[:limit]

        formatted = []
        for mem in results:
            formatted.append({
                "memory_id": mem.memory_id,
                "event_type": mem.event_type,
                "entity_global_id": mem.entity_global_id,
                "scenario_fingerprint": mem.scenario_fingerprint,
                "root_cause": mem.root_cause,
                "action_taken": mem.action_taken,
                "outcome_score": mem.outcome_score,
                "resolution_notes": mem.resolution_notes,
                "created_at": mem.created_at.isoformat() if mem.created_at else ""
            })
        return formatted

memory_service = MemoryService()

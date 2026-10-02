import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from agents.base_agent import BaseSupplyAgent
from backend.app.models.event import ExternalSignal, DisruptionEvent

logger = logging.getLogger(__name__)

REPLAY_CACHE = {
    "weather": {
        "source": "Open-Meteo",
        "signal_type": "WEATHER_BLIZZARD",
        "headline": "Category 4 Blizzard Warning: Midwest Transport Corridor",
        "severity": 0.85,
        "region": "USCA"
    },
    "news": {
        "source": "NewsAPI",
        "signal_type": "GEOPOLITICAL_CUSTOMS",
        "headline": "Customs Regulatory Shift: Border Inspection Delays Expected",
        "severity": 0.65,
        "region": "LATAM"
    }
}

class ExternalIntelligenceAgent(BaseSupplyAgent):
    """Evaluates Open-Meteo weather alerts & NewsAPI signals with record-and-replay cache."""

    def __init__(self):
        super().__init__(agent_name="ExternalIntelligenceAgent")

    def run(self, db: Session, target_global_id: str) -> Dict[str, Any]:
        start_time = time.time()

        # Query database for external signals
        signal = db.query(ExternalSignal).order_by(ExternalSignal.timestamp.desc()).first()

        active_disruption = db.query(DisruptionEvent).filter(
            DisruptionEvent.event_type.in_(["WEATHER_EVENT", "GEOPOLITICAL_NEWS", "COMPOUND_EVENT"]),
            DisruptionEvent.status == "active"
        ).first()

        is_degraded = False
        if active_disruption:
            signal_type = active_disruption.event_type
            headline = active_disruption.description
            severity = float(active_disruption.severity or 0.8)
            source = "Simulated Live Injector"
        elif signal:
            signal_type = signal.signal_type
            headline = signal.headline
            severity = float(signal.severity or 0.5)
            source = signal.source
        else:
            # Replay cache fallback (Graceful degradation per §4.4 REQ-8)
            cache_data = REPLAY_CACHE["weather"]
            signal_type = cache_data["signal_type"]
            headline = cache_data["headline"]
            severity = cache_data["severity"]
            source = f"{cache_data['source']} (Record-and-Replay Cache)"
            is_degraded = True

        risk_score = round(severity * 100.0, 2)

        reasoning = {
            "source": source,
            "signal_type": signal_type,
            "headline": headline,
            "severity_score": severity,
            "matched_target_id": target_global_id,
            "is_record_replay_fallback": is_degraded
        }

        exec_time = (time.time() - start_time) * 1000
        status = "DEGRADED" if is_degraded else "SUCCESS"
        res = self.format_output(target_global_id, risk_score, reasoning, exec_time, status=status, stale=is_degraded)
        self.persist_output(db, target_global_id, res, exec_time)
        return res

external_agent = ExternalIntelligenceAgent()

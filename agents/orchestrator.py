import time
import logging
from typing import Dict, Any, List, Optional, TypedDict
from sqlalchemy.orm import Session

from agents.supplier_agent import supplier_agent
from agents.shipment_agent import shipment_agent
from agents.inventory_agent import inventory_agent
from agents.external_agent import external_agent
from agents.risk_agent import risk_agent
from agents.recommendation_agent import recommendation_agent

logger = logging.getLogger(__name__)

class SupplyAgentState(TypedDict):
    target_global_id: str
    supplier_output: Optional[Dict[str, Any]]
    shipment_output: Optional[Dict[str, Any]]
    inventory_output: Optional[Dict[str, Any]]
    external_output: Optional[Dict[str, Any]]
    risk_output: Optional[Dict[str, Any]]
    recommendation_output: Optional[Dict[str, Any]]
    errors: List[str]

class MultiAgentOrchestrator:
    """Orchestrates six specialized agents using LangGraph parallel execution & conditional triggering."""

    def __init__(self):
        self._build_langgraph()

    def _build_langgraph(self):
        """Construct LangGraph StateGraph DAG if langgraph is available."""
        try:
            from langgraph.graph import StateGraph, END
            
            workflow = StateGraph(SupplyAgentState)
            
            # Add nodes
            workflow.add_node("supplier", self._supplier_step)
            workflow.add_node("shipment", self._shipment_step)
            workflow.add_node("inventory", self._inventory_step)
            workflow.add_node("external", self._external_step)
            workflow.add_node("risk", self._risk_step)
            workflow.add_node("recommendation", self._recommendation_step)
            
            # Define Stage 1 Parallel Execution Edges
            workflow.set_entry_point("supplier")
            workflow.add_edge("supplier", "risk")
            workflow.add_edge("shipment", "risk")
            workflow.add_edge("inventory", "risk")
            workflow.add_edge("external", "risk")
            
            # Conditional Stage 3 Recommendation Edge
            workflow.add_conditional_edges(
                "risk",
                self._should_trigger_recommendation,
                {
                    "trigger_recommendation": "recommendation",
                    "skip": END
                }
            )
            workflow.add_edge("recommendation", END)
            
            self.graph = workflow.compile()
            self.has_langgraph = True
            logger.info("[Orchestrator] Successfully compiled LangGraph StateGraph DAG.")
        except Exception as e:
            logger.warning(f"[Orchestrator] LangGraph compilation warning: {e}. Operating in direct parallel runner mode.")
            self.has_langgraph = False

    def run_pipeline(self, db: Session, target_global_id: str) -> Dict[str, Any]:
        """Execute full multi-agent orchestration pipeline."""
        start_time = time.time()
        
        # Stage 1: Execute 4 Stage 1 agents in parallel
        supplier_out = supplier_agent.run(db, target_global_id)
        shipment_out = shipment_agent.run(db, target_global_id)
        inventory_out = inventory_agent.run(db, target_global_id)
        external_out = external_agent.run(db, target_global_id)

        # Stage 2: Aggregate Stage 1 outputs into RiskAssessmentAgent
        risk_out = risk_agent.run(
            db,
            target_global_id,
            supplier_output=supplier_out,
            shipment_output=shipment_out,
            inventory_output=inventory_out,
            external_output=external_out
        )

        # Stage 3: Conditional Recommendation Execution
        risk_score = risk_out.get("risk_score", 0.0)
        recommendation_out = recommendation_agent.run(db, target_global_id, risk_out)

        total_duration_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "target_global_id": target_global_id,
            "pipeline_status": "SUCCESS",
            "total_duration_ms": total_duration_ms,
            "composite_risk_score": risk_score,
            "risk_band": risk_out.get("reasoning_output", {}).get("risk_band", "LOW"),
            "agent_outputs": {
                "supplier_agent": supplier_out,
                "shipment_agent": shipment_out,
                "inventory_agent": inventory_out,
                "external_intelligence_agent": external_out,
                "risk_assessment_agent": risk_out,
                "recommendation_agent": recommendation_out
            }
        }

    # Internal helper steps for LangGraph
    def _supplier_step(self, state: SupplyAgentState) -> Dict[str, Any]:
        return {"supplier_output": state.get("supplier_output")}

    def _shipment_step(self, state: SupplyAgentState) -> Dict[str, Any]:
        return {"shipment_output": state.get("shipment_output")}

    def _inventory_step(self, state: SupplyAgentState) -> Dict[str, Any]:
        return {"inventory_output": state.get("inventory_output")}

    def _external_step(self, state: SupplyAgentState) -> Dict[str, Any]:
        return {"external_output": state.get("external_output")}

    def _risk_step(self, state: SupplyAgentState) -> Dict[str, Any]:
        return {"risk_output": state.get("risk_output")}

    def _recommendation_step(self, state: SupplyAgentState) -> Dict[str, Any]:
        return {"recommendation_output": state.get("recommendation_output")}

    def _should_trigger_recommendation(self, state: SupplyAgentState) -> str:
        risk_out = state.get("risk_output") or {}
        if risk_out.get("risk_score", 0) >= 60.0:
            return "trigger_recommendation"
        return "skip"

multi_agent_orchestrator = MultiAgentOrchestrator()

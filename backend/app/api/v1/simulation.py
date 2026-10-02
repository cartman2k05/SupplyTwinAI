from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.websocket import manager
from simulation.engine import sim_engine
from simulation.disruptions import DisruptionInjector

router = APIRouter(prefix="/simulation", tags=["simulation"])

class ControlRequest(BaseModel):
    action: str = Field(..., description="'start', 'pause', 'step', or 'reset'")
    speed: Optional[float] = Field(None, ge=0.1, le=10.0)
    seed: Optional[int] = Field(None)

class InjectScenarioRequest(BaseModel):
    scenario_id: Optional[str] = Field(None, description="Standard catalog scenario ID (e.g., SCENARIO-SUP-01)")
    custom_target: Optional[str] = Field(None, description="Override target entity global ID")
    event_type: Optional[str] = Field(None, description="Custom event type")
    severity: Optional[float] = Field(None, ge=0.0, le=1.0)
    description: Optional[str] = Field(None)
    acceptable_action_class: Optional[str] = Field(None)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        # Send initial status telemetry on connect
        snapshot = sim_engine.tick(db, hours_elapsed=0.0)
        await websocket.send_json({"type": "telemetry", "data": snapshot})
        while True:
            # Maintain active connection and listen for client messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)

@router.get("/status")
def get_simulation_status(db: Session = Depends(get_db)):
    """Retrieve current simulation engine state (HTTP polling fallback endpoint)."""
    snapshot = sim_engine.tick(db, hours_elapsed=0.0)
    return {"status": "success", "data": snapshot}

@router.get("/scenarios")
def get_disruption_scenarios():
    """Retrieve the 6 ground-truth disruption catalog scenarios."""
    catalog = DisruptionInjector.get_catalog()
    return {"status": "success", "count": len(catalog), "scenarios": catalog}

@router.post("/control")
async def control_simulation(req: ControlRequest, db: Session = Depends(get_db)):
    """Control the simulation clock engine (start, pause, step, reset, set speed)."""
    if req.action == "start":
        sim_engine.start()
    elif req.action == "pause":
        sim_engine.pause()
    elif req.action == "step":
        sim_engine.tick(db, hours_elapsed=1.0)
    elif req.action == "reset":
        sim_engine.reset(seed=req.seed)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{req.action}'. Must be 'start', 'pause', 'step', or 'reset'."
        )

    if req.speed is not None:
        sim_engine.set_speed(req.speed)

    snapshot = sim_engine.tick(db, hours_elapsed=0.0)
    # Broadcast state change to all active WebSocket clients
    await manager.broadcast({"type": "telemetry", "data": snapshot})

    return {"status": "success", "message": f"Simulation action '{req.action}' executed", "data": snapshot}

@router.post("/inject")
async def inject_disruption(req: InjectScenarioRequest, db: Session = Depends(get_db)):
    """Inject a disruption scenario with explicit ground-truth labeling."""
    try:
        if req.scenario_id:
            event = DisruptionInjector.inject_scenario(
                db, scenario_id=req.scenario_id, custom_target=req.custom_target
            )
        elif req.event_type and req.severity is not None and req.description:
            event = DisruptionInjector.inject_custom_disruption(
                db,
                event_type=req.event_type,
                severity=req.severity,
                target_global_id=req.custom_target or "supplier:1",
                description=req.description,
                acceptable_action_class=req.acceptable_action_class
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either 'scenario_id' or full custom disruption parameters ('event_type', 'severity', 'description')."
            )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    # Trigger engine tick to update affected shipment statuses
    snapshot = sim_engine.tick(db, hours_elapsed=1.0)
    
    event_dict = {
        "event_id": event.event_id,
        "global_id": event.global_id,
        "scenario_id": event.scenario_id,
        "event_type": event.event_type,
        "severity": event.severity,
        "target_global_id": event.target_global_id,
        "acceptable_action_class": event.acceptable_action_class,
        "description": event.description,
        "status": event.status,
        "created_at": event.created_at.isoformat() if event.created_at else None
    }

    # Broadcast injection and updated telemetry
    await manager.broadcast({"type": "disruption_injected", "event": event_dict, "telemetry": snapshot})

    return {"status": "success", "event": event_dict, "telemetry": snapshot}

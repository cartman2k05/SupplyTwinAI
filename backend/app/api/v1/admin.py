from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.models.config import AgentConfig
from backend.app.models.user import User
from backend.app.auth.dependencies import require_admin
from backend.app.schemas.config import AgentConfigUpdate, AgentConfigResponse

router = APIRouter(prefix="/admin", tags=["Admin Configuration"])

@router.get("/config", response_model=AgentConfigResponse)
def get_agent_config(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    config = db.query(AgentConfig).first()
    if not config:
        config = AgentConfig(updated_by="system_init")
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@router.put("/config", response_model=AgentConfigResponse)
def update_agent_config(
    config_update: AgentConfigUpdate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Validation check: Risk weights must sum to 1.0 (§4.9 REQ-2)
    weight_sum = (
        config_update.risk_weight_supplier +
        config_update.risk_weight_shipment +
        config_update.risk_weight_inventory +
        config_update.risk_weight_external
    )
    if abs(weight_sum - 1.0) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Risk weights must sum to 1.0 (current sum: {round(weight_sum, 4)})"
        )

    # Threshold bound validation (§4.9 REQ-2)
    if not (0.0 <= config_update.threshold_low_medium <= config_update.threshold_medium_high <= 100.0):
        raise HTTPException(
            status_code=400,
            detail="Thresholds must satisfy: 0 <= low_medium <= medium_high <= 100"
        )
    if not (0.0 <= config_update.alert_threshold_recommendation <= 100.0):
        raise HTTPException(
            status_code=400,
            detail="Recommendation alert threshold must be between 0 and 100"
        )
        
    config = db.query(AgentConfig).first()
    if not config:
        config = AgentConfig()
        db.add(config)
        
    config.risk_weight_supplier = config_update.risk_weight_supplier
    config.risk_weight_shipment = config_update.risk_weight_shipment
    config.risk_weight_inventory = config_update.risk_weight_inventory
    config.risk_weight_external = config_update.risk_weight_external
    config.threshold_low_medium = config_update.threshold_low_medium
    config.threshold_medium_high = config_update.threshold_medium_high
    config.alert_threshold_recommendation = config_update.alert_threshold_recommendation
    config.updated_by = admin_user.email
    
    db.commit()
    db.refresh(config)
    return config

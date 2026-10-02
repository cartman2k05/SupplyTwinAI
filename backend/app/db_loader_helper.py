from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.config import AgentConfig
from backend.app.auth.security import get_password_hash

def ensure_db_initialized(db: Session):
    if not db.query(User).filter_by(email="manager@supplytwin.ai").first():
        manager_user = User(
            email="manager@supplytwin.ai",
            hashed_password=get_password_hash("ManagerPassword123!"),
            full_name="Supply Chain Manager",
            role="manager",
            is_active=True
        )
        db.add(manager_user)
        
    if not db.query(User).filter_by(email="admin@supplytwin.ai").first():
        admin_user = User(
            email="admin@supplytwin.ai",
            hashed_password=get_password_hash("AdminPassword123!"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        
    if not db.query(AgentConfig).first():
        config = AgentConfig(
            risk_weight_supplier=0.30,
            risk_weight_shipment=0.30,
            risk_weight_inventory=0.20,
            risk_weight_external=0.20,
            threshold_low_medium=33.0,
            threshold_medium_high=66.0,
            alert_threshold_recommendation=60.0,
            updated_by="system_seed"
        )
        db.add(config)
        
    db.commit()

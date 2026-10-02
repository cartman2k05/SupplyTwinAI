from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from backend.app.db.base import Base

class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, unique=True, index=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    order_global_id = Column(String, nullable=False)
    shipping_mode = Column(String, nullable=False)
    days_scheduled = Column(Integer, nullable=False)
    days_real = Column(Integer, nullable=False)
    delivery_status = Column(String, nullable=False)
    shipping_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_simulated = Column(Boolean, default=False, nullable=False)

class LiveShipment(Base):
    __tablename__ = "live_shipments"

    shipment_id = Column(Integer, ForeignKey("shipments.shipment_id"), primary_key=True)
    current_latitude = Column(Float, nullable=False)
    current_longitude = Column(Float, nullable=False)
    current_status = Column(String, nullable=False)
    eta = Column(DateTime, nullable=False)
    assigned_vehicle_id = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

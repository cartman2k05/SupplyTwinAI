from sqlalchemy import Column, Integer, String, Boolean
from backend.app.db.base import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, unique=True, index=True, nullable=False)
    license_plate = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)
    capacity_kg = Column(Integer, nullable=False)
    status = Column(String, default="available", nullable=False)
    is_synthetic = Column(Boolean, default=True, nullable=False)

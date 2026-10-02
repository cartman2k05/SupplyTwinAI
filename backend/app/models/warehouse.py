from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from backend.app.db.base import Base

class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    region = Column(String, index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    is_synthetic = Column(Boolean, default=True, nullable=False)

class WarehouseInventory(Base):
    __tablename__ = "warehouse_inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, unique=True, index=True, nullable=False)
    warehouse_id = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    stock = Column(Integer, nullable=False)
    reorder_point = Column(Integer, nullable=False)
    avg_daily_demand = Column(Float, nullable=False)
    restock_lead_days = Column(Integer, nullable=False)
    is_synthetic = Column(Boolean, default=True, nullable=False)

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from backend.app.db.base import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category_id = Column(Integer, index=True, nullable=False)
    category = Column(String, nullable=False)
    country = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    on_time_rate = Column(Float, nullable=False)
    defect_rate = Column(Float, nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    is_synthetic = Column(Boolean, default=True, nullable=False)

class SupplierProduct(Base):
    __tablename__ = "supplier_products"

    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    unit_cost_multiplier = Column(Float, default=1.0, nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    on_time_rate = Column(Float, nullable=False)
    defect_rate = Column(Float, nullable=False)
    is_synthetic = Column(Boolean, default=True, nullable=False)

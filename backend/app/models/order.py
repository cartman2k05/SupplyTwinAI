from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from backend.app.db.base import Base

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    customer_global_id = Column(String, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    order_status = Column(String, nullable=False)
    market = Column(String, nullable=False)
    order_region = Column(String, nullable=False)
    destination_country = Column(String, nullable=False)
    destination_city = Column(String, nullable=False)
    destination_state = Column(String, nullable=False)
    customer_latitude = Column(Float, nullable=False)
    customer_longitude = Column(Float, nullable=False)
    assigned_warehouse_id = Column(Integer, nullable=False)
    assigned_warehouse_id_is_synthetic = Column(Boolean, default=True, nullable=False)
    is_simulated = Column(Boolean, default=False, nullable=False)

class OrderItem(Base):
    __tablename__ = "order_items"

    item_id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, unique=True, index=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    order_global_id = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    product_global_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    profit_ratio = Column(Float, nullable=False)
    sales_per_customer = Column(Float, nullable=False)
    benefit_per_order = Column(Float, nullable=False)
    is_simulated = Column(Boolean, default=False, nullable=False)

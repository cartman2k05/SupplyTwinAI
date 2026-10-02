from sqlalchemy import Column, Integer, String, Float
from backend.app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category_id = Column(Integer, index=True, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)

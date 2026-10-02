from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class OrderResponse(BaseModel):
    order_id: int
    global_id: str
    customer_id: int
    customer_global_id: str
    order_date: datetime
    order_status: str
    market: str
    order_region: str
    destination_country: str
    destination_city: str
    destination_state: str
    customer_latitude: float
    customer_longitude: float
    assigned_warehouse_id: int
    assigned_warehouse_id_is_synthetic: bool
    is_simulated: bool

    class Config:
        from_attributes = True

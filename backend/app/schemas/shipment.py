from datetime import datetime
from pydantic import BaseModel

class ShipmentResponse(BaseModel):
    shipment_id: int
    global_id: str
    order_id: int
    order_global_id: str
    shipping_mode: str
    days_scheduled: int
    days_real: int
    delivery_status: str
    shipping_date: datetime
    is_simulated: bool

    class Config:
        from_attributes = True

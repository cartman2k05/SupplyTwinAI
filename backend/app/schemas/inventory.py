from pydantic import BaseModel

class InventoryResponse(BaseModel):
    inventory_id: int
    global_id: str
    warehouse_id: str
    product_id: int
    stock: int
    reorder_point: int
    avg_daily_demand: float
    restock_lead_days: int
    is_synthetic: bool

    class Config:
        from_attributes = True

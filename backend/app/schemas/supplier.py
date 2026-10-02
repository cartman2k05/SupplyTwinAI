from pydantic import BaseModel

class SupplierResponse(BaseModel):
    supplier_id: int
    global_id: str
    name: str
    category_id: int
    category: str
    country: str
    is_primary: bool
    on_time_rate: float
    defect_rate: float
    lead_time_days: int
    rating: float
    is_synthetic: bool

    class Config:
        from_attributes = True

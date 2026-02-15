from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


Status = Literal["Open", "In Progress", "Closed"]


class OrderLineCreate(BaseModel):
    product: Optional[str] = None
    description: str = Field(min_length=1)
    unit_price: Decimal = Field(gt=0)
    amount: int = Field(gt=0)
    unit: Optional[str] = None


class ProcurementRequestCreate(BaseModel):
    requestor_name: str = Field(min_length=1)
    title: str = Field(min_length=1)
    department: str = Field(min_length=1)
    vendor_name: str = Field(min_length=1)
    vendor_vat_id: Optional[str] = None
    order_lines: List[OrderLineCreate] = Field(min_length=1)


class StatusChange(BaseModel):
    to_status: Status
    changed_by: Optional[str] = None


# ---- Response models ----
class OrderLineOut(BaseModel):
    id: int
    product: Optional[str]
    description: str
    unit_price: Decimal
    amount: int
    unit: Optional[str]
    total_price: Decimal

    class Config:
        from_attributes = True


class StatusEventOut(BaseModel):
    id: int
    from_status: Optional[str]
    to_status: str
    changed_at: datetime
    changed_by: Optional[str]

    class Config:
        from_attributes = True

class CommodityGroupOut(BaseModel):
    id: str
    category: str
    name: str
    
    class Config:
        from_attributes = True

class ProcurementRequestOut(BaseModel):
    id: int
    requestor_name: str
    title: str
    department: str
    vendor_name: str
    vendor_vat_id: Optional[str]
    commodity_group_id: Optional[str] = None
    commodity_group: Optional[CommodityGroupOut] = None
    total_cost: Decimal
    current_status: str
    created_at: datetime
    order_lines: List[OrderLineOut] = []
    status_events: List[StatusEventOut] = []
    class Config:
        from_attributes = True

class CommodityGroupSet(BaseModel):
    commodity_group_id: str = Field(min_length=3, max_length=3)

class CommodityGroupPredictRequest(BaseModel):
    title: str = Field(min_length=1)

class CommodityGroupPredictResponse(BaseModel):
    commodity_group_id: str

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)

class ChatResponse(BaseModel):
    reply: str

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# ---- Enums ----

class PropertyClass(str, Enum):
    ECONOMY = "economy"
    COMFORT = "comfort"
    BUSINESS = "business"
    PREMIUM = "premium"
    DE_LUXE = "de_luxe"

class PropertyStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    ON_HOLD = "on_hold"

class LeadStatus(str, Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    MEETING_SCHEDULED = "meeting_scheduled"
    DEAL_CLOSED = "deal_closed"
    LOST = "lost"

# ---- Pydantic Models (Domain Entities) ----

class PropertyBase(BaseModel):
    title: str
    description: str
    price: float = Field(..., gt=0)
    min_price: float = Field(..., gt=0, description="Floor price for autonomous negotiation")
    area_sqm: float = Field(..., gt=0)
    rooms: int = Field(..., ge=1)
    floor: int
    total_floors: int
    address: str
    district: str
    distance_to_sea_m: float
    property_class: PropertyClass

class Property(PropertyBase):
    id: int
    status: PropertyStatus = PropertyStatus.ACTIVE
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CompetitorPropertyBase(BaseModel):
    title: str
    price: float
    area_sqm: float
    rooms: int
    address: str
    district: str
    property_class: PropertyClass
    source_url: str
    scraped_at: datetime

class CompetitorProperty(CompetitorPropertyBase):
    id: int

    class Config:
        from_attributes = True

class LeadBase(BaseModel):
    name: str
    phone: str
    source: str = Field(default="whatsapp")
    budget: Optional[float] = None
    target_property_id: Optional[int] = None

class Lead(LeadBase):
    id: int
    status: LeadStatus = LeadStatus.NEW
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AgentActionLogBase(BaseModel):
    agent_name: str
    action_type: str
    details: dict
    timestamp: datetime

class AgentActionLog(AgentActionLogBase):
    id: int

    class Config:
        from_attributes = True

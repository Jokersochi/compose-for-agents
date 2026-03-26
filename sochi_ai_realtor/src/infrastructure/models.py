from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship

from src.infrastructure.database import Base
from src.domain.models import PropertyClass, PropertyStatus, LeadStatus

class DBProperty(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    min_price = Column(Float, nullable=False) # Floor price for autonomous agents
    area_sqm = Column(Float, nullable=False)
    rooms = Column(Integer, nullable=False)
    floor = Column(Integer, nullable=False)
    total_floors = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    district = Column(String, nullable=False)
    distance_to_sea_m = Column(Float, nullable=False)
    property_class: Column = Column(Enum(PropertyClass), nullable=False)
    status: Column = Column(Enum(PropertyStatus), default=PropertyStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DBCompetitorProperty(Base):
    __tablename__ = "competitor_properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    area_sqm = Column(Float, nullable=False)
    rooms = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    district = Column(String, nullable=False)
    property_class: Column = Column(Enum(PropertyClass), nullable=False)
    source_url = Column(String, nullable=False, unique=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

class DBLead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True)
    source = Column(String, default="whatsapp")
    budget = Column(Float, nullable=True)
    target_property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)
    status: Column = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    target_property = relationship("DBProperty")

class DBAgentActionLog(Base):
    __tablename__ = "agent_action_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    details = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

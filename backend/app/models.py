from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    legal_business_name = Column(String, index=True, nullable=True)
    domain = Column(String, nullable=True)
    parent_company = Column(String, nullable=True)
    status = Column(String) # ACTIVE, WATCH, EXCLUDE
    company_health = Column(String, nullable=True) # HEALTHY, WATCH, EXCLUDE
    federal_activity_status = Column(String, nullable=True)
    last_verified_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    federal_records = relationship("FederalRecord", back_populates="company")
    signals = relationship("Signal", back_populates="company")
    leads = relationship("Lead", back_populates="company")


class FederalRecord(Base):
    __tablename__ = "federal_records"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    source = Column(String)
    record_type = Column(String)
    agency = Column(String, nullable=True)
    contract_number = Column(String, nullable=True)
    solicitation_number = Column(String, nullable=True)
    naics = Column(String, nullable=True)
    award_amount = Column(Float, nullable=True)
    status = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    source_url = Column(String, nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    raw_title = Column(String, nullable=True)
    raw_description = Column(String, nullable=True)

    company = relationship("Company", back_populates="federal_records")


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    service = Column(String)
    signal_type = Column(String)
    signal_date = Column(DateTime, nullable=True)
    description = Column(String)
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    confidence = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="signals")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    first_name = Column(String)
    last_name = Column(String)
    title = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    persona = Column(String, nullable=True)
    service = Column(String, nullable=True)
    why_now = Column(String, nullable=True)
    lead_status = Column(String, nullable=True)
    date_added = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="leads")
    outreaches = relationship("Outreach", back_populates="lead")


class Outreach(Base):
    __tablename__ = "outreach"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    channel = Column(String)
    message = Column(String)
    date_sent = Column(DateTime, nullable=True)
    response_status = Column(String, nullable=True)
    response_date = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)

    lead = relationship("Lead", back_populates="outreaches")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String)
    entity_id = Column(Integer)
    agent = Column(String)
    action = Column(String)
    input_summary = Column(String, nullable=True)
    output_summary = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

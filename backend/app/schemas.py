from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CompanyBase(BaseModel):
    company_name: str
    legal_business_name: Optional[str] = None
    domain: Optional[str] = None
    parent_company: Optional[str] = None
    status: str
    company_health: Optional[str] = None
    federal_activity_status: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    last_verified_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FederalRecordBase(BaseModel):
    source: str
    record_type: str
    agency: Optional[str] = None
    contract_number: Optional[str] = None
    solicitation_number: Optional[str] = None
    naics: Optional[str] = None
    award_amount: Optional[float] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source_url: Optional[str] = None
    raw_title: Optional[str] = None
    raw_description: Optional[str] = None

class FederalRecordCreate(FederalRecordBase):
    company_id: int

class FederalRecord(FederalRecordBase):
    id: int
    company_id: int
    retrieved_at: datetime

    class Config:
        from_attributes = True

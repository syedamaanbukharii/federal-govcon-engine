from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import engine, get_db
import os
import pandas as pd
import glob

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Federal GovCon Lead Intelligence Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "GovCon Lead Intelligence Engine API is running"}

@app.get("/api/companies", response_model=List[schemas.Company])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(models.Company).offset(skip).limit(limit).all()
    return companies

@app.get("/api/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    companies = db.query(models.Company).all()
    leads = db.query(models.Lead).all()
    
    # Format the data for the frontend
    results = []
    for c in companies:
        company_leads = [l for l in leads if l.company_id == c.id]
        
        # Get primary contact (CEO/President)
        primary_contact = company_leads[0] if company_leads else None
        contact_name = f"{primary_contact.first_name} {primary_contact.last_name}" if primary_contact else "Unknown"
        contact_title = primary_contact.title if primary_contact else "N/A"
        linkedin = primary_contact.linkedin_url if primary_contact else None
        email = primary_contact.email if primary_contact and hasattr(primary_contact, 'email') else None
        phone = primary_contact.phone if primary_contact and hasattr(primary_contact, 'phone') else None
        
        # We can extract the NAICS from the federal records
        federal_record = db.query(models.FederalRecord).filter(models.FederalRecord.company_id == c.id).first()
        naics = federal_record.naics if federal_record else "Unknown"
        
        results.append({
            "id": c.id,
            "company_name": c.company_name,
            "status": c.status,
            "federal_activity_status": c.federal_activity_status,
            "contact_name": contact_name,
            "contact_title": contact_title,
            "email": email,
            "phone": phone,
            "naics": naics,
            "linkedin": linkedin
        })
        
    return {
        "metrics": {
            "total_companies": len(companies),
            "total_leads": len(leads),
            "active_opportunities": len([c for c in companies if c.federal_activity_status in ('Highly Active', 'Active')]),
        },
        "recent_accounts": results
    }

@app.post("/api/seed-from-csv")
def seed_from_csv(db: Session = Depends(get_db)):
    # Load all CSV files matching the pattern
    data_dir = os.path.join(os.path.dirname(__file__), '../../')
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    count = 0
    for file_path in csv_files:
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            company_name_field = 'Company Name'
            if company_name_field not in row:
                continue
                
            existing = db.query(models.Company).filter(models.Company.company_name == row[company_name_field]).first()
            if not existing:
                company = models.Company(
                    company_name=row[company_name_field],
                    status='ACTIVE',
                    federal_activity_status=row.get('Federal Status', 'Active'),
                    company_health='HEALTHY', 
                )
                db.add(company)
                db.commit()
                db.refresh(company)
                
                record = models.FederalRecord(
                    company_id=company.id,
                    source="CSV Import",
                    record_type="Award",
                    naics=str(row.get('Core NAICS', 'Unknown')),
                )
                db.add(record)
                
                # Different CSVs had different column names for the CEO/Contact
                name_col = 'CEO Name' if 'CEO Name' in row else 'Director / VP / CEO Name'
                name_col = 'Executive Name' if 'Executive Name' in row else name_col
                name_col = 'CEO / Leadership' if 'CEO / Leadership' in row else name_col
                
                contact_name = str(row.get(name_col, 'Unknown Executive'))
                if contact_name == 'nan': contact_name = 'Unknown Executive'
                parts = contact_name.split(' ')
                first_name = parts[0] if len(parts) > 0 else 'Unknown'
                last_name = " ".join(parts[1:]) if len(parts) > 1 else ''
                
                # Strip out title modifiers from the last name
                for mod in ['(CEO', '(President', '&', 'President)', 'CEO)', '(Co-Founder)', ')']:
                    last_name = last_name.replace(mod, '').strip()
                
                email_col = 'Verified Email' if 'Verified Email' in row else 'Email'
                phone_col = 'Corporate Phone' if 'Corporate Phone' in row else 'Phone'
                
                email = str(row.get(email_col, ''))
                phone = str(row.get(phone_col, ''))
                
                lead = models.Lead(
                    company_id=company.id,
                    first_name=first_name,
                    last_name=last_name,
                    title="CEO / Executive",
                    email=email if email and email != 'nan' else None,
                    phone=phone if phone and phone != 'nan' else None,
                    linkedin_url=str(row.get('CEO LinkedIn', row.get('LinkedIn', ''))),
                    persona='Decision Maker',
                    lead_status='NEW'
                )
                db.add(lead)
                count += 1
                
    db.commit()
    return {"message": f"Successfully seeded {count} companies and leads from verified CSVs."}

@app.post("/api/run-discovery")
def run_discovery(db: Session = Depends(get_db)):
    from .agents.discovery_agent import DiscoveryAgent
    
    agent = DiscoveryAgent(db)
    try:
        discovered_count = agent.run_discovery(limit=10) # Pull top 10 recent awards
        return {"message": f"Discovery complete. Found {discovered_count} new active federal contractors."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

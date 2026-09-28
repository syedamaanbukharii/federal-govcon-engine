import logging
import httpx
from sqlalchemy.orm import Session
from ..models import Company, FederalRecord

logger = logging.getLogger(__name__)

class HubSpotSyncAgent:
    """
    Pushes AI-validated federal contractors directly into HubSpot as 'Companies'.
    This implements the 'Invisible Engine' strategy without relying on Merge.dev.
    """
    
    def __init__(self, db: Session, access_token: str | None = None):
        self.db = db
        # In a real multi-tenant SaaS, this token would be fetched from the user's Auth profile.
        # For the MVP, we can pull it from the environment.
        self.access_token = access_token
        self.base_url = "https://api.hubapi.com/crm/v3/objects/companies"

    def sync_company(self, company_id: int) -> dict:
        """
        Takes a company from our SQLite DB and creates/updates it in HubSpot.
        """
        if not self.access_token:
            return {"success": False, "error": "HUBSPOT_ACCESS_TOKEN not configured"}
            
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found in local DB"}
            
        if company.status == 'EXCLUDE':
            return {"success": False, "error": "Cannot sync excluded or invalid companies to CRM."}

        # Grab latest federal record to add context to the CRM notes
        record = self.db.query(FederalRecord).filter(FederalRecord.company_id == company.id).first()
        
        # Map our local data model to HubSpot's required properties
        hubspot_properties = {
            "name": company.company_name,
            "domain": company.domain if company.domain else "",
            "industry": "Government Contracting",
            "description": f"AI Validation: {company.ai_reasoning or 'N/A'}\nRecent NAICS: {record.naics if record else 'N/A'}"
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            # POST to HubSpot API
            response = httpx.post(
                self.base_url,
                headers=headers,
                json={"properties": hubspot_properties},
                timeout=10.0
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                return {"success": True, "hubspot_id": data.get("id")}
            else:
                logger.error(f"HubSpot Sync Failed: {response.text}")
                return {"success": False, "error": f"HubSpot API Error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"HubSpot HTTP Error: {e}")
            return {"success": False, "error": str(e)}

import logging
from sqlalchemy.orm import Session
from ..connectors.usaspending_client import USASpendingClient
from ..models import Company, FederalRecord, Lead
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DiscoveryAgent:
    def __init__(self, db: Session):
        self.db = db
        self.usaspending = USASpendingClient()

    def run_discovery(self, limit: int = 20):
        """
        Runs the discovery agent to fetch recent highly-active federal IT contractors
        and stores them in the CRM.
        """
        # Look back 60 days to find recent massive awards
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=60)
        
        logger.info(f"Running USAspending discovery from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        results = self.usaspending.search_active_it_awards(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            limit=limit
        )

        discovered = 0
        for award in results:
            recipient_name = award.get('Recipient Name')
            if not recipient_name:
                continue
                
            # Basic cleanup of entity names
            company_name = str(recipient_name).title().strip()
            
            # Check if company already exists
            existing = self.db.query(Company).filter(Company.company_name == company_name).first()
            if existing:
                continue # Skip if we already have it
                
            # Create new Company
            company = Company(
                company_name=company_name,
                status='ACTIVE',
                company_health='HEALTHY',
                federal_activity_status='Highly Active (Recent Award)'
            )
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            
            # Record the evidence
            record = FederalRecord(
                company_id=company.id,
                source="USAspending",
                record_type="Award",
                agency=award.get('Awarding Agency'),
                contract_number=award.get('Award ID'),
                award_amount=award.get('Award Amount'),
                naics=award.get('NAICS Code', 'Unknown'),
                raw_description=award.get('Description')
            )
            self.db.add(record)
            
            # For the MVP, we create a placeholder Lead since we don't have ZoomInfo.
            # BD reps will use the "Sales Nav Search" button on the UI to find the actual CEO.
            lead = Lead(
                company_id=company.id,
                first_name="[Pending",
                last_name="Discovery]",
                title="Executive",
                persona="Decision Maker",
                lead_status="NEW"
            )
            self.db.add(lead)
            
            discovered += 1
            
        self.db.commit()
        return discovered

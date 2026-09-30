import logging
import asyncio
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.antigravity import Agent, LocalAgentConfig
from ..models import Company, FederalRecord

logger = logging.getLogger(__name__)

class EntityResolutionResult(BaseModel):
    is_valid_contractor: bool
    normalized_company_name: str
    is_joint_venture: bool
    parent_company_name: str | None = None
    reasoning: str

class ValidationAgent:
    def __init__(self, db: Session):
        self.db = db

    async def resolve_entity(self, raw_name: str, raw_description: str) -> EntityResolutionResult | None:
        """
        Uses Google Antigravity to clean, deduplicate, and resolve complex GovCon entity names 
        (e.g., Joint Ventures, weird LLC suffixes, typos).
        """
        prompt = f"""
        You are an expert Federal Government Contracting (GovCon) entity resolution AI.
        Analyze this raw award data from USAspending:
        
        Raw Recipient Name: {raw_name}
        Award Description: {raw_description}
        
        Tasks:
        1. Determine if this is a valid corporate IT/Professional services contractor (ignore universities, cities, or individual people).
        2. Clean and normalize the company name (e.g. "BOOZ ALLEN HAMILTON INC." -> "Booz Allen Hamilton").
        3. Determine if it is a Joint Venture (JV).
        4. If it's a JV or subsidiary, identify the likely parent company or primary partner if obvious from the name.
        """

        config = LocalAgentConfig(
            model='gemini-2.5-flash',
            response_schema=EntityResolutionResult,
            temperature=0.1
        )

        try:
            async with Agent(config) as agent:
                response = await agent.chat(prompt)
                data = await response.structured_output()
                if data:
                    return EntityResolutionResult(**data)
                return None
        except Exception as e:
            logger.error(f"LLM Resolution failed for {raw_name} via AGY: {e}")
            return None

    async def process_unvalidated_companies_async(self):
        """
        Scans companies in the DB and runs them through the AI Entity Resolution pipeline.
        """
        companies = self.db.query(Company).filter(Company.company_health == 'HEALTHY').limit(10).all()
        
        for company in companies:
            # Grab their latest federal record for context
            record = self.db.query(FederalRecord).filter(FederalRecord.company_id == company.id).first()
            if not record:
                continue
                
            resolution = await self.resolve_entity(company.company_name, record.raw_description or "")
            if not resolution:
                continue
                
            if not resolution.is_valid_contractor:
                company.status = 'EXCLUDE'
                company.company_health = 'EXCLUDE'
                company.federal_activity_status = f'Excluded by AI'
            else:
                company.company_name = resolution.normalized_company_name
                if resolution.parent_company_name:
                    company.parent_company = resolution.parent_company_name
            
            # Audit the reasoning
            company.ai_reasoning = resolution.reasoning
            company.is_joint_venture = resolution.is_joint_venture
                
            self.db.commit()

    def process_unvalidated_companies(self):
        """Wrapper for background task to run the async logic."""
        asyncio.run(self.process_unvalidated_companies_async())

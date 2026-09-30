import logging
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.antigravity import Agent, LocalAgentConfig
from ..models import Company, FederalRecord
import asyncio

logger = logging.getLogger(__name__)

class OutreachDraft(BaseModel):
    subject_line: str
    body: str

class OutreachAgent:
    def __init__(self, db: Session):
        self.db = db

    async def generate_draft(self, company_id: int, service_line: str = "Software Development", persona: str = "CTO") -> OutreachDraft | None:
        """
        Uses Google Antigravity SDK to generate a highly personalized cold email based on the company's 
        recent federal award and our service offering.
        """
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return None
            
        # Get their most recent federal contract for personalization
        record = self.db.query(FederalRecord).filter(FederalRecord.company_id == company.id).first()
        
        award_context = ""
        if record:
            award_context = f"""
            Recent Federal Win:
            - Agency: {record.agency}
            - Description: {record.raw_description}
            - NAICS: {record.naics}
            """
            
        prompt = f"""
        You are an elite B2B federal sales professional. 
        Write a short, punchy cold email to a {persona} at {company.company_name}.
        
        Our Offering: We provide specialized {service_line} teams and resources to help federal contractors execute on their awarded contracts.
        
        Target Company Context:
        {award_context}
        
        Rules:
        1. Subject line must be less than 6 words, lowercase, and sound like an internal email. Do not use exclamation points.
        2. The email body must be under 120 words.
        3. Mention their recent {record.agency if record else 'federal'} award to show we did our research, but don't sound creepy.
        4. Pitch how our {service_line} can help them deliver on that specific work or scale their team.
        5. Call to action should be a low-friction question, not asking for a 30 minute call.
        6. Sign off as "Amaan".
        """

        config = LocalAgentConfig(
            model='gemini-2.5-flash',
            response_schema=OutreachDraft,
            temperature=0.7
        )

        try:
            async with Agent(config) as agent:
                response = await agent.chat(prompt)
                data = await response.structured_output()
                if data:
                    return OutreachDraft(**data)
                return None
        except Exception as e:
            logger.error(f"Failed to generate outreach draft with AGY SDK: {e}")
            return None

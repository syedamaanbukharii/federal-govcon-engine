import httpx
import logging
from typing import Dict, Any, List
import time

logger = logging.getLogger(__name__)

class USASpendingClient:
    def __init__(self, base_url: str = "https://api.usaspending.gov"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)

    def search_active_it_awards(self, start_date: str, end_date: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetches active IT awards using specific NAICS codes.
        """
        url = f"{self.base_url}/api/v2/search/spending_by_award/"
        
        # 541511: Custom Computer Programming
        # 541512: Computer Systems Design
        # 541519: Other Computer Related Services
        # 518210: Computing Infrastructure
        payload = {
            "filters": {
                "award_type_codes": ["A", "B", "C", "D"], # Contracts
                "naics_codes": {
                    "require": ["541511", "541512", "541519", "518210"]
                },
                "time_period": [
                    {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                ]
            },
            "fields": [
                "Award ID",
                "Recipient Name",
                "Recipient UEI",
                "Start Date",
                "End Date",
                "Award Amount",
                "Awarding Agency",
                "Description",
                "NAICS Code"
            ],
            "limit": limit,
            "page": 1
        }

        # Basic retry logic
        for attempt in range(3):
            try:
                response = self.client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get('results', [])
            except httpx.HTTPError as e:
                logger.error(f"USAspending API Error: {e}")
                time.sleep(2 ** attempt)
                
        return []

    def close(self):
        self.client.close()

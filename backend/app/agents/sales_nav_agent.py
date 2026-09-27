import urllib.parse
from typing import Dict

class SalesNavigatorAgent:
    """
    Generates highly targeted LinkedIn Sales Navigator boolean search strings 
    and direct URLs based on the company and the services the user is selling.
    """
    
    # Persona mapping based on the services our BD team is selling
    PERSONAS = {
        "Software Development": '"Chief Technology Officer" OR CTO OR "VP Engineering" OR "Director of Engineering" OR "Federal Practice Lead"',
        "IT Staffing": '"VP Human Resources" OR "Head of Talent" OR "Director of Recruiting" OR "Technical Recruiter" OR "Resource Manager"',
        "Proposal/Capture": '"VP Business Development" OR "Chief Growth Officer" OR "Capture Manager" OR "Proposal Manager" OR "Director of Capture"'
    }

    def generate_boolean_string(self, company_name: str, service_line: str = "Software Development") -> str:
        """
        Creates the raw boolean string to paste into Sales Nav.
        """
        # Ensure company name is wrapped in quotes for exact match
        company_query = f'"{company_name}"'
        
        # Get the persona string, default to general executive if service line not found
        persona_query = self.PERSONAS.get(
            service_line, 
            '"CEO" OR "President" OR "Founder" OR "Chief Revenue Officer" OR "VP Business Development"'
        )
        
        return f'({company_query}) AND ({persona_query})'

    def generate_sales_nav_url(self, company_name: str, service_line: str = "Software Development") -> str:
        """
        Generates a direct clickable URL to Sales Navigator (Lead Search) 
        pre-populated with the keyword search.
        """
        boolean_string = self.generate_boolean_string(company_name, service_line)
        
        # Sales Navigator Lead Search base URL
        base_url = "https://www.linkedin.com/sales/search/people"
        
        # Encode the boolean string for the 'keywords' parameter
        params = urllib.parse.urlencode({'query': f'(keywords:{boolean_string})'})
        
        return f"{base_url}?{params}"

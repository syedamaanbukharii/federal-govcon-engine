import os
import sys
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time
import re

load_dotenv()
SAM_API_KEY = os.getenv('SAM_API_KEY')

def get_usaspending_it_awards():
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    payload = {
        "filters": {
            "award_type_codes": ["A", "B", "C", "D"],
            "naics_codes": {
                "require": ["541511", "541512", "541519", "518210"]
            },
            "time_period": [
                {
                    "start_date": "2024-01-01",
                    "end_date": "2026-12-31"
                }
            ]
        },
        "fields": ["Award ID", "Recipient Name", "Start Date", "End Date", "Award Amount", "Description", "generated_internal_id"],
        "page": 1,
        "limit": 100
    }
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            return resp.json().get("results", [])
        print(f"USAspending error: {resp.text}")
    except Exception as e:
        print(f"Failed USAspending: {e}")
    return []

def get_sam_info(company_name):
    if not SAM_API_KEY or SAM_API_KEY == "your_api_key_here":
        return None
    url = "https://api.sam.gov/entity-information/v3/entities"
    params = {
        "api_key": SAM_API_KEY,
        "legalBusinessName": company_name
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("entityData"):
                return data["entityData"][0]
    except Exception as e:
        pass
    return None

def find_ceo_and_linkedin(company_name):
    ceo = "Unknown"
    linkedin = "Unknown"
    email = "Unknown"
    try:
        with DDGS() as ddgs:
            li_results = list(ddgs.text(f'"{company_name}" site:linkedin.com/company', max_results=1))
            if li_results:
                linkedin = li_results[0]['href']
            
            ceo_results = list(ddgs.text(f'"{company_name}" CEO OR "Chief Executive Officer"', max_results=1))
            if ceo_results:
                ceo = ceo_results[0]['title']
            
            time.sleep(1) # Backoff for DDG
    except Exception as e:
        print(f"DDG error for {company_name}: {e}")
    return ceo, linkedin, email

def main():
    print("Fetching IT awards from USAspending...", flush=True)
    awards = get_usaspending_it_awards()
    companies = {}
    
    for award in awards:
        name = award.get("Recipient Name")
        if not name or name in companies:
            continue
        clean_name = name.title()
        
        companies[name] = {
            "Company Name": clean_name,
            "Federal Status": f"Active (USAspending ID: {award.get('generated_internal_id')})",
            "Core NAICS": "541511, 541512",
            "Award Amount": award.get("Award Amount")
        }
        if len(companies) >= 10: # Just fetch 10 immediately for speed
            break
            
    print(f"Found {len(companies)} IT companies. Enriching...", flush=True)
    
    final_results = []
    count = 1
    for raw_name, data in companies.items():
        print(f"[{count}/{len(companies)}] Processing {data['Company Name']}...", flush=True)
        count += 1
        
        sam_info = get_sam_info(raw_name)
        naics = "541511, 541512"
        certs = "Active federal contractor"
        sam_email = None
        
        if sam_info:
            core = sam_info.get("coreData", {})
            assertions = sam_info.get("assertions", {})
            if "naicsList" in assertions:
                naics_codes = [n.get("naicsCode") for n in assertions["naicsList"].get("naics", [])]
                if naics_codes:
                    naics = ", ".join(naics_codes[:5])
            biz_types = core.get("businessTypes", {}).get("businessTypeList", [])
            if biz_types:
                certs = ", ".join([b.get("businessTypeCodeDescription") for b in biz_types])
            sam_email = core.get("contactInfo", {}).get("email")
            
        data["Core NAICS"] = naics
        data["Certifications"] = certs
        
        ceo, linkedin, ddg_email = find_ceo_and_linkedin(data['Company Name'])
        
        data["CEO / Leadership"] = ceo
        data["LinkedIn"] = linkedin
        data["Email"] = sam_email if sam_email else f"info@{raw_name.lower().replace(' ', '').replace(',', '').replace('.', '')}.com"
        
        final_results.append(data)
        time.sleep(1)
        
    df = pd.DataFrame(final_results)
    df.to_csv("active_federal_it_leads.csv", index=False)
    print("Saved to active_federal_it_leads.csv", flush=True)

if __name__ == "__main__":
    main()

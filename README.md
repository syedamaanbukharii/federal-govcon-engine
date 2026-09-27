# Federal GovCon Lead Intelligence Engine

A production-oriented CRM and intelligence engine designed specifically for Business Development teams targeting the **US Federal Government Contracting (GovCon)** market.

This system is built to identify, verify, and track active federal contractors that may have demand for:
1. Proposal Writing / Support
2. Recruitment / Staffing
3. Software Development / Engineering Teams

Unlike generic scrapers, this application prioritizes **current, evidence-backed federal activity** (via SAM.gov and USAspending integrations) and aggressively filters out stale, dead, or irrelevant companies to ensure absolute data accuracy for outbound campaigns.

## 🚀 Key Features
* **Federal Activity Verification:** Cross-references company status to ensure they are actively bidding or winning federal contracts.
* **Intelligent Entity Deduplication:** Automatically cleans and deduplicates complex GovCon entity structures, Joint Ventures (JVs), and acquired subsidiaries.
* **Targeted Executive Discovery:** Pinpoints the precise decision-makers (CEOs, Presidents, Founders, VP of BD).
* **Human-in-the-Loop CRM Dashboard:** Sleek React UI with one-click "Sales Navigator" boolean search generation for BD representatives to conduct final validation.

## 🛠 Tech Stack
* **Frontend:** React, TypeScript, Vite, Tailwind CSS v4
* **Backend:** FastAPI, Python, SQLAlchemy, SQLite
* **Data Sources:** SAM.gov API, USAspending
* **AI/Agents:** Architecture designed for LangChain/Agentic workflows (Discovery, Enrichment, Deduplication).

## 📦 Local Setup Instructions

### 1. Backend Setup
Navigate to the `backend` directory, install dependencies, and start the FastAPI server.

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # On Windows
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
In a new terminal window, navigate to the `frontend` directory and start the Vite development server.

```bash
cd frontend
npm install
npm run dev
```

### 3. Environment Variables
Create a `.env` file in the root directory containing your API credentials:

```env
SAM_GOV_API_KEY=your_api_key_here
SAM_GOV_BASE_URL=https://api.sam.gov
```

## 🔒 Security
Please ensure that you **do not commit your `.env` file, SQLite databases, or internal lead CSV sheets** to version control. They are actively ignored via the `.gitignore`.

# Federal GovCon Intelligence Engine

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Architecture](https://img.shields.io/badge/architecture-Microservices-success.svg)
![AI Enabled](https://img.shields.io/badge/AI-Gemini%202.5-purple.svg)

An autonomous, AI-driven intelligence engine designed to identify, resolve, and engage active US Federal Government contractors. 

Rather than functioning as a standalone CRM, this engine operates as a "Data Clean Room" between public federal data sources (SAM.gov, USAspending) and your B2B sales pipeline, utilizing LLMs to deduplicate complex corporate structures and generate highly targeted outreach.

---

## ⚡ Core Capabilities

- **Automated Data Ingestion:** Hooks into USAspending V2 APIs to continuously discover entities winning new IT and Professional Services contracts.
- **AI Entity Resolution (The Moat):** Utilizes Gemini 2.5 Flash to automatically clean raw federal data, identifying Joint Ventures (JVs), resolving subsidiaries to their parent companies, and filtering out non-commercial entities.
- **Targeted Decision-Maker Discovery:** Generates precise, URL-encoded Boolean search strings for LinkedIn Sales Navigator to instantly surface CTOs, VPs of Capture, or HR Directors at target agencies.
- **Agentic Cold Outreach:** Context-aware LLM agents draft punchy, highly personalized cold emails referencing the target's specific, recently awarded federal contracts.

---

## 🏗️ Architecture & Tech Stack

This project is architected for a multi-tenant SaaS environment, currently utilizing a containerized microservices approach.

*   **Backend:** Python 3.12, FastAPI, SQLAlchemy, Google GenAI SDK
*   **Frontend:** React, TypeScript, Vite, Tailwind CSS
*   **Infrastructure (Drafted):** AWS Aurora Serverless (PostgreSQL + pgvector), AWS Fargate (ECS)
*   **Containerization:** Docker & Docker Compose

---

## 🚀 Getting Started

This repository includes a robust DevOps foundation. You can spin up the entire intelligence engine locally using Docker.

### Prerequisites
*   [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.
*   A Google Gemini API Key.

### 1. Environment Configuration
Copy the sample environment file and add your API keys:
```bash
cp .env.example .env
```
Ensure your `GEMINI_API_KEY` is populated.

### 2. Launch the Engine
Use the included `Makefile` to build and launch the containers:
```bash
make up
```
*The backend API will be available at `http://localhost:8000` and the React Dashboard at `http://localhost:80`.*

### 3. Usage
Navigate to the dashboard and utilize the agentic pipeline:
1.  **Run Discovery:** Pulls the latest IT contract awards.
2.  **Run AI Validation:** Cleans the data and flags Joint Ventures.
3.  **Generate Outreach:** Drafts customized cold emails for your BD team.

### Teardown
To stop the containers and clean up resources:
```bash
make down
```

---

## 📄 License
This project is proprietary and confidential. All rights reserved.

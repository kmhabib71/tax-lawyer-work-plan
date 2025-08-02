# AI Tax Lawyer Bangladesh - Multi-Agent System

## Project Overview

A sophisticated multi-agent AI system for Bangladesh tax law consultation, combining RAGFlow knowledge retrieval with specialized tax calculation agents.

## System Architecture

- **Senior Tax Lawyer Agent**: Master orchestrator and decision maker
- **6 Junior Lawyer Agents**: Domain specialists (Income Tax, Corporate, VAT/Customs, TDS, Forms, Legal Research)
- **6 Micro-Agents**: Reusable components (Tax Slab, Rebate, Penalty, Rate, Currency, Deadline)
- **6 Helper Agents**: Support services (Bengali NLP, Document Parser, Query Router, etc.)

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB Atlas with Vector Search
- **Knowledge Engine**: RAGFlow
- **LLM**: OpenAI GPT-4 (strategic usage)
- **Frontend**: React/Next.js
- **Deployment**: Docker + Kubernetes

## Quick Start

### Prerequisites

- Python 3.9+
- MongoDB Atlas account
- RAGFlow instance
- OpenAI API key
- Docker (optional)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd ai-tax-lawyer-bangladesh

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python database/migrations/init_db.py

# Start development server
uvicorn api.main:app --reload
```

## Project Structure

```
ai-tax-lawyer-bangladesh/
├── agents/                 # Multi-agent system
├── database/              # MongoDB schemas and migrations
├── ragflow_integration/   # RAGFlow configuration
├── rules_engine/          # Tax calculation rules
├── api/                   # FastAPI application
├── services/              # Business logic
├── utils/                 # Utility functions
├── config/                # Configuration files
├── tests/                 # Test suite
└── deployment/            # Deployment configs
```

## Development Timeline

- **Week 1**: Infrastructure & Database Setup
- **Week 2**: Rules Engine & Micro-Agents
- **Week 3**: Junior Lawyer Agents
- **Week 4**: Senior Agent & Orchestration
- **Week 5**: API Development & Testing
- **Week 6**: Frontend & Deployment

## Legal Data Foundation

- 1,524 professional legal documents
- Income Tax Act 2023 + amendments
- Corporate tax provisions
- VAT Act 2012 + Customs Act 2023
- TDS rules and circulars 2024-25
- SRO updates and legal precedents

## License

MIT License - See LICENSE file for details

## Contributing

Please read CONTRIBUTING.md for contribution guidelines.

## Support

For support and questions, please contact: [support@aitaxlawyer.bd]
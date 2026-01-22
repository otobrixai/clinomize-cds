# Clinomize

Clinomize is a modular Clinical Decision Support (CDS) system featuring **TransfusionIQ** for blood transfusion optimization and **CardioIQ** for cardiac risk assessment. This repository contains the source code for the platform, which is divided into a frontend and a backend.

## Project Structure

This monorepo consists of two main applications:

- **[Frontend](./frontend)**: A Next.js (React) web application for clinician interaction.
- **[Backend](./backend)**: A FastAPI (Python) server handling business logic, rules engine, and database operations.

## Quick Start

### Prerequisites

- Node.js (for frontend)
- Python 3.9+ (for backend)
- PostgreSQL (database)

### Getting Started

Please refer to the detailed setup instructions in the respective directories:

- [Frontend Setup Guide](./frontend/README.md)
- [Backend Setup Guide](./backend/README.md)

## Key Features

- **CardioIQ**: Cardiac risk assessment and triage (Chest pain, ECG, Troponin analysis).
- **TransfusionIQ**: Advanced blood product recommendation engine.
- **Rules Engine**: Deterministic, evidence-based recommendations.

## Deployment

- **Frontend**: Deployed on Vercel (https://clinomize.vercel.app)
- **Backend**: Deployed on Vercel (https://clinomize-api.vercel.app)

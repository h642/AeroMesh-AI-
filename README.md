Markdown# AeroMesh-AI: Operational Deployment & Technical Specification Guide

[![Python 3.10+](https://img.shields.io/badge/python-3.10%25-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![PostGIS](https://img.shields.io/badge/PostGIS-Spatial%25-336791.svg)](https://postgis.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade technical documentation and deployment repository for **AeroMesh-AI**, tailored for integration with the Ministry of Earth Sciences (MoES) and NCMRWF infrastructure.

---

## 📌 Core Architecture Overview

```text
[ Data Ingestion Layer ]
  ├── NCUM 12km Ensembles ──► [ Dask Worker Cluster ]
  └── ERA5 Climatology    ──► [ Dask Worker Cluster ]

[ AI Processing Core ]
  [ Dask Worker Cluster ] ──► Stage 1: Icosahedral GNN
  Stage 1: Icosahedral GNN ──► Stage 2: Physics-Guided Diffusion

[ Emergency Dispatch ]
  Stage 2: Physics-Guided Diffusion ──► FastAPI REST API
  ├── FastAPI REST API ──► CAP v1.2 XML Generator
  └── FastAPI REST API ──► NDRF PDF Briefs
```
⚙️ Configuration & Environment Variables
Create a .env file in the root directory before launching containerized services:Code snippet# Server Configuration
```text
HOST=0.0.0.0
PORT=8000
DEBUG=false
WORKERS=4

# Database & Spatial Storage
POSTGRES_USER=aeromesh_admin
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=aeromesh_spatial
DATABASE_URL=postgresql://aeromesh_admin:secure_password_here@localhost:5432/aeromesh_spatial

# Meteorological Model Checkpoints
GNN_MODEL_PATH=weights/stage1_gnn_icosahedral.pt
DIFFUSION_MODEL_PATH=weights/stage2_amplitude_diffusion.pt
MAX_RAM_LIMIT_GB=2.0
```
🐳 Docker Deployment
To spin up the complete backend, worker queue, and spatial database stack using Docker Compose:Build and start containers:
Bash
docker-compose up --build -d
Verify container health:
Bash
docker ps
Access API documentation:

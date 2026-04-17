# Day 12 Lab Submission - Deployment and Production Agent

## Overview

Repository nay la bai nop Day 12 ve:

- localhost vs production
- Docker va containerization
- cloud deployment
- API security
- scaling va reliability
- final production-ready agent

## Files For Grading

Nguoi cham nen xem theo thu tu nay:

1. [MISSION_ANSWERS.md](./MISSION_ANSWERS.md)
2. [DEPLOYMENT.md](./DEPLOYMENT.md)
3. [06-lab-complete](./06-lab-complete)
4. [screenshots](./screenshots)

## Repository Structure

```text
day12_2A202600010_BuiTrongAnh/
├── 01-localhost-vs-production/
├── 02-docker/
├── 03-cloud-deployment/
├── 04-api-gateway/
├── 05-scaling-reliability/
├── 06-lab-complete/
├── screenshots/
├── MISSION_ANSWERS.md
├── DEPLOYMENT.md
└── README.md
```

## Final Project

Thu muc final project la [06-lab-complete](./06-lab-complete).

Project nay bao gom:

- config tu environment variables
- API key authentication
- rate limiting
- cost guard
- health check
- readiness check
- graceful shutdown
- structured logging
- Docker multi-stage
- deploy config cho Railway va Render

## Public Deployment

Final project da duoc deploy that tren Render:

- Public URL: [https://day12-2a202600010-buitronganh.onrender.com](https://day12-2a202600010-buitronganh.onrender.com)

Endpoint public:

- [https://day12-2a202600010-buitronganh.onrender.com/health](https://day12-2a202600010-buitronganh.onrender.com/health)
- [https://day12-2a202600010-buitronganh.onrender.com/ready](https://day12-2a202600010-buitronganh.onrender.com/ready)

Chi tiet test deploy nam trong [DEPLOYMENT.md](./DEPLOYMENT.md).

## Screenshots

Cac screenshot phuc vu cham bai duoc luu tai:

- [dashboard.png](./screenshots/dashboard.png)
- [health.png](./screenshots/health.png)
- [ready.png](./screenshots/ready.png)
- [ask-success.png](./screenshots/ask-success.png)

## Prerequisites For Local Run

De chay local:

- Python 3.11+
- Docker Desktop
- Docker Compose

## How To Run The Final Project Locally

### Option 1: Run with Python

Tu thu muc `06-lab-complete`:

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Test:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
curl http://127.0.0.1:8000/ask -X POST \
  -H "X-API-Key: dev-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is deployment?"}'
```

### Option 2: Run with Docker

Tu thu muc `06-lab-complete`:

```bash
docker compose up --build
```

Test:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/ask -X POST \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is deployment?"}'
```

## Production Readiness Check

Trong thu muc final project co script kiem tra nhanh:

```bash
cd 06-lab-complete
python check_production_ready.py
```

Ket qua hien tai:

- `20/20 checks passed`
- `100%`
- `PRODUCTION READY`

## How To Review Each Part

### Part 1

- Code: [01-localhost-vs-production](./01-localhost-vs-production)
- Answers: [MISSION_ANSWERS.md](./MISSION_ANSWERS.md)

### Part 2

- Code: [02-docker](./02-docker)
- Answers: [MISSION_ANSWERS.md](./MISSION_ANSWERS.md)

### Part 3

- Code: [03-cloud-deployment](./03-cloud-deployment)
- Deployment proof: [DEPLOYMENT.md](./DEPLOYMENT.md)

### Part 4

- Code: [04-api-gateway](./04-api-gateway)
- Answers: [MISSION_ANSWERS.md](./MISSION_ANSWERS.md)

### Part 5

- Code: [05-scaling-reliability](./05-scaling-reliability)
- Answers: [MISSION_ANSWERS.md](./MISSION_ANSWERS.md)

### Part 6

- Final code: [06-lab-complete](./06-lab-complete)
- Final deployment: [DEPLOYMENT.md](./DEPLOYMENT.md)
- Final answers: [MISSION_ANSWERS.md](./MISSION_ANSWERS.md)

## Notes For Instructor

- Final grading should focus on the final deliverable in `06-lab-complete`.
- The service is deployed and publicly reachable.
- The protected `/ask` endpoint requires `X-API-Key`.
- The real deployment secret is not committed to the repository.

## Submission Summary

- Mission answers completed: yes
- Final project completed: yes
- Final project deployed: yes
- Public URL working: yes
- Screenshots included: yes

# Intelligent Wi-Fi Hotspot Sharing Detection using Machine Learning

Real-time system that detects unauthorized Wi-Fi hotspot / tethering activity using passive network traffic analysis and Machine Learning.

Router MAC filtering controls **who can join** the Wi-Fi. This system detects **who is sharing a hotspot** among devices that are already connected. Both can be used together.

## Features

- **Real-time Detection Agent** – Captures live traffic, extracts behavioral features (TTL variance, TCP window diversity, rates), and classifies devices using Random Forest
- **Private IP filter** – Only local Wi-Fi devices (192.168.x.x, 10.x.x.x, 172.16–31.x.x); public IPs like 8.8.8.8 are ignored
- **FastAPI Backend** – Auth (JWT), Devices, Alerts, Analytics APIs
- **One alert per device** – Updates existing open alert instead of creating duplicates
- **Advanced Dashboard** – React + TypeScript + Tailwind dark theme with live stats, charts, device management, whitelist, and alert sound
- **Docker Compose** – One-command startup for database + backend
- **Privacy-preserving** – Only packet headers are analyzed, no payload inspection

## Project Structure

```
intelligent-wifi-hotspot-detection/
├── agent/                 # Detection Engine (Scapy + ML)
├── backend/               # FastAPI Backend
├── frontend/              # React Dashboard
├── scripts/               # Training & utility scripts
├── docker-compose.yml
└── README.md
```

## Architecture

```
Wi-Fi Traffic → Detection Agent (Scapy + ML) → FastAPI Backend → PostgreSQL
                                                      ↓
                                               Web Dashboard
```

## Quick Start

### 1. Train the Model (optional – model already included)

```bash
cd scripts
pip install scikit-learn joblib numpy
python train_model.py
```

### 2. Start Backend + Database

```bash
docker compose up -d db backend
```

- Backend: http://localhost:8000  
- API Docs: http://localhost:8000/docs  

### 3. Create Admin User

**Swagger UI:** open docs → `POST /api/v1/auth/register` → Try it out

**PowerShell:**

```powershell
$body = @{
  email = "admin@example.com"
  full_name = "Admin"
  password = "admin123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -ContentType "application/json" -Body $body
```

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: http://localhost:5173

### 5. Run Detection Agent

From the **project root** (not inside the `agent` folder):

```bash
python -m agent.main
```

Create a `.env` file in the **project root**:

```env
NETWORK_INTERFACE=Wi-Fi
FEATURE_WINDOW_SECONDS=12
MIN_PACKETS_FOR_CLASSIFICATION=15
MODEL_PATH=agent/ml/models/hotspot_rf.joblib
CONFIDENCE_THRESHOLD=0.75
SENSITIVITY=balanced
BACKEND_URL=http://127.0.0.1:8000/api/v1/events/ingest
BACKEND_TIMEOUT=5.0
MAX_RETRIES=3
CLASSIFICATION_INTERVAL=5.0
LOG_LEVEL=INFO
```

**Windows notes:**
- Install [Npcap](https://npcap.com/#download) with WinPcap API-compatible mode
- Set `NETWORK_INTERFACE` to your active adapter name (often `Wi-Fi`)
- Run terminal as Administrator if packet capture fails

**Linux/macOS:** packet capture often requires `sudo`.

## Default Credentials (after register)

- Email: `admin@example.com`
- Password: `admin123`

## How Detection Works

1. Agent sniffs packets on the configured network interface  
2. Only **private/local** source IPs are analyzed  
3. Features are extracted (TTL diversity, TCP window patterns, packet/byte rates, etc.)  
4. Random Forest classifies each device as `normal` or `hotspot`  
5. Backend stores the device and event; creates or updates a single open alert  
6. Dashboard shows live status; **Whitelist** suppresses alerts for trusted devices  

## Alert Behavior

| Condition | Result |
|-----------|--------|
| Label = hotspot and confidence ≥ 55% | Alert created or updated |
| Confidence ≥ 85% | Severity = high |
| Device is whitelisted | No alert |
| Same device again while alert is open | Same alert is **updated** (no spam) |

## MAC Filtering Compatibility

If a user enables MAC filtering on their router:

- Only allowed devices can join the Wi-Fi  
- This system still works the same way on those connected devices  
- It does **not** replace router MAC filtering  
- It adds a second layer: detect hotspot/tethering among connected devices  

## Tech Stack

| Layer | Technology |
|-------|------------|
| Detection | Python, Scapy, Scikit-learn |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, JWT |
| Frontend | React 18, TypeScript, Vite, Tailwind, Recharts, TanStack Query |
| Deployment | Docker Compose |

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/register` | Create admin |
| POST | `/api/v1/events/ingest` | Agent pushes detections |
| GET | `/api/v1/devices/` | List devices |
| GET | `/api/v1/alerts/` | List alerts |
| GET | `/api/v1/analytics/summary` | Dashboard stats |

## License

This project was developed as a Final Year Project and can be extended for research or commercial use.

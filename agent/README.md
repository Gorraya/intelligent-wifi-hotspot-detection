# Detection Agent

**Intelligent Wi-Fi Hotspot Sharing Detection using Machine Learning**

This is the core detection engine of the system.

## Features

- Live packet capture using Scapy
- Privacy-preserving feature extraction (TTL, TCP Window, rates)
- Random Forest based classification
- Real-time result publishing to Backend API
- Configurable sensitivity (Strict / Balanced / Relaxed)
- Structured logging

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run (requires root/capabilities for packet capture)
sudo python -m agent.main
```

## Configuration

All settings can be controlled via environment variables or `.env` file:

- `NETWORK_INTERFACE` → e.g. `eth0`, `wlan0`, `enp0s3`
- `FEATURE_WINDOW_SECONDS` → default 12
- `SENSITIVITY` → `strict` | `balanced` | `relaxed`
- `BACKEND_URL` → Backend ingest endpoint
- `MODEL_PATH` → Path to trained `.joblib` model

## Project Structure

```
agent/
├── main.py                 # Entry point
├── config.py               # Settings
├── capture/                # Packet sniffing
├── features/               # Feature engineering
├── ml/                     # Model loading & prediction
├── publisher/              # Backend communication
└── utils/                  # Logging & helpers
```

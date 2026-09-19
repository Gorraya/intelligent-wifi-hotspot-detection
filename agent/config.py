"""
Configuration management for the Detection Agent.
All settings are loaded from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    # Network Interface
    network_interface: str = Field(default="eth0", description="Interface to sniff on")
    
    # Feature extraction
    feature_window_seconds: int = Field(default=12, description="Sliding window size in seconds")
    min_packets_for_classification: int = Field(default=15, description="Minimum packets before classifying")
    
    # ML
    model_path: str = Field(default="ml/models/hotspot_rf.joblib", description="Path to trained model")
    confidence_threshold: float = Field(default=0.75, ge=0.5, le=0.99)
    sensitivity: Literal["strict", "balanced", "relaxed"] = Field(default="balanced")
    
    # Backend communication
    backend_url: str = Field(default="http://backend:8000/api/v1/events/ingest")
    backend_timeout: float = Field(default=5.0)
    max_retries: int = Field(default=3)
    
    # Agent behavior
    classification_interval: float = Field(default=5.0, description="How often to run classification (seconds)")
    log_level: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_threshold(sensitivity: str) -> float:
    """Map sensitivity setting to confidence threshold."""
    mapping = {
        "strict": 0.65,
        "balanced": 0.75,
        "relaxed": 0.85,
    }
    return mapping.get(sensitivity, 0.75)


settings = Settings()

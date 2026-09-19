"""
HTTP client for sending detection results to the Backend API.
"""

from __future__ import annotations

import time
from typing import Dict, Any
import httpx
from loguru import logger
from agent.config import settings


class ResultPublisher:
    def __init__(self):
        self.backend_url = settings.backend_url
        self.timeout = settings.backend_timeout
        self.max_retries = settings.max_retries

    def publish(self, payload: Dict[str, Any]) -> bool:
        """
        Send detection result to backend.
        Returns True if successful.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(self.backend_url, json=payload)
                    if response.status_code in (200, 201, 202):
                        logger.debug(f"Successfully published result for {payload.get('ip_address')}")
                        return True
                    else:
                        logger.warning(
                            f"Backend returned {response.status_code}: {response.text}"
                        )
            except Exception as e:
                logger.error(f"Publish attempt {attempt} failed: {e}")

            if attempt < self.max_retries:
                time.sleep(1.5 * attempt)

        return False

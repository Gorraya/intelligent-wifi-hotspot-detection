"""
Machine Learning model loader and predictor for hotspot detection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple
import joblib
import numpy as np
from loguru import logger

from agent.features.extractor import IPFeatures


class HotspotClassifier:
    """
    Wrapper around a trained Random Forest (or similar) model.
    """

    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        if not self.model_path.exists():
            logger.warning(
                f"Model file not found at {self.model_path}. "
                "Classifier will run in rule-based fallback mode."
            )
            self.model = None
            return

        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Successfully loaded model from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None

    def predict(self, features: IPFeatures) -> Tuple[str, float]:
        """
        Predict whether the IP is a hotspot or normal device.

        Returns:
            (label, confidence)
            label: "hotspot" or "normal"
            confidence: float between 0 and 1
        """
        vector = features.to_vector().reshape(1, -1)

        if self.model is None:
            return self._rule_based_fallback(features)

        try:
            # Most sklearn classifiers support predict_proba
            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(vector)[0]
                # Assuming classes are ordered as [normal, hotspot] or check classes_
                classes = list(self.model.classes_)
                if "hotspot" in classes:
                    hotspot_idx = classes.index("hotspot")
                else:
                    hotspot_idx = 1 if len(classes) > 1 else 0

                confidence = float(proba[hotspot_idx])
                label = "hotspot" if confidence >= 0.5 else "normal"
                return label, confidence
            else:
                prediction = self.model.predict(vector)[0]
                label = str(prediction).lower()
                return label, 0.80  # default confidence when proba not available

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._rule_based_fallback(features)

    def _rule_based_fallback(self, features: IPFeatures) -> Tuple[str, float]:
        """
        Simple heuristic when ML model is not available.
        Useful for initial development and testing.
        """
        score = 0.0

        if features.unique_ttl_count >= 3:
            score += 0.35
        elif features.unique_ttl_count == 2:
            score += 0.20

        if features.unique_window_count >= 3:
            score += 0.30
        elif features.unique_window_count == 2:
            score += 0.15

        if features.ttl_std > 8.0:
            score += 0.20

        if features.packet_rate > 80:
            score += 0.10

        label = "hotspot" if score >= 0.50 else "normal"
        confidence = min(score, 0.95)
        return label, confidence

"""
Train a Random Forest model for Hotspot vs Normal classification.
Uses synthetic but realistic feature distributions based on known behavioral patterns.
"""

import os
import sys
from pathlib import Path
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Output path
MODEL_DIR = Path(__file__).parent.parent / "agent" / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "hotspot_rf.joblib"


def generate_synthetic_data(n_normal=2000, n_hotspot=1200):
    """
    Generate realistic synthetic features.
    
    Feature order (must match FeatureExtractor.to_vector()):
    0 unique_ttl_count
    1 ttl_std
    2 unique_window_count
    3 avg_window_size
    4 packet_rate
    5 byte_rate
    6 syn_ratio
    7 active_flows_approx
    """
    rng = np.random.default_rng(42)

    # ----- Normal devices -----
    # Usually 1 TTL, low variance, 1 window size
    normal = np.column_stack([
        rng.integers(1, 2, n_normal),                          # unique_ttl_count (almost always 1)
        rng.uniform(0.0, 3.0, n_normal),                       # ttl_std (very low)
        rng.integers(1, 3, n_normal),                          # unique_window_count
        rng.normal(60000, 8000, n_normal).clip(1000, 65535),   # avg_window_size
        rng.uniform(5, 60, n_normal),                          # packet_rate
        rng.uniform(500, 15000, n_normal),                     # byte_rate
        rng.uniform(0.01, 0.15, n_normal),                     # syn_ratio
        rng.integers(1, 4, n_normal),                          # active_flows_approx
    ])

    # ----- Hotspot devices -----
    # Multiple TTLs, higher std, multiple window sizes
    hotspot = np.column_stack([
        rng.integers(2, 6, n_hotspot),                         # unique_ttl_count (2+)
        rng.uniform(5.0, 25.0, n_hotspot),                     # ttl_std (higher)
        rng.integers(2, 7, n_hotspot),                         # unique_window_count
        rng.normal(45000, 15000, n_hotspot).clip(1000, 65535), # avg_window_size (more varied)
        rng.uniform(30, 250, n_hotspot),                       # packet_rate (higher)
        rng.uniform(8000, 80000, n_hotspot),                   # byte_rate
        rng.uniform(0.08, 0.35, n_hotspot),                    # syn_ratio
        rng.integers(3, 15, n_hotspot),                        # active_flows_approx
    ])

    X = np.vstack([normal, hotspot]).astype(np.float32)
    y = np.array(["normal"] * n_normal + ["hotspot"] * n_hotspot)

    # Shuffle
    indices = rng.permutation(len(X))
    return X[indices], y[indices]


def train():
    print("=" * 60)
    print("Training Hotspot Detection Model")
    print("=" * 60)

    X, y = generate_synthetic_data()
    print(f"Dataset size : {len(X)} samples")
    print(f"Features     : {X.shape[1]}")
    print(f"Class balance: {np.unique(y, return_counts=True)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    print("\nTraining Random Forest...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("\n===== Evaluation =====")
    print(f"Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Feature importance
    print("\nFeature Importances:")
    feature_names = [
        "unique_ttl_count", "ttl_std", "unique_window_count", "avg_window_size",
        "packet_rate", "byte_rate", "syn_ratio", "active_flows_approx"
    ]
    for name, imp in sorted(zip(feature_names, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {name:25s} {imp:.4f}")

    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")
    print("=" * 60)
    return model


if __name__ == "__main__":
    train()

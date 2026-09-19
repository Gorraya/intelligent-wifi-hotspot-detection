"""
Detection Agent - Main Entry Point
Intelligent Wi-Fi Hotspot Sharing Detection using Machine Learning
"""

from __future__ import annotations

import time
import signal
import sys
from datetime import datetime, timezone

from agent.config import settings, get_threshold
from agent.utils.logger import log
from agent.capture.sniffer import PacketSniffer
from agent.features.extractor import FeatureExtractor
from agent.ml.model import HotspotClassifier
from agent.publisher.api_client import ResultPublisher


class DetectionAgent:
    def __init__(self):
        self.extractor = FeatureExtractor(window_seconds=settings.feature_window_seconds)
        self.classifier = HotspotClassifier(model_path=settings.model_path)
        self.publisher = ResultPublisher()
        self.threshold = get_threshold(settings.sensitivity)

        self.sniffer = PacketSniffer(
            interface=settings.network_interface,
            packet_callback=self._on_packet,
        )

        self._running = False

    def _is_private_ip(self, ip: str) -> bool:
        """Sirf local network / Wi-Fi devices allow karo. Public IPs skip."""
        try:
            parts = [int(x) for x in ip.split(".")]
            if len(parts) != 4:
                return False
            if parts[0] == 10:
                return True
            if parts[0] == 172 and 16 <= parts[1] <= 31:
                return True
            if parts[0] == 192 and parts[1] == 168:
                return True
            return False
        except Exception:
            return False

    def _on_packet(self, src_ip: str, ttl, window_size, length: int, is_syn: bool):
        if not self._is_private_ip(src_ip):
            return
        self.extractor.add_packet(src_ip, ttl, window_size, length, is_syn)

    def _classify_and_publish(self):
        active_ips = self.extractor.get_active_ips()

        for ip in active_ips:
            features = self.extractor.compute_features(ip)
            if features is None or features.packet_count < settings.min_packets_for_classification:
                continue

            label, confidence = self.classifier.predict(features)

            payload = {
                "ip_address": ip,
                "mac_address": None,
                "label": label,
                "confidence": round(confidence, 4),
                "features": {
                    "unique_ttl_count": features.unique_ttl_count,
                    "ttl_std": round(features.ttl_std, 2),
                    "unique_window_count": features.unique_window_count,
                    "avg_window_size": round(features.avg_window_size, 1),
                    "packet_rate": round(features.packet_rate, 2),
                    "byte_rate": round(features.byte_rate, 1),
                    "syn_ratio": round(features.syn_ratio, 3),
                    "active_flows_approx": features.active_flows_approx,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            success = self.publisher.publish(payload)
            if success and label == "hotspot" and confidence >= self.threshold:
                log.warning(
                    f"HOTSPOT DETECTED | IP: {ip} | Confidence: {confidence:.2%} | "
                    f"TTL unique: {features.unique_ttl_count} | Windows: {features.unique_window_count}"
                )

    def start(self):
        log.info("=" * 60)
        log.info("Intelligent Wi-Fi Hotspot Sharing Detection Agent")
        log.info("=" * 60)
        log.info(f"Interface     : {settings.network_interface}")
        log.info(f"Window        : {settings.feature_window_seconds}s")
        log.info(f"Sensitivity   : {settings.sensitivity} (threshold={self.threshold})")
        log.info(f"Backend URL   : {settings.backend_url}")
        log.info("Filter        : Private IPs only (192.168.x.x / 10.x.x.x / 172.16-31.x.x)")
        log.info("=" * 60)

        self._running = True
        self.sniffer.start()

        try:
            while self._running:
                self._classify_and_publish()
                time.sleep(settings.classification_interval)
        except KeyboardInterrupt:
            log.info("Received shutdown signal")
        finally:
            self.stop()

    def stop(self):
        self._running = False
        self.sniffer.stop()
        log.info("Detection Agent stopped cleanly")


def main():
    agent = DetectionAgent()

    def signal_handler(sig, frame):
        agent.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    agent.start()


if __name__ == "__main__":
    main()
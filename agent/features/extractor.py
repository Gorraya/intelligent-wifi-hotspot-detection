"""
Feature extraction from network packet headers.
Focuses on privacy-preserving behavioral signals for hotspot detection.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, Deque, Optional, Set
import time
import statistics
import numpy as np


@dataclass
class PacketInfo:
    timestamp: float
    ttl: Optional[int]
    window_size: Optional[int]
    packet_length: int
    is_syn: bool = False


@dataclass
class IPFeatures:
    """Aggregated features for a single source IP within the current window."""
    ip: str
    unique_ttl_count: int = 0
    ttl_std: float = 0.0
    unique_window_count: int = 0
    avg_window_size: float = 0.0
    packet_rate: float = 0.0
    byte_rate: float = 0.0
    syn_ratio: float = 0.0
    active_flows_approx: int = 0
    packet_count: int = 0
    last_updated: float = field(default_factory=time.time)

    def to_vector(self) -> np.ndarray:
        """Return feature vector in consistent order for the ML model."""
        return np.array([
            self.unique_ttl_count,
            self.ttl_std,
            self.unique_window_count,
            self.avg_window_size,
            self.packet_rate,
            self.byte_rate,
            self.syn_ratio,
            self.active_flows_approx,
        ], dtype=np.float32)


class FeatureExtractor:
    """
    Maintains a sliding window of packets per source IP
    and computes behavioral features used for hotspot detection.
    """

    def __init__(self, window_seconds: int = 12):
        self.window_seconds = window_seconds
        self._packets: Dict[str, Deque[PacketInfo]] = defaultdict(lambda: deque())
        self._ttls: Dict[str, Set[int]] = defaultdict(set)
        self._windows: Dict[str, Set[int]] = defaultdict(set)

    def add_packet(
        self,
        src_ip: str,
        ttl: Optional[int],
        window_size: Optional[int],
        packet_length: int,
        is_syn: bool = False,
    ) -> None:
        """Add a new packet to the sliding window of the given source IP."""
        now = time.time()
        info = PacketInfo(
            timestamp=now,
            ttl=ttl,
            window_size=window_size,
            packet_length=packet_length,
            is_syn=is_syn,
        )
        self._packets[src_ip].append(info)

        if ttl is not None:
            self._ttls[src_ip].add(ttl)
        if window_size is not None:
            self._windows[src_ip].add(window_size)

        self._cleanup(src_ip, now)

    def _cleanup(self, src_ip: str, now: float) -> None:
        """Remove packets older than the sliding window."""
        cutoff = now - self.window_seconds
        q = self._packets[src_ip]

        while q and q[0].timestamp < cutoff:
            q.popleft()

        # Rebuild sets from remaining packets for accuracy
        if not q:
            self._ttls[src_ip].clear()
            self._windows[src_ip].clear()
            return

        self._ttls[src_ip] = {p.ttl for p in q if p.ttl is not None}
        self._windows[src_ip] = {p.window_size for p in q if p.window_size is not None}

    def compute_features(self, src_ip: str) -> Optional[IPFeatures]:
        """
        Compute features for a source IP.
        Returns None if there are not enough packets.
        """
        q = self._packets.get(src_ip)
        if not q or len(q) < 5:
            return None

        now = time.time()
        self._cleanup(src_ip, now)
        q = self._packets.get(src_ip)
        if not q or len(q) < 5:
            return None

        ttls = [p.ttl for p in q if p.ttl is not None]
        windows = [p.window_size for p in q if p.window_size is not None]
        lengths = [p.packet_length for p in q]
        syn_count = sum(1 for p in q if p.is_syn)

        duration = max(q[-1].timestamp - q[0].timestamp, 0.001)

        features = IPFeatures(
            ip=src_ip,
            unique_ttl_count=len(self._ttls[src_ip]),
            ttl_std=float(statistics.pstdev(ttls)) if len(ttls) > 1 else 0.0,
            unique_window_count=len(self._windows[src_ip]),
            avg_window_size=float(statistics.mean(windows)) if windows else 0.0,
            packet_rate=len(q) / duration,
            byte_rate=sum(lengths) / duration,
            syn_ratio=syn_count / len(q),
            active_flows_approx=max(1, syn_count),  # simple approximation
            packet_count=len(q),
            last_updated=now,
        )
        return features

    def get_active_ips(self) -> list[str]:
        """Return list of IPs that currently have packets in the window."""
        now = time.time()
        active = []
        for ip in list(self._packets.keys()):
            self._cleanup(ip, now)
            if self._packets[ip]:
                active.append(ip)
            else:
                # Clean empty entries
                self._packets.pop(ip, None)
                self._ttls.pop(ip, None)
                self._windows.pop(ip, None)
        return active

"""
Packet capture module using Scapy.
Runs in a separate thread and feeds packets to the FeatureExtractor.
"""

from __future__ import annotations

import threading
from typing import Callable, Optional
from scapy.all import sniff, IP, TCP, Ether
from loguru import logger


class PacketSniffer:
    """
    Asynchronous packet sniffer.
    """

    def __init__(
        self,
        interface: str,
        packet_callback: Callable[[str, Optional[int], Optional[int], int, bool], None],
    ):
        self.interface = interface
        self.packet_callback = packet_callback
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _process_packet(self, packet) -> None:
        if self._stop_event.is_set():
            return

        if IP not in packet:
            return

        src_ip = packet[IP].src
        ttl = packet[IP].ttl
        length = len(packet)
        window_size = None
        is_syn = False

        if TCP in packet:
            window_size = packet[TCP].window
            is_syn = packet[TCP].flags.S and not packet[TCP].flags.A

        try:
            self.packet_callback(src_ip, ttl, window_size, length, is_syn)
        except Exception as e:
            logger.error(f"Error in packet callback: {e}")

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            logger.warning("Sniffer already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(f"Packet sniffer started on interface: {self.interface}")

    def _run(self) -> None:
        try:
            sniff(
                iface=self.interface,
                prn=self._process_packet,
                store=False,
                stop_filter=lambda _: self._stop_event.is_set(),
            )
        except Exception as e:
            logger.error(f"Sniffer error: {e}")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("Packet sniffer stopped")

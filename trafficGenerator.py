"""Compatibility wrapper for older imports.

New code should import from loadbalancer.traffic.
"""

from loadbalancer.traffic import generate_traffic, slow_print

__all__ = ["generate_traffic", "slow_print"]

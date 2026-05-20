"""Compatibility wrapper for older imports.

New code should import from loadbalancer.server.
"""

from loadbalancer.server import Server

__all__ = ["Server"]

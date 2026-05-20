"""Compatibility wrapper for older imports.

New code should import from loadbalancer.algorithms.
"""

from loadbalancer.algorithms import LeastConnectionLoadBalancer, RoundRobinLoadBalancer

__all__ = ["LeastConnectionLoadBalancer", "RoundRobinLoadBalancer"]

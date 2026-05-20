"""Compatibility wrapper for older imports.

New code should import from loadbalancer.rl_env.
"""

from loadbalancer.rl_env import LoadBalancingEnv

__all__ = ["LoadBalancingEnv"]

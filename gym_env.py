"""Compatibility wrapper for older imports.

New code should import from loadbalancer.gym_env.
"""

from loadbalancer.gym_env import GymLoadBalancingEnv

__all__ = ["GymLoadBalancingEnv"]

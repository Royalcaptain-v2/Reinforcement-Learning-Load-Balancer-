import gymnasium as gym
import numpy as np
from gymnasium import spaces


class GymLoadBalancingEnv(gym.Env):
    def __init__(self, core_env):
        super().__init__()
        self.core_env = core_env

        n_servers = len(core_env.servers)
        self.action_space = spaces.Discrete(n_servers)

        # State columns: busy time, active flag, latency, estimated response time.
        self.observation_space = spaces.Box(
            low=0.0,
            high=np.inf,
            shape=(n_servers, 4),
            dtype=np.float32,
        )

    def reset(self, seed=None, options=None):
        state = self.core_env.reset()
        return np.array(state, dtype=np.float32), {}

    def step(self, action):
        next_state, reward, done, info = self.core_env.step(action)
        return np.array(next_state, dtype=np.float32), reward, done, False, info

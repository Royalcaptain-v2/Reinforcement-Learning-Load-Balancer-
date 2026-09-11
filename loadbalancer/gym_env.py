# gymnasium import for wrapping simulation to make it PPO understandable
import gymnasium as gym
# ppo understand numerical data in the form of an array there numpy
import numpy as np
# spaces module of gymnasium decides the choice boundary 
from gymnasium import spaces

#class inheriting the componenets of base class gym.Env
class GymLoadBalancingEnv(gym.Env):

    #constructor passed with custom simulation logic in var core_env
    def __init__(self, core_env):
        # calling superclass constructor to setup base components
        super().__init__()
        self.core_env = core_env

        n_servers = len(core_env.servers)

        # discrete actions allowed on server from 0 till n_servers-1
        self.action_space = spaces.Discrete(n_servers)

        # State columns: busy time, active flag, latency, estimated response time.
        self.observation_space = spaces.Box(
            low=0.0, #lowest possible value allowed
            high=np.inf, #highest possible value allowed
            shape=(n_servers, 4), 
            dtype=np.float32, # allowed data type in numpy array 
        )

    # calls reset from rl_env.py to reset environment state when starting a new episode
    def reset(self, seed=None, options=None):
        state = self.core_env.reset()
        return np.array(state, dtype=np.float32), {}

    #defines the updated state of environment when a decision is made for any server
    def step(self, action):
        next_state, reward, done, info = self.core_env.step(action)
        return np.array(next_state, dtype=np.float32), reward, done, False, info

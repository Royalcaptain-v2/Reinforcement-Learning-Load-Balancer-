import random

from loadbalancer.rl_env import LoadBalancingEnv
from loadbalancer.server import Server

servers = [
    Server("S1", 2),
    Server("S2", 2),
    Server("S3", 2),
]

traffic = [
    {"id": 1, "arrival_time": 0},
    {"id": 2, "arrival_time": 1},
    {"id": 3, "arrival_time": 1},
    {"id": 4, "arrival_time": 3},
]

env = LoadBalancingEnv(servers, traffic)

state = env.reset()
done = False

print("---- RANDOM AGENT TEST ----")

while not done:
    action = random.randint(0, len(servers) - 1)
    state, reward, done, _ = env.step(action)
    print("action:", action, "reward:", reward)

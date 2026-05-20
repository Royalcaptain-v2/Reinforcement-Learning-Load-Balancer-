import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from stable_baselines3 import PPO
from loadbalancer.gym_env import GymLoadBalancingEnv
from loadbalancer.rl_env import LoadBalancingEnv
from loadbalancer.server import Server
from loadbalancer.traffic import generate_traffic

MODEL_PATH = PROJECT_ROOT / "models" / "ppo_load_balancer"
LATENCY_CHOICES = [1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 10.0]
INACTIVE_CHANCE = 0.25

random.seed(42)

servers = [
    Server("A",base_processing_time=1),
    Server("B",base_processing_time=1.5),
    Server("C",base_processing_time=2)
]

traffic = generate_traffic()

core_env = LoadBalancingEnv(
    servers,
    traffic,
    randomize_conditions=True,
    traffic_generator=generate_traffic,
    latency_choices=LATENCY_CHOICES,
    inactive_chance=INACTIVE_CHANCE,
    seed=42,
)
env = GymLoadBalancingEnv(core_env)

model = PPO(
    "MlpPolicy",    env,
    verbose=0,
    learning_rate=3e-4,
    gamma=0.99,
    max_grad_norm=0.3,
    n_steps=128,
    batch_size=64,
    ent_coef=0.01,
    seed=42
)

model.learn(total_timesteps=60_000)

model.save(str(MODEL_PATH))

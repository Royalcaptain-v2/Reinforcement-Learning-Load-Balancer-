import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from loadbalancer.algorithms import LeastConnectionLoadBalancer, RoundRobinLoadBalancer
from loadbalancer.gym_env import GymLoadBalancingEnv
from loadbalancer.rl_env import LoadBalancingEnv
from loadbalancer.server import Server
from loadbalancer.traffic import generate_traffic

MODEL_PATH = PROJECT_ROOT / "models" / "ppo_load_balancer"

def apply_server_conditions(server_list):
    server_list[1].latency_multiplier = 5.0
    server_list[2].is_active = False
    # server_list[0].is_active = False 
    server_list[0].latency_multiplier = 10.0


def print_decision_header(algorithm_name):
    print(f"\n--- {algorithm_name} Decision Log ---")
    print("Req | Arrival | Server | Response Time | Server Busy Till")
    print("---------------------------------------------------------")


def print_decision(req, server, response_time, busy_till=None):
    server_name = "None" if server == 0 or server is None else server.name
    response_text = "N/A" if response_time is None else f"{response_time:.2f}"

    if busy_till is None:
        busy_text = "N/A" if server == 0 or server is None else f"{server.server_busy_till_time:.2f}"
    else:
        busy_text = f"{busy_till:.2f}"

    print(
        f"{req['id']:>3} | "
        f"{req['arrival_time']:>7.2f} | "
        f"{server_name:^6} | "
        f"{response_text:^13} | "
        f"{busy_text:^16}"
    )


random.seed(42)

# recreate servers & traffic (same as training)
servers = [
    Server("A", base_processing_time=1),
    Server("B", base_processing_time=1.5),
    Server("C", base_processing_time=2),
]

traffic = generate_traffic()
for req in traffic:
    print(req)

apply_server_conditions(servers)

core_env = LoadBalancingEnv(servers, traffic)

env = DummyVecEnv([
    lambda: GymLoadBalancingEnv(core_env)
])

model = PPO.load(str(MODEL_PATH))

obs = env.reset()

total_response_time = 0
max_rt = 0
done = False
print_decision_header("PPO (RL)")
while not done:
    action, _ = model.predict(obs, deterministic=True)

    action_index = int(action[0])
    current_req = traffic[core_env.current_request_index]
    selected_server = servers[action_index]

    obs, reward, done, info = env.step(action)
    raw_response_time = info[0]["response_time"]
    response_time = 1000 if raw_response_time is None else raw_response_time
    busy_till = None if raw_response_time is None else current_req["arrival_time"] + raw_response_time
    print_decision(current_req, selected_server, response_time, busy_till)
    total_response_time += response_time
    max_rt = max(max_rt , response_time)
print("")
print("\n--- Routing with Reinforcement Learning Algorithm")
print("PPO Total Response Time:", total_response_time)
print("PPO Avg Response Time:", total_response_time / len(traffic))
print("PPO max Response Time:" , max_rt )

#--Round Robin--

servers_rr = [
    Server("A", base_processing_time=1),
    Server("B", base_processing_time=1.5),
    Server("C", base_processing_time=2),
]

apply_server_conditions(servers_rr)

rr_total_rt = 0
rr_max_rt = 0

rr_balancer = RoundRobinLoadBalancer(servers_rr)

print_decision_header("Round Robin")

for req in traffic:
    server = rr_balancer.select_server()

    rt = server.handle_request(req["arrival_time"])
    rt = 0 if rt is None else rt
    print_decision(req, server, rt)
    rr_total_rt += rt
    rr_max_rt = max(rr_max_rt, rt)

rr_avg_rt = rr_total_rt / len(traffic)

print("\n--- Routing with Round Robin")
print("RR Total Response Time:", rr_total_rt)
print("RR Avg Response Time:", rr_avg_rt)
print("RR Max Response Time:", rr_max_rt)

# LEAST CONNECTIONS EVALUATION

servers_lc = [
    Server("A", base_processing_time=1),
    Server("B", base_processing_time=1.5),
    Server("C", base_processing_time=2),
]

apply_server_conditions(servers_lc)

lc_total_rt = 0
lc_max_rt = 0

print_decision_header("Least Connections")

for req in traffic:
    # choose server with least current load
    server = LeastConnectionLoadBalancer(servers_lc).select_server()

    rs = server.handle_request(req["arrival_time"])
    rs = 0 if rs is None else rs
    print_decision(req, server, rs)
    lc_total_rt += rs
    lc_max_rt = max(lc_max_rt, rs)

lc_avg_rt = lc_total_rt / len(traffic)

print("\n--- Routing with Least Connections")
print("LC Total Response Time:", lc_total_rt)
print("LC Avg Response Time:", lc_avg_rt)
print("LC Max Response Time:", lc_max_rt)

# FINAL COMPARISON

print("\n================ FINAL COMPARISON ================")
print("Algorithm           Avg RT")
print("---------------------------------")
print(f"Round Robin         {rr_avg_rt:.3f}")
print(f"Least Connections   {lc_avg_rt:.3f}")
print(f"PPO (RL)            {total_response_time / len(traffic):.3f}")
print("==================================================")

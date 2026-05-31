import os
import random
from functools import lru_cache
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from stable_baselines3 import PPO

from loadbalancer.algorithms import LeastConnectionLoadBalancer, RoundRobinLoadBalancer
from loadbalancer.gym_env import GymLoadBalancingEnv
from loadbalancer.rl_env import LoadBalancingEnv
from loadbalancer.server import Server
from loadbalancer.traffic import generate_traffic


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = PROJECT_ROOT / "public" / "static"
MODEL_PATH = PROJECT_ROOT / "models" / "ppo_load_balancer"

app = FastAPI(title="Reinforcement Learning Load Balancer")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ServerInput(BaseModel):
    name: str
    base_processing_time: float
    latency_multiplier: float
    is_active: bool


class SimulationRequest(BaseModel):
    seed: int = 42
    servers: list[ServerInput]


def default_servers():
    return [
        ServerInput(name="A", base_processing_time=1.0, latency_multiplier=10.0, is_active=True),
        ServerInput(name="B", base_processing_time=1.5, latency_multiplier=5.0, is_active=True),
        ServerInput(name="C", base_processing_time=2.0, latency_multiplier=1.0, is_active=True),
    ]


@lru_cache(maxsize=1)
def load_model():
    return PPO.load(str(MODEL_PATH))


def make_servers(server_inputs):
    servers = []

    for server_input in server_inputs:
        server = Server(server_input.name, server_input.base_processing_time)
        server.latency_multiplier = server_input.latency_multiplier
        server.is_active = server_input.is_active
        servers.append(server)

    return servers


def make_traffic(seed):
    random.seed(seed)
    return generate_traffic()


def record_decision(req, server, response_time):
    if server == 0 or server is None:
        server_name = "NONE"
        busy_till = None
    else:
        server_name = server.name
        busy_till = None if response_time is None else req["arrival_time"] + response_time

    return {
        "request_id": req["id"],
        "arrival_time": req["arrival_time"],
        "server": server_name,
        "response_time": 1000 if response_time is None else response_time,
        "busy_till": busy_till,
    }


def summarize(name, decisions):
    total = sum(decision["response_time"] for decision in decisions)
    max_response_time = max(decision["response_time"] for decision in decisions) if decisions else 0
    counts = {}

    for decision in decisions:
        counts[decision["server"]] = counts.get(decision["server"], 0) + 1

    return {
        "name": name,
        "total_response_time": total,
        "avg_response_time": total / len(decisions) if decisions else 0,
        "max_response_time": max_response_time,
        "counts": counts,
        "decisions": decisions,
    }


def simulate_ppo(server_inputs, traffic):
    servers = make_servers(server_inputs)
    core_env = LoadBalancingEnv(servers, traffic)
    env = GymLoadBalancingEnv(core_env)
    model = load_model()
    obs, _ = env.reset()
    decisions = []
    done = False

    while not done:
        action, _ = model.predict(obs, deterministic=True)
        action_index = int(action)
        req = traffic[core_env.current_request_index]
        selected_server = servers[action_index]
        obs, reward, terminated, truncated, info = env.step(action_index)
        decisions.append(record_decision(req, selected_server, info["response_time"]))
        done = terminated or truncated

    return summarize("PPO (RL)", decisions)


def simulate_round_robin(server_inputs, traffic):
    servers = make_servers(server_inputs)
    load_balancer = RoundRobinLoadBalancer(servers)
    decisions = []

    for req in traffic:
        server = load_balancer.select_server()
        response_time = None if server == 0 else server.handle_request(req["arrival_time"])
        decisions.append(record_decision(req, server, response_time))

    return summarize("Round Robin", decisions)


def simulate_least_connections(server_inputs, traffic):
    servers = make_servers(server_inputs)
    decisions = []

    for req in traffic:
        server = LeastConnectionLoadBalancer(servers).select_server()
        response_time = None if server == 0 else server.handle_request(req["arrival_time"])
        decisions.append(record_decision(req, server, response_time))

    return summarize("Least Connections", decisions)


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/simulate")
def simulate(request: SimulationRequest):
    server_inputs = request.servers or default_servers()
    traffic = make_traffic(request.seed)
    algorithms = [
        simulate_ppo(server_inputs, traffic),
        simulate_round_robin(server_inputs, traffic),
        simulate_least_connections(server_inputs, traffic),
    ]

    winner = min(algorithms, key=lambda algorithm: algorithm["avg_response_time"])

    return {
        "seed": request.seed,
        "traffic_count": len(traffic),
        "servers": [server.model_dump() for server in server_inputs],
        "algorithms": algorithms,
        "winner": winner["name"],
    }

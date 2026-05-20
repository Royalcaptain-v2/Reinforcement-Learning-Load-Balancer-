from loadbalancer.algorithms import RoundRobinLoadBalancer
from loadbalancer.server import Server

# Create servers
servers = [
    Server("S1", base_processing_time=2),
    Server("S2", base_processing_time=2),
    Server("S3", base_processing_time=2),
]

lb = RoundRobinLoadBalancer(servers)

# Sample traffic
traffic = [
    {"id": 1, "arrival_time": 0},
    {"id": 2, "arrival_time": 1},
    {"id": 3, "arrival_time": 2},
    {"id": 4, "arrival_time": 3},
    {"id": 5, "arrival_time": 4},
]

print("---- ROUND ROBIN TEST ----")

#check when server becomes unactive
servers[1].is_active =False

for req in traffic:
    server = lb.select_server()
    response_time = server.handle_request(req["arrival_time"])

    print(
        f"Request {req['id']} -> {server.name} | "
        f"response_time = {response_time}"
    )

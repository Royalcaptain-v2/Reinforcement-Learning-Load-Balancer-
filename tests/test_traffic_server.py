from loadbalancer.server import Server

# create server
server = Server("Server-1", base_processing_time=2)
# server.latency_multiplier =3
# server.is_active = False

# fake traffic (manual)
traffic = [
    {"id": 1, "arrival_time": 0},
    {"id": 2, "arrival_time": 1},
    {"id": 3, "arrival_time": 1},
    {"id": 4, "arrival_time": 3},
]

for req in traffic:
    rt = server.handle_request(req["arrival_time"])
    print(f"Request {req['id']} response time: {rt}")

from loadbalancer.algorithms import LeastConnectionLoadBalancer
from loadbalancer.server import Server

servers = [
    Server("S1", base_processing_time=2),
    Server("S2", base_processing_time=2),
    Server("S3", base_processing_time=2),
]

lb = LeastConnectionLoadBalancer(servers)

traffic = [
    {"id": 1, "arrival_time": 0},
    {"id": 2, "arrival_time": 1},
    {"id": 3, "arrival_time": 1},
    {"id": 4, "arrival_time": 3},
]

print("---- LEAST CONNECTIONS TEST ----")
# servers[0].is_active =False #failure testing
for req in traffic:
    #prints which server is busy till what time
    for serverc in servers:
        print(
            f"server {serverc.name} will be busy till {serverc.server_busy_till_time}"
        )

    #selecting best server and providing the request to it
    server = lb.select_server()
    rt = server.handle_request(req["arrival_time"])

    print(
        f"Request {req['id']} arrive at time {req['arrival_time']} |"
        f"Request {req['id']} -> {server.name} | "
        f"busy_till={server.server_busy_till_time} | "
        f"response_time={rt}"
    )

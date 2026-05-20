from loadbalancer.server import Server

server = Server("Server-1",base_processing_time=2)
print("Initial queue:", server.queue_length)

server.receive_request()
server.receive_request()

print("Queue after 2 request: ",server.queue_length)

time1 = server.process_request()
print("Processed 1 request in: ",time1)

print("Queue now:" ,server.queue_length)

server.latency_multiplier=3
time2 = server.process_request()
print("Process delayed: ", time2)

server.is_active =False
result = server.receive_request()
print("Server After being inactive receives request: ",result)

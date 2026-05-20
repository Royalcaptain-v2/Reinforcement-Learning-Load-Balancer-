import random 
import time
import sys
def generate_traffic():
    #list to store requests 
    traffic = []

    #request counter to uniquely identify the requests increments with each new request 
    request_id = 0

    #variable to decide how long our simuation works 
    total_time = 5

    #number of request that arrive per second from user without spikes
    requests_per_second = 3

    #variable to stimulate spikes into our requests 
    spike_mutiplier = 3 

    #30% of the time , traffic spikes and remains normal for 70% of the time 
    spike_chance =0.7 



    for current_time in range(total_time): #runs for time 0 till (total_time - 1)

        #using random function to ensure some seconds have more request/traffic and some less.
        if(random.random()<spike_chance):
            current_rate = requests_per_second * spike_mutiplier
        else:
            current_rate = requests_per_second
        for _ in range (current_rate) : #runs for iteration 0 till (current_rate - 1)
            request_id+=1 

            #stores generated time and incremented id into traffic list 
            traffic.append({
                "id":request_id,
                "arrival_time":round(current_time * 0.3 , 1)
            })
        
    return traffic

def slow_print(text, delay=0.05):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()


# print("")
# print("")
# time.sleep(5)
# slow_print("=======Generating Traffic=======")
# time.sleep(5)
# GREEN = "\033[92m"
# RESET = "\033[0m"
# traffic = generate_traffic()
# for req in traffic:
    # slow_print(f"Request {req['id']} arrives at time T = {req['arrival_time']} ")
#     time.sleep(1)


class Server:
    def __init__(self,name, base_processing_time):
        #name for server identification
        self.name = name

        #processing time for the server
        self.base_processing_time = base_processing_time

        #length of the queue
        self.queue_length = 0

        #to stimulate the latency of the server 
        self.latency_multiplier =1.0

        #Server status -> Active/Inactive
        self.is_active  = True

        #variable to know when server is busy 
        self.server_busy_till_time =0 #server idle

    def receive_request(self):
        #checks whether is active or not 
        if not self.is_active:
            return None 
        
        #if status is active then add the request to queue
        self.queue_length+=1

    def process_request(self):
        if self.queue_length == 0:
            return 0
        
        self.queue_length-=1

        #calculating processing time of the request 
        processing_time = self.base_processing_time * self.latency_multiplier
        return processing_time
    
    def handle_request(self,arrival_time):
        if not self.is_active:
            return None 
        
        #waiting logic 
        start_time =  max(arrival_time , self.server_busy_till_time)
        
        processing_time = self.base_processing_time * self.latency_multiplier

        finish_time = start_time + processing_time

        #update time after which server becomes free
        self.server_busy_till_time = finish_time
        
        response_time  = finish_time - arrival_time

        return response_time


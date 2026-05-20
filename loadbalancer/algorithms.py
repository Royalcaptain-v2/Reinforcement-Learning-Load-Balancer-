
#Round Robin Load Balancer 
class RoundRobinLoadBalancer:
    def __init__(self, servers):
        #passing list of server to the variable 
        self.servers = servers 

        #current index of the accessed server on the list
        self.current_index = 0

    def select_server(self):
        attempts = 0

        #loop through server list 
        while (attempts < len(self.servers)):
            server = self.servers[self.current_index]

            #index increment with circular logic when reach the end of list 
            self.current_index = (self.current_index + 1) % len(self.servers)

        #return the server if active at current index
            if server.is_active:
                return server
            
            attempts+=1

        #if all servers are off return None
        return 0
    

#Least Connections Load Balancer 
class LeastConnectionLoadBalancer:
    def __init__(self , servers):
        self.servers = servers
    
    def select_server(self):
        active_servers= []

        #check for all active servers
        for server in self.servers:
            if server.is_active:
                active_servers.append(server)
        
        #if not found any active servers then return None
        if not active_servers:
            return 0
        
        best_server = active_servers[0]

        #traffic sent to server which is least busy
        for server in active_servers:
            if server.server_busy_till_time < best_server.server_busy_till_time:
                best_server = server
        
        return best_server
    
            
        
import math
import random


class LoadBalancingEnv:
    def __init__(
        self,
        servers,
        traffic,
        randomize_conditions=False,
        traffic_generator=None,
        latency_choices=None,
        inactive_chance=0.25,
        seed=None,
    ):
        self.servers = servers
        self.traffic = traffic

        # Training can randomize traffic and server conditions per episode.
        self.randomize_conditions = randomize_conditions
        self.traffic_generator = traffic_generator
        self.latency_choices = latency_choices or [1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 10.0]
        self.inactive_chance = inactive_chance
        self.rng = random.Random(seed)

        # Preserve configured evaluation conditions across resets.
        self.initial_server_conditions = [
            {
                "is_active": server.is_active,
                "latency_multiplier": server.latency_multiplier,
            }
            for server in self.servers
        ]

        self.current_request_index = 0

    def reset(self):
        self.current_request_index = 0

        if self.traffic_generator is not None:
            self.traffic = self.traffic_generator()

        if self.randomize_conditions:
            self._randomize_server_conditions()

        for index, server in enumerate(self.servers):
            server.server_busy_till_time = 0
            if not self.randomize_conditions:
                server.is_active = self.initial_server_conditions[index]["is_active"]
                server.latency_multiplier = self.initial_server_conditions[index]["latency_multiplier"]

        state = self._get_state()
        for server_state in state:
            for value in server_state:
                if not math.isfinite(value):
                    raise RuntimeError("NaN in reset state")

        return state

    def _randomize_server_conditions(self):
        active_count = 0

        for server in self.servers:
            server.is_active = self.rng.random() >= self.inactive_chance
            server.latency_multiplier = self.rng.choice(self.latency_choices)

            if server.is_active:
                active_count += 1

        if active_count == 0:
            self.rng.choice(self.servers).is_active = True

    def _get_state(self):
        state = []

        if self.current_request_index < len(self.traffic):
            current_arrival_time = self.traffic[self.current_request_index]["arrival_time"]
        else:
            current_arrival_time = self.traffic[-1]["arrival_time"]

        for server in self.servers:
            busy = min(server.server_busy_till_time / 100.0, 10.0)
            active = 1.0 if server.is_active else 0.0

            latency = server.latency_multiplier
            if latency is None or latency != latency or latency > 10:
                latency = 10.0
            latency = latency / 10.0

            if server.is_active:
                processing_time = server.base_processing_time * server.latency_multiplier
                estimated_response_time = (
                    max(current_arrival_time, server.server_busy_till_time)
                    + processing_time
                    - current_arrival_time
                )
            else:
                estimated_response_time = 1000

            estimated_response_time = min(estimated_response_time / 100.0, 10.0)
            state.append([busy, active, latency, estimated_response_time])

        return state

    def step(self, action):
        done = False
        info = {"response_time": None}

        req = self.traffic[self.current_request_index]
        arrival_time = req["arrival_time"]
        selected_server = self.servers[action]

        best_response_time = None
        for server in self.servers:
            if server.is_active:
                possible_start_time = max(arrival_time, server.server_busy_till_time)
                possible_processing_time = server.base_processing_time * server.latency_multiplier
                possible_response_time = possible_start_time + possible_processing_time - arrival_time

                if best_response_time is None or possible_response_time < best_response_time:
                    best_response_time = possible_response_time

        if not selected_server.is_active:
            reward = -1000
        else:
            response_time = selected_server.handle_request(arrival_time)
            if response_time is None or response_time != response_time:
                reward = -1000
            else:
                regret = response_time - best_response_time
                reward = -float((response_time + (2 * regret)) / 10)
                info["response_time"] = response_time

        self.current_request_index += 1
        if self.current_request_index >= len(self.traffic):
            done = True

        next_state = self._get_state()

        return next_state, reward, done, info

# Reinforcement Learning Load Balancer

A FastAPI web app with a neon frontend for simulating server traffic routing with PPO reinforcement learning, Round Robin, and Least Connections load-balancing algorithms.

## Project Structure

```text
Project-LoadBalancer/
|-- app/                    # FastAPI application
|   `-- main.py
|-- loadbalancer/           # Core simulation package
|   |-- algorithms.py       # Round Robin and Least Connections
|   |-- gym_env.py          # Gymnasium wrapper for PPO
|   |-- rl_env.py           # RL environment and reward logic
|   |-- server.py           # Server model
|   `-- traffic.py          # Traffic generation helpers
|-- public/                 # Frontend served by FastAPI
|   |-- index.html
|   `-- static/
|       |-- styles.css
|       `-- app.js
|-- models/                 # Trained PPO model
|   `-- ppo_load_balancer.zip
|-- scripts/                # Training/evaluation scripts
|-- tests/                  # Local demo scripts
|-- docs/                   # Project documentation assets
|-- render.yaml             # Render deployment config
|-- requirements.txt        # Python dependencies
`-- .python-version         # Python version
```



# Reinforcement Learning Load Balancer

A FastAPI web app for simulating server traffic routing with PPO reinforcement learning, Round Robin, and Least Connections load-balancing algorithms.

## Project Structure

```text
Project-LoadBalancer/
├── app/                    # FastAPI application entry point
│   └── main.py
├── loadbalancer/           # Core simulation package
│   ├── algorithms.py       # Round Robin and Least Connections
│   ├── gym_env.py          # Gymnasium wrapper for PPO
│   ├── rl_env.py           # RL environment and reward logic
│   ├── server.py           # Server model
│   └── traffic.py          # Traffic generation helpers
├── static/                 # Frontend files served by FastAPI
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── models/                 # Trained PPO model
│   └── ppo_load_balancer.zip
├── scripts/                # Command-line training/evaluation scripts
│   ├── train_ppo.py
│   └── evaluate_ppo.py
├── tests/                  # Local test/demo scripts
├── docs/                   # Project documentation assets
├── requirements.txt        # Python dependencies
└── render.yaml             # Render deployment config
```

The root-level `server.py`, `load_balancer.py`, `rl_env.py`, `gym_env.py`, and `trafficGenerator.py` files are compatibility wrappers for older imports. New code should import from the `loadbalancer` package.

## Run Locally

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## Train PPO

```powershell
python scripts/train_ppo.py
```

The trained model is saved to `models/ppo_load_balancer.zip`.

## Evaluate PPO

```powershell
python scripts/evaluate_ppo.py
```

## Deploy On Render

Render uses `render.yaml`:

```text
Build Command: pip install -r requirements.txt
Start Command: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

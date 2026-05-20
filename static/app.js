// Default server setup shown when the simulation console first opens.
const defaultServers = [
  { name: "A", base_processing_time: 1.0, latency_multiplier: 10.0, is_active: true },
  { name: "B", base_processing_time: 1.5, latency_multiplier: 5.0, is_active: true },
  { name: "C", base_processing_time: 2.0, latency_multiplier: 1.0, is_active: true }
];

let servers = structuredClone(defaultServers);
let activeDecisionIndex = 0;

// DOM references for controls and rendered output areas.
const enterButton = document.querySelector(".enter-button");
const simulationPage = document.getElementById("simulationPage");
const seedSlider = document.getElementById("seedSlider");
const seedValue = document.getElementById("seedValue");
const serverControlGrid = document.getElementById("serverControlGrid");
const runSimulationButton = document.getElementById("runSimulationButton");
const resultInsight = document.getElementById("resultInsight");
const metricsGrid = document.getElementById("metricsGrid");
const serverLoadGrid = document.getElementById("serverLoadGrid");
const decisionTabs = document.getElementById("decisionTabs");
const decisionTableBody = document.getElementById("decisionTableBody");

// Keeps the intro page orbit animation active.
document.body.classList.add("system-ready");

// Number formatting used by metrics, sliders, and tables.
function formatNumber(value) {
  return Number(value).toFixed(2);
}

function formatPercent(value) {
  return `${formatNumber(value)}%`;
}

// Builds the server sliders and active/off toggles from current server state.
function renderServerControls() {
  serverControlGrid.innerHTML = servers.map((server, index) => `
    <article class="server-control ${server.is_active ? "" : "off"}">
      <div class="server-control-head">
        <div>
          <div class="server-control-title">Server ${server.name}</div>
          <small>${server.is_active ? "Active node" : "Offline node"}</small>
        </div>
        <label class="active-toggle">
          <input type="checkbox" ${server.is_active ? "checked" : ""} data-index="${index}" data-field="is_active">
          Active
        </label>
      </div>

      <div class="server-slider">
        <label>
          <span>Latency</span>
          <strong>x${formatNumber(server.latency_multiplier)}</strong>
        </label>
        <input type="range" min="1" max="10" step="0.5" value="${server.latency_multiplier}" data-index="${index}" data-field="latency_multiplier">
      </div>

      <div class="server-slider">
        <label>
          <span>Base Clock</span>
          <strong>${formatNumber(server.base_processing_time)}</strong>
        </label>
        <input type="range" min="0.5" max="5" step="0.5" value="${server.base_processing_time}" data-index="${index}" data-field="base_processing_time">
      </div>
    </article>
  `).join("");

  serverControlGrid.querySelectorAll("input").forEach((input) => {
    input.addEventListener("input", (event) => {
      const index = Number(event.target.dataset.index);
      const field = event.target.dataset.field;
      servers[index][field] = field === "is_active" ? event.target.checked : Number(event.target.value);
      renderServerControls();
    });
  });
}

// Creates the comparison sentence above the metric cards.
function computeInsight(result) {
  const ppo = result.algorithms.find((algorithm) => algorithm.name === "PPO (RL)");
  const baselines = result.algorithms.filter((algorithm) => algorithm.name !== "PPO (RL)");
  const beaten = baselines.filter((algorithm) => ppo.avg_response_time < algorithm.avg_response_time);

  resultInsight.classList.remove("ppo-good", "baseline-good");

  if (beaten.length > 0) {
    resultInsight.classList.add("ppo-good");
    const lines = beaten.map((algorithm) => {
      const improvement = ((algorithm.avg_response_time - ppo.avg_response_time) / algorithm.avg_response_time) * 100;
      return `${formatPercent(improvement)} better than ${algorithm.name}`;
    });
    return `PPO performed better in this scenario: ${lines.join(", ")}.`;
  }

  resultInsight.classList.add("baseline-good");
  const winner = result.algorithms.find((algorithm) => algorithm.name === result.winner);
  const gap = ((ppo.avg_response_time - winner.avg_response_time) / ppo.avg_response_time) * 100;
  return `${winner.name} performed best in this scenario. It is ${formatPercent(gap)} better than PPO by average response time.`;
}

// Renders average, total, and max response-time metrics for each algorithm.
function renderMetrics(result) {
  metricsGrid.innerHTML = result.algorithms.map((algorithm) => `
    <article class="metric-card ${algorithm.name === result.winner ? "best" : ""}">
      <div class="metric-name">${algorithm.name}</div>
      <div class="metric-values">
        <div class="metric-value">
          <span class="metric-label">Average</span>
          <strong>${formatNumber(algorithm.avg_response_time)}</strong>
        </div>
        <div class="metric-value">
          <span class="metric-label">Total</span>
          <strong>${formatNumber(algorithm.total_response_time)}</strong>
        </div>
        <div class="metric-value">
          <span class="metric-label">Max</span>
          <strong>${formatNumber(algorithm.max_response_time)}</strong>
        </div>
      </div>
    </article>
  `).join("");
}

// Shows how many requests each algorithm routed to each server.
function renderServerLoads(result) {
  const maxCount = Math.max(
    1,
    ...result.algorithms.flatMap((algorithm) => ["A", "B", "C"].map((serverName) => algorithm.counts[serverName] || 0))
  );

  serverLoadGrid.innerHTML = result.algorithms.map((algorithm) => `
    <article class="load-card">
      <h3>${algorithm.name}</h3>
      ${["A", "B", "C"].map((serverName) => {
        const count = algorithm.counts[serverName] || 0;
        const width = (count / maxCount) * 100;
        return `
          <div class="server-bar">
            <span>${serverName}</span>
            <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
            <strong>${count}</strong>
          </div>
        `;
      }).join("")}
    </article>
  `).join("");
}

// Builds tabs for switching between algorithm decision tables.
function renderDecisionTabs(result) {
  decisionTabs.innerHTML = result.algorithms.map((algorithm, index) => `
    <button class="decision-tab ${index === activeDecisionIndex ? "active" : ""}" type="button" data-index="${index}">
      ${algorithm.name}
    </button>
  `).join("");

  decisionTabs.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      activeDecisionIndex = Number(button.dataset.index);
      renderDecisionTabs(result);
      renderDecisions(result.algorithms[activeDecisionIndex]);
    });
  });
}

// Renders request-by-request decisions for one selected algorithm.
function renderDecisions(algorithm) {
  decisionTableBody.innerHTML = algorithm.decisions.map((decision) => `
    <tr>
      <td>${decision.request_id}</td>
      <td>${formatNumber(decision.arrival_time)}</td>
      <td>${decision.server}</td>
      <td>${formatNumber(decision.response_time)}</td>
      <td>${decision.busy_till === null ? "N/A" : formatNumber(decision.busy_till)}</td>
    </tr>
  `).join("");
}

// Updates all output panels after a simulation response comes back.
function renderResult(result) {
  resultInsight.textContent = computeInsight(result);
  renderMetrics(result);
  renderServerLoads(result);
  renderDecisionTabs(result);
  renderDecisions(result.algorithms[activeDecisionIndex]);
}

// Calls the FastAPI simulation endpoint using the current slider values.
async function runSimulation() {
  runSimulationButton.disabled = true;
  runSimulationButton.textContent = "Running";
  resultInsight.textContent = "Running all algorithms and collecting routing decisions...";
  resultInsight.classList.remove("ppo-good", "baseline-good");

  try {
    const response = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        seed: Number(seedSlider.value),
        servers,
      }),
    });

    if (!response.ok) {
      throw new Error(`Simulation request failed with status ${response.status}`);
    }

    const simulationResult = await response.json();
    activeDecisionIndex = 0;
    renderResult(simulationResult);
  } catch (error) {
    resultInsight.textContent = error.message;
    resultInsight.classList.add("baseline-good");
  } finally {
    runSimulationButton.disabled = false;
    runSimulationButton.textContent = "Run Simulation";
  }
}

// Page events. The intro fades out before the simulation console is shown.
enterButton.addEventListener("click", () => {
  document.body.classList.add("transitioning-to-sim");

  setTimeout(() => {
    document.body.classList.add("simulation-active");
    simulationPage.classList.remove("hidden");
    simulationPage.classList.add("reveal");
    runSimulation();
  }, 520);
});

seedSlider.addEventListener("input", () => {
  seedValue.textContent = seedSlider.value;
});

runSimulationButton.addEventListener("click", runSimulation);

renderServerControls();

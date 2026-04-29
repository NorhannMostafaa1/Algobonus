const data = window.APP_DATA;

const scenarioSelect = document.getElementById("scenarioSelect");
const startSelect = document.getElementById("startSelect");
const endSelect = document.getElementById("endSelect");
const raceButton = document.getElementById("raceButton");
const resetButton = document.getElementById("resetButton");
const hotspotCards = document.getElementById("hotspotCards");
const recommendationList = document.getElementById("recommendationList");
const networkSvg = document.getElementById("networkSvg");
const dijkstraStats = document.getElementById("dijkstraStats");
const astarStats = document.getElementById("astarStats");
const dijkstraLog = document.getElementById("dijkstraLog");
const astarLog = document.getElementById("astarLog");

const nodeById = new Map(data.nodes.map((node) => [node.id, node]));
const scenarioNames = Object.keys(data.predictions);
const state = {
  currentScenario: scenarioNames[0],
  edgeEls: new Map(),
  nodeEls: new Map(),
};

function normalizeNodes() {
  const xs = data.nodes.map((node) => node.x);
  const ys = data.nodes.map((node) => node.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  const nodes = data.nodes.map((node) => ({
    ...node,
    sx: 90 + ((node.x - minX) / (maxX - minX)) * 820,
    sy: 510 - ((node.y - minY) / (maxY - minY)) * 390,
  }));

  const coreNodes = nodes.filter(
    (node) => node.sx > 260 && node.sx < 710 && node.sy > 100 && node.sy < 360
  );
  const centroid = {
    x: coreNodes.reduce((sum, node) => sum + node.sx, 0) / coreNodes.length,
    y: coreNodes.reduce((sum, node) => sum + node.sy, 0) / coreNodes.length,
  };

  for (const [index, node] of nodes.entries()) {
    if (!coreNodes.includes(node)) continue;
    let dx = node.sx - centroid.x;
    let dy = node.sy - centroid.y;
    let distance = Math.hypot(dx, dy);

    if (distance < 1) {
      const angle = (index / nodes.length) * Math.PI * 2;
      dx = Math.cos(angle);
      dy = Math.sin(angle);
      distance = 1;
    }

    const expansion = Math.max(0, 165 - distance) * 0.42;
    node.sx += (dx / distance) * expansion;
    node.sy += (dy / distance) * expansion;
  }

  const anchorPositions = new Map(nodes.map((node) => [node.id, { x: node.sx, y: node.sy }]));

  for (let step = 0; step < 160; step += 1) {
    for (let i = 0; i < nodes.length; i += 1) {
      const a = nodes[i];
      const anchor = anchorPositions.get(a.id);
      let shiftX = (anchor.x - a.sx) * 0.03;
      let shiftY = (anchor.y - a.sy) * 0.03;

      for (let j = i + 1; j < nodes.length; j += 1) {
        const b = nodes[j];
        const dx = a.sx - b.sx;
        const dy = a.sy - b.sy;
        const distance = Math.hypot(dx, dy) || 0.01;
        const minDistance = a.id.startsWith("F") || b.id.startsWith("F") ? 42 : 48;

        if (distance < minDistance) {
          const force = ((minDistance - distance) / minDistance) * 3.8;
          const pushX = (dx / distance) * force;
          const pushY = (dy / distance) * force;
          shiftX += pushX;
          shiftY += pushY;
          b.sx -= pushX;
          b.sy -= pushY;
        }
      }

      a.sx = Math.max(74, Math.min(930, a.sx + shiftX));
      a.sy = Math.max(84, Math.min(514, a.sy + shiftY));
    }
  }

  return nodes.map((node) => {
    const angle = Math.atan2(node.sy - centroid.y, node.sx - centroid.x);
    const labelSide = Math.cos(angle) >= 0 ? "right" : "left";
    const labelWidth = Math.max(112, node.name.length * 6.45 + 36);
    return {
      ...node,
      labelSide,
      labelWidth,
    };
  });
}

const screenNodes = normalizeNodes();
const screenNodeById = new Map(screenNodes.map((node) => [node.id, node]));

function congestionColor(ratio) {
  if (ratio < 0.72) return "#3d8b64";
  if (ratio < 0.92) return "#d7a12f";
  if (ratio < 1.04) return "#d3663f";
  return "#962f2f";
}

function formatNode(id) {
  const node = nodeById.get(id);
  return node ? node.name : id;
}

function describeCongestion(ratio) {
  if (ratio < 0.72) return "Low";
  if (ratio < 0.92) return "Moderate";
  if (ratio < 1.04) return "Heavy";
  return "Critical";
}

function edgePath(fromNode, toNode, roadId) {
  const dx = toNode.sx - fromNode.sx;
  const dy = toNode.sy - fromNode.sy;
  const distance = Math.hypot(dx, dy) || 1;
  const nx = -dy / distance;
  const ny = dx / distance;
  const [leftId, rightId] = [fromNode.id, toNode.id].sort();
  const direction = roadId === `${leftId}-${rightId}` ? 1 : -1;
  const bend = Math.min(40, Math.max(16, distance * 0.14)) * direction;
  const cx = (fromNode.sx + toNode.sx) / 2 + nx * bend;
  const cy = (fromNode.sy + toNode.sy) / 2 + ny * bend;
  return `M ${fromNode.sx} ${fromNode.sy} Q ${cx} ${cy} ${toNode.sx} ${toNode.sy}`;
}

function updateNodeFocus() {
  const startId = startSelect.value;
  const endId = endSelect.value;
  for (const [id, group] of state.nodeEls.entries()) {
    group.classList.remove("start", "end", "focus");
    if (id === startId) group.classList.add("start", "focus");
    if (id === endId) group.classList.add("end", "focus");
  }
}

function buildGraph(scenarioName) {
  const predictions = new Map(
    data.predictions[scenarioName].map((item) => [item.road_id, item])
  );
  const graph = new Map();

  for (const road of data.roads) {
    const forecast = predictions.get(road.id);
    const edge = {
      roadId: road.id,
      from: road.from,
      to: road.to,
      weight: forecast.travel_cost,
      ratio: forecast.congestion_ratio,
      distance: road.distance_km,
    };
    if (!graph.has(road.from)) graph.set(road.from, []);
    if (!graph.has(road.to)) graph.set(road.to, []);
    graph.get(road.from).push(edge);
    graph.get(road.to).push({ ...edge, from: road.to, to: road.from });
  }

  return graph;
}

function drawNetwork() {
  networkSvg.innerHTML = "";
  state.edgeEls.clear();
  state.nodeEls.clear();

  const scenarioPredictions = new Map(
    data.predictions[state.currentScenario].map((item) => [item.road_id, item])
  );

  const caption = document.createElementNS("http://www.w3.org/2000/svg", "text");
  caption.setAttribute("x", "24");
  caption.setAttribute("y", "34");
  caption.setAttribute("class", "map-caption");
  caption.textContent = `${state.currentScenario} congestion forecast`;
  networkSvg.appendChild(caption);

  const subcaption = document.createElementNS("http://www.w3.org/2000/svg", "text");
  subcaption.setAttribute("x", "24");
  subcaption.setAttribute("y", "54");
  subcaption.setAttribute("class", "map-caption map-caption-subtle");
  subcaption.textContent = "Dense central nodes are gently separated to improve readability.";
  networkSvg.appendChild(subcaption);

  for (const road of data.roads) {
    const fromNode = screenNodeById.get(road.from);
    const toNode = screenNodeById.get(road.to);
    const forecast = scenarioPredictions.get(road.id);

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", edgePath(fromNode, toNode, road.id));
    path.setAttribute("class", "edge");
    path.setAttribute("stroke", congestionColor(forecast.congestion_ratio));
    path.setAttribute("stroke-width", String(3.5 + forecast.congestion_ratio * 3.4));
    path.setAttribute("opacity", "0.82");
    const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
    title.textContent = `${formatNode(road.from)} -> ${formatNode(road.to)} | ${describeCongestion(
      forecast.congestion_ratio
    )} congestion | ${Math.round(forecast.predicted_flow_vph)} veh/h`;
    path.appendChild(title);
    networkSvg.appendChild(path);
    state.edgeEls.set(road.id, path);
  }

  for (const node of screenNodes) {
    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    group.setAttribute("class", "node");
    group.dataset.nodeId = node.id;
    if (node.id.startsWith("F")) {
      group.classList.add("facility");
    }

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", node.sx);
    circle.setAttribute("cy", node.sy);
    circle.setAttribute("r", node.id.startsWith("F") ? "7.5" : "10.5");

    const labelX = node.labelSide === "right" ? node.sx + 14 : node.sx - node.labelWidth - 14;
    const labelBg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    labelBg.setAttribute("x", String(labelX));
    labelBg.setAttribute("y", String(node.sy - 15));
    labelBg.setAttribute("rx", "11");
    labelBg.setAttribute("ry", "11");
    labelBg.setAttribute("width", String(node.labelWidth));
    labelBg.setAttribute("height", "28");
    labelBg.setAttribute("class", "node-label-bg");

    const leader = document.createElementNS("http://www.w3.org/2000/svg", "line");
    leader.setAttribute("x1", String(node.sx));
    leader.setAttribute("y1", String(node.sy));
    leader.setAttribute("x2", String(node.labelSide === "right" ? labelX : labelX + node.labelWidth));
    leader.setAttribute("y2", String(node.sy - 1));
    leader.setAttribute("class", "node-leader");

    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", String(labelX + 11));
    text.setAttribute("y", node.sy);
    text.setAttribute("dominant-baseline", "middle");
    text.setAttribute("class", "node-name");
    text.textContent = `${node.id} ${node.name}`;

    const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
    title.textContent = `${node.name} (${node.id}) - ${node.type}`;

    group.appendChild(leader);
    group.appendChild(circle);
    group.appendChild(labelBg);
    group.appendChild(text);
    group.appendChild(title);
    networkSvg.appendChild(group);
    state.nodeEls.set(node.id, group);
  }

  updateNodeFocus();
}

function fillSelectors() {
  for (const scenarioName of scenarioNames) {
    const option = document.createElement("option");
    option.value = scenarioName;
    option.textContent = scenarioName;
    scenarioSelect.appendChild(option);
  }

  const routeNodes = data.nodes.filter(
    (node) => !node.id.startsWith("F") || ["F1", "F2", "F7", "F8"].includes(node.id)
  );

  for (const node of routeNodes) {
    const optionA = document.createElement("option");
    optionA.value = node.id;
    optionA.textContent = `${node.id} - ${node.name}`;
    startSelect.appendChild(optionA);

    const optionB = optionA.cloneNode(true);
    endSelect.appendChild(optionB);
  }

  scenarioSelect.value = state.currentScenario;
  startSelect.value = "7";
  endSelect.value = "5";
}

function setHeaderMetrics() {
  document.getElementById("modelName").textContent = data.metadata.model;
  document.getElementById("modelMae").textContent = `${data.metadata.metrics.mae} veh/h`;
  document.getElementById("modelR2").textContent = data.metadata.metrics.r2;
}

function updateInsights() {
  const selectedScenario = scenarioSelect.value;
  const hotspots = [...data.predictions[selectedScenario]]
    .sort((a, b) => b.congestion_ratio - a.congestion_ratio)
    .slice(0, 6);

  hotspotCards.innerHTML = hotspots
    .map(
      (road) => `
        <article class="card">
          <h3>${formatNode(road.from_id)} -> ${formatNode(road.to_id)}</h3>
          <div class="metric-row"><span>Forecast flow</span><strong>${Math.round(road.predicted_flow_vph)} veh/h</strong></div>
          <div class="metric-row"><span>Capacity usage</span><strong>${Math.round(road.congestion_ratio * 100)}%</strong></div>
          <div class="metric-row"><span>Travel cost</span><strong>${road.travel_cost} h</strong></div>
        </article>
      `
    )
    .join("");
}

function updateRecommendations() {
  recommendationList.innerHTML = data.recommended_new_roads
    .map(
      (road) => `
        <article class="rec-card">
          <h3>${formatNode(road.from_id)} <-> ${formatNode(road.to_id)}</h3>
          <div class="metric-row"><span>Build cost</span><strong>${road.construction_cost_million_egp} M EGP</strong></div>
          <div class="metric-row"><span>Estimated capacity</span><strong>${road.estimated_capacity_vph} veh/h</strong></div>
          <div class="metric-row"><span>Distance</span><strong>${road.distance_km} km</strong></div>
          <div class="metric-row"><span>Priority score</span><strong>${road.score}</strong></div>
        </article>
      `
    )
    .join("");
}

function resetVisualState() {
  for (const edge of state.edgeEls.values()) {
    edge.classList.remove("active-dijkstra", "active-astar", "path-dijkstra", "path-astar");
  }
  for (const node of state.nodeEls.values()) {
    node.classList.remove("visited-dijkstra", "visited-astar");
  }
  dijkstraLog.innerHTML = "";
  astarLog.innerHTML = "";
  dijkstraStats.innerHTML = "";
  astarStats.innerHTML = "";
}

function heuristic(nodeId, targetId) {
  const a = screenNodeById.get(nodeId);
  const b = screenNodeById.get(targetId);
  return Math.hypot(a.sx - b.sx, a.sy - b.sy) / 100;
}

function runSearch(algorithm, graph, start, goal) {
  const frontier = [{ node: start, priority: 0 }];
  const distances = new Map([[start, 0]]);
  const previous = new Map();
  const visited = new Set();
  const steps = [];

  while (frontier.length) {
    frontier.sort((a, b) => a.priority - b.priority);
    const current = frontier.shift();
    if (visited.has(current.node)) continue;
    visited.add(current.node);

    steps.push({
      type: "visit",
      node: current.node,
      score: distances.get(current.node),
    });

    if (current.node === goal) break;

    for (const edge of graph.get(current.node) || []) {
      const candidate = distances.get(current.node) + edge.weight;
      if (candidate < (distances.get(edge.to) ?? Infinity)) {
        distances.set(edge.to, candidate);
        previous.set(edge.to, { node: current.node, roadId: edge.roadId });
        frontier.push({
          node: edge.to,
          priority: candidate + (algorithm === "astar" ? heuristic(edge.to, goal) : 0),
        });
        steps.push({
          type: "relax",
          roadId: edge.roadId,
        });
      }
    }
  }

  const pathNodes = [];
  const pathEdges = [];
  let cursor = goal;
  if (!previous.has(goal) && start !== goal) {
    return { steps, pathNodes, pathEdges, cost: Infinity, visited: visited.size };
  }

  pathNodes.push(cursor);
  while (cursor !== start) {
    const prev = previous.get(cursor);
    if (!prev) break;
    pathEdges.push(prev.roadId);
    cursor = prev.node;
    pathNodes.push(cursor);
  }
  pathNodes.reverse();
  pathEdges.reverse();

  steps.push({
    type: "path",
    pathNodes,
    pathEdges,
  });

  return {
    steps,
    pathNodes,
    pathEdges,
    cost: distances.get(goal) ?? 0,
    visited: visited.size,
  };
}

function renderStats(target, result, fallbackLabel) {
  target.innerHTML = `
    <article class="stat-pill">
      <span>Visited nodes</span>
      <strong>${result.visited}</strong>
    </article>
    <article class="stat-pill">
      <span>Total cost</span>
      <strong>${Number.isFinite(result.cost) ? result.cost.toFixed(2) : "No route"} h</strong>
    </article>
    <article class="stat-pill">
      <span>Route</span>
      <strong>${result.pathNodes.length ? result.pathNodes.join(" -> ") : fallbackLabel}</strong>
    </article>
  `;
}

function appendLog(target, message) {
  const entry = document.createElement("div");
  entry.className = "log-entry";
  entry.textContent = message;
  target.appendChild(entry);
  target.scrollTop = target.scrollHeight;
}

async function playSteps(algorithm, result, logTarget, statTarget) {
  const nodeClass = algorithm === "dijkstra" ? "visited-dijkstra" : "visited-astar";
  const edgeClass = algorithm === "dijkstra" ? "active-dijkstra" : "active-astar";
  const pathClass = algorithm === "dijkstra" ? "path-dijkstra" : "path-astar";

  renderStats(statTarget, result, "Pending");

  for (const step of result.steps) {
    if (step.type === "visit") {
      state.nodeEls.get(step.node)?.classList.add(nodeClass);
      appendLog(
        logTarget,
        `${algorithm.toUpperCase()} visited ${step.node} (${formatNode(step.node)}) with cumulative cost ${step.score.toFixed(2)}`
      );
    }

    if (step.type === "relax") {
      state.edgeEls.get(step.roadId)?.classList.add(edgeClass);
    }

    if (step.type === "path") {
      for (const roadId of step.pathEdges) {
        state.edgeEls.get(roadId)?.classList.add(pathClass);
      }
      renderStats(statTarget, result, "No route");
      appendLog(logTarget, `${algorithm.toUpperCase()} final route: ${step.pathNodes.join(" -> ")}`);
    }

    await new Promise((resolve) => setTimeout(resolve, 180));
  }
}

async function runRace() {
  resetVisualState();
  const graph = buildGraph(scenarioSelect.value);
  const dijkstraResult = runSearch("dijkstra", graph, startSelect.value, endSelect.value);
  const astarResult = runSearch("astar", graph, startSelect.value, endSelect.value);

  await Promise.all([
    playSteps("dijkstra", dijkstraResult, dijkstraLog, dijkstraStats),
    playSteps("astar", astarResult, astarLog, astarStats),
  ]);
}

scenarioSelect.addEventListener("change", () => {
  state.currentScenario = scenarioSelect.value;
  drawNetwork();
  updateInsights();
  resetVisualState();
});

startSelect.addEventListener("change", updateNodeFocus);
endSelect.addEventListener("change", updateNodeFocus);

raceButton.addEventListener("click", runRace);
resetButton.addEventListener("click", resetVisualState);

setHeaderMetrics();
fillSelectors();
drawNetwork();
updateInsights();
updateRecommendations();

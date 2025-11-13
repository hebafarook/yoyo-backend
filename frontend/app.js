const API_BASE = "https://yoyo-backend-uqda.onrender.com/api";

// Views
const viewLanding = document.getElementById("view-landing");
const viewPlayerAuth = document.getElementById("view-player-auth");
const viewPlayerDashboard = document.getElementById("view-player-dashboard");

// Landing buttons
const playerPortalBtn = document.getElementById("playerPortalBtn");

// Auth elements
const playerIdAuth = document.getElementById("playerIdAuth");
const playerNameAuth = document.getElementById("playerNameAuth");
const playerAgeAuth = document.getElementById("playerAgeAuth");
const playerPositionAuth = document.getElementById("playerPositionAuth");
const playerFootAuth = document.getElementById("playerFootAuth");
const playerPasswordAuth = document.getElementById("playerPasswordAuth");
const playerLoginBtn = document.getElementById("playerLoginBtn");
const playerRegisterBtn = document.getElementById("playerRegisterBtn");
const authStatus = document.getElementById("authStatus");

// Dashboard elements
const playerWelcomeText = document.getElementById("playerWelcomeText");
const playerProfileMini = document.getElementById("playerProfileMini");
const logoutBtn = document.getElementById("logoutBtn");

const tabButtons = document.querySelectorAll(".tab-btn");
const tabViews = document.querySelectorAll(".tab-view");

const metricsGrid = document.getElementById("metricsGrid");
const strengthsList = document.getElementById("strengthsList");
const weaknessesList = document.getElementById("weaknessesList");
const recommendationsList = document.getElementById("recommendationsList");
const statusMessage = document.getElementById("statusMessage");

const programStatus = document.getElementById("programStatus");
const programOutput = document.getElementById("programOutput");
const generateProgramBtn = document.getElementById("generateProgramBtn");
const homeSummary = document.getElementById("homeSummary");
const profileDetails = document.getElementById("profileDetails");

let trendChart = null;
let currentPlayer = null; // { id, name, age, position, foot }

function setView(view) {
  viewLanding.classList.add("hidden");
  viewPlayerAuth.classList.add("hidden");
  viewPlayerDashboard.classList.add("hidden");

  if (view === "landing") viewLanding.classList.remove("hidden");
  if (view === "auth") viewPlayerAuth.classList.remove("hidden");
  if (view === "dashboard") viewPlayerDashboard.classList.remove("hidden");
}

function setStatus(msg) {
  statusMessage.textContent = msg || "";
}

// ====== SIMPLE DEMO "AUTH" (LOCAL STORAGE ONLY) ======
const STORAGE_KEY = "yoyo_demo_players";

function loadStoredPlayers() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function saveStoredPlayers(players) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(players));
}

function registerPlayer() {
  const id = playerIdAuth.value.trim();
  const name = playerNameAuth.value.trim();
  const age = Number(playerAgeAuth.value);
  const position = playerPositionAuth.value.trim();
  const foot = playerFootAuth.value.trim();
  const password = playerPasswordAuth.value;

  if (!id || !name || !age || !position || !password) {
    authStatus.textContent = "Please fill all required fields.";
    return;
  }

  const players = loadStoredPlayers();
  if (players[id]) {
    authStatus.textContent = "Player ID already exists. Try logging in.";
    return;
  }

  players[id] = { id, name, age, position, foot, password };
  saveStoredPlayers(players);
  authStatus.textContent = "✅ Registered. You can now log in.";
}

function loginPlayer() {
  const id = playerIdAuth.value.trim();
  const password = playerPasswordAuth.value;

  const players = loadStoredPlayers();
  const player = players[id];

  if (!player || player.password !== password) {
    authStatus.textContent = "Invalid ID or password (demo auth).";
    return;
  }

  currentPlayer = player;
  localStorage.setItem("yoyo_current_player", id);
  authStatus.textContent = "";

  initDashboardForPlayer();
  setView("dashboard");
}

// ====== DASHBOARD & TABS ======

function initDashboardForPlayer() {
  const p = currentPlayer;
  playerWelcomeText.textContent = `Hi ${p.name}, age ${p.age} – ${p.position}`;
  playerProfileMini.textContent = `ID: ${p.id} • ${p.foot || "Foot N/A"}`;

  profileDetails.innerHTML = `
    <p><strong>Player ID:</strong> ${p.id}</p>
    <p><strong>Name:</strong> ${p.name}</p>
    <p><strong>Age:</strong> ${p.age}</p>
    <p><strong>Position:</strong> ${p.position}</p>
    <p><strong>Dominant foot:</strong> ${p.foot || "Not set"}</p>
  `;

  loadHomeSummary();
  loadPlayerReport(); // pre-load report
}

function switchTab(tabName) {
  tabViews.forEach((v) => v.classList.add("hidden"));
  tabButtons.forEach((b) => b.classList.remove("active"));

  document.getElementById(`tab-${tabName}`).classList.remove("hidden");
  document
    .querySelector(`.tab-btn[data-tab="${tabName}"]`)
    .classList.add("active");

  if (tabName === "report") {
    loadPlayerReport();
  }
}

// ====== GAUGE HELPERS ======

function setGaugeNeedle(needleEl, value, max) {
  if (typeof value !== "number" || isNaN(value)) return;
  const clamped = Math.max(0, Math.min(max, value));
  const ratio = clamped / max;
  const angle = -90 + ratio * 180;
  needleEl.style.transform = `translateX(-50%) rotate(${angle}deg)`;
}

function createGaugeCard({ label, value, unit = "", max = 100 }) {
  const card = document.createElement("div");
  card.className = "metric-card gauge-card";

  const displayValue =
    typeof value === "number" && !isNaN(value) ? value : "--";

  card.innerHTML = `
    <div class="gauge-wrap">
      <div class="gauge-shell">
        <div class="gauge-needle"></div>
        <div class="gauge-center"></div>
      </div>
    </div>
    <div class="metric-value">${displayValue}${unit ? " " + unit : ""}</div>
    <div class="metric-label">${label}</div>
  `;

  const needle = card.querySelector(".gauge-needle");
  if (typeof value === "number" && !isNaN(value)) {
    setGaugeNeedle(needle, value, max);
  }
  return card;
}

// ====== API CALLS ======

async function loadPlayerReport() {
  if (!currentPlayer) return;
  const playerId = currentPlayer.id;

  setStatus("Loading player report...");

  try {
    // Latest assessment
    const latestRes = await fetch(
      `${API_BASE}/players/${encodeURIComponent(playerId)}/latest-assessment`
    );

    if (!latestRes.ok) {
      const err = await latestRes.json().catch(() => ({}));
      setStatus(`❌ ${err.detail || "No assessment found for this player."}`);
      metricsGrid.innerHTML = "";
      strengthsList.innerHTML = "";
      weaknessesList.innerHTML = "";
      recommendationsList.innerHTML = "";
      if (trendChart) {
        trendChart.destroy();
        trendChart = null;
      }
      homeSummary.innerHTML = "";
      return;
    }

    const latest = await latestRes.json();
    const m = latest.metrics || {};

    // Gauges
    metricsGrid.innerHTML = "";
    metricsGrid.appendChild(
      createGaugeCard({
        label: "Sprint 30m",
        value: m.sprint_30m,
        unit: "s",
        max: 8,
      })
    );
    metricsGrid.appendChild(
      createGaugeCard({
        label: "Agility test",
        value: m.agility_test,
        unit: "",
        max: 25,
      })
    );
    metricsGrid.appendChild(
      createGaugeCard({
        label: "Reaction time",
        value: m.reaction_time_ms,
        unit: "ms",
        max: 500,
      })
    );
    metricsGrid.appendChild(
      createGaugeCard({
        label: "Beep test level",
        value: m.beep_test_level,
        unit: "",
        max: 20,
      })
    );
    metricsGrid.appendChild(
      createGaugeCard({
        label: "Ball control",
        value: m.ball_control_score,
        unit: "/10",
        max: 10,
      })
    );
    metricsGrid.appendChild(
      createGaugeCard({
        label: "Passing accuracy",
        value: m.passing_accuracy_pct,
        unit: "%",
        max: 100,
      })
    );

    // Lists
    strengthsList.innerHTML = "";
    (latest.strengths || []).forEach((s) => {
      const li = document.createElement("li");
      li.textContent = s;
      strengthsList.appendChild(li);
    });

    weaknessesList.innerHTML = "";
    (latest.weaknesses || []).forEach((s) => {
      const li = document.createElement("li");
      li.textContent = s;
      weaknessesList.appendChild(li);
    });

    recommendationsList.innerHTML = "";
    (latest.recommendations || []).forEach((s) => {
      const li = document.createElement("li");
      li.textContent = s;
      recommendationsList.appendChild(li);
    });

    // Home summary
    homeSummary.innerHTML = `
      <p><strong>Overall score:</strong> ${
        m.overall_score ?? "--"
      }</p>
      <p><strong>Last assessment date:</strong> ${
        latest.created_at
          ? new Date(latest.created_at).toLocaleDateString()
          : "N/A"
      }</p>
    `;

    // History for chart
    const historyRes = await fetch(
      `${API_BASE}/players/${encodeURIComponent(playerId)}/assessments`
    );
    const history = historyRes.ok ? await historyRes.json() : [];

    const labels = history.map((h) =>
      h.created_at
        ? new Date(h.created_at).toLocaleDateString()
        : "Unknown"
    );
    const overallScores = history.map(
      (h) => h.metrics?.overall_score ?? null
    );
    const sprintScores = history.map((h) => h.metrics?.sprint_30m ?? null);
    const passingScores = history.map(
      (h) => h.metrics?.passing_accuracy_pct ?? null
    );

    const ctx = document.getElementById("trendChart").getContext("2d");
    if (trendChart) trendChart.destroy();
    trendChart = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          { label: "Overall Score", data: overallScores },
          { label: "Sprint 30m", data: sprintScores },
          { label: "Passing Accuracy", data: passingScores },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });

    setStatus("✅ Player report loaded.");
  } catch (err) {
    console.error(err);
    setStatus("❌ Error loading player report.");
  }
}

async function generateProgram() {
  if (!currentPlayer) {
    programStatus.textContent = "Log in first.";
    return;
  }

  const playerId = currentPlayer.id;
  programStatus.textContent = "Generating AI program...";

  try {
    const url = `${API_BASE}/programs/generate?player_id=${encodeURIComponent(
      playerId
    )}`;

    const response = await fetch(url, { method: "POST" });
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const detail =
        data.detail ||
        `Error ${response.status}${data.message ? ": " + data.message : ""}`;
      programStatus.textContent = `❌ Failed: ${detail}`;
      return;
    }

    programOutput.textContent =
      data.program || "(No program text returned from backend.)";
    programStatus.textContent = "✅ Program generated.";
  } catch (err) {
    console.error(err);
    programStatus.textContent = "❌ Network error.";
  }
}

async function loadHomeSummary() {
  await loadPlayerReport(); // already updates homeSummary
}

// ====== EVENT WIRING ======
playerPortalBtn.addEventListener("click", () => {
  setView("auth");
});

playerRegisterBtn.addEventListener("click", registerPlayer);
playerLoginBtn.addEventListener("click", loginPlayer);

logoutBtn.addEventListener("click", () => {
  currentPlayer = null;
  localStorage.removeItem("yoyo_current_player");
  setView("landing");
});

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    switchTab(btn.dataset.tab);
  });
});

generateProgramBtn.addEventListener("click", generateProgram);

// Restore session if exists (demo)
(function init() {
  const players = loadStoredPlayers();
  const id = localStorage.getItem("yoyo_current_player");
  if (id && players[id]) {
    currentPlayer = players[id];
    initDashboardForPlayer();
    setView("dashboard");
  } else {
    setView("landing");
  }
})();

// Backend base URL (Render)
const API_BASE = "https://yoyo-backend-uqda.onrender.com/api";

const playerIdInput = document.getElementById("playerId");
const generateBtn = document.getElementById("generateBtn");
const statusMessage = document.getElementById("statusMessage");
const programOutput = document.getElementById("programOutput");

async function generateProgram() {
  const playerId = playerIdInput.value.trim();

  statusMessage.textContent = "";
  programOutput.textContent = "";

  if (!playerId) {
    statusMessage.textContent = "Please enter a player ID first.";
    return;
  }

  statusMessage.textContent = "Generating program, please wait...";

  try {
    const url = `${API_BASE}/programs/generate?player_id=${encodeURIComponent(
      playerId
    )}`;

    const response = await fetch(url, {
      method: "POST",
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const detail =
        data.detail ||
        `Error ${response.status}${
          data.message ? `: ${data.message}` : ""
        }`;
      statusMessage.textContent = `❌ Failed to generate program: ${detail}`;
      return;
    }

    statusMessage.textContent = "✅ Program generated successfully.";

    // Show the markdown/text as plain text for now
    programOutput.textContent =
      data.program || "(No program text returned from backend.)";
  } catch (err) {
    console.error(err);
    statusMessage.textContent =
      "❌ Network error while calling the backend. Check Render URL.";
  }
}

generateBtn.addEventListener("click", generateProgram);

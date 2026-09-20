// File: frontend/app.js
const STAGES = [
  "awareness",
  "consideration",
  "purchase",
  "onboarding",
  "usage",
  "retention",
  "advocacy",
];

const state = {
  stages: STAGES.map((name) => ({
    name,
    customer_goal: "",
    customer_actions: [],
    thoughts: [],
    emotions: [],
    pain_points: [],
    opportunities: [],
    touchpoints: [],
  })),
};

const stageContainer = document.querySelector("#stage-container");
const analyzeButton = document.querySelector("#analyze-button");
const analysisOutput = document.querySelector("#analysis-output");

function titleCase(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function createStageCard(stage, index) {
  const card = document.createElement("section");
  card.className = "stage-card";

  card.innerHTML = `
    <div class="stage-header">
      <span class="stage-number">${index + 1}</span>
      <h2>${titleCase(stage.name)}</h2>
    </div>

    <label>
      Customer goal
      <input data-field="customer_goal" value="${stage.customer_goal}" />
    </label>

    <label>
      Customer actions
      <textarea data-field="customer_actions"
        placeholder="One action per line"></textarea>
    </label>

    <label>
      Thoughts
      <textarea data-field="thoughts"
        placeholder="One thought per line"></textarea>
    </label>

    <label>
      Emotions
      <textarea data-field="emotions"
        placeholder="One emotion per line"></textarea>
    </label>

    <label>
      Pain points
      <textarea data-field="pain_points"
        placeholder="One pain point per line"></textarea>
    </label>

    <label>
      Opportunities
      <textarea data-field="opportunities"
        placeholder="One opportunity per line"></textarea>
    </label>

    <div class="touchpoint">
      <h3>Primary touchpoint</h3>
      <input data-touchpoint="channel" placeholder="Channel, e.g. Search" />
      <input data-touchpoint="description" placeholder="What happens?" />

      <div class="metrics">
        <label>
          Sentiment
          <input data-touchpoint="sentiment" type="number" min="-5" max="5" value="0" />
        </label>
        <label>
          Effort
          <input data-touchpoint="effort" type="number" min="1" max="5" value="3" />
        </label>
        <label>
          Frequency
          <input data-touchpoint="frequency" type="number" min="1" max="5" value="1" />
        </label>
      </div>
    </div>
  `;

  card.querySelectorAll("[data-field]").forEach((element) => {
    element.addEventListener("input", () => {
      const field = element.dataset.field;
      state.stages[index][field] =
        element.tagName === "TEXTAREA"
          ? element.value.split("\n").map((item) => item.trim()).filter(Boolean)
          : element.value;
    });
  });

  card.querySelectorAll("[data-touchpoint]").forEach((element) => {
    element.addEventListener("input", () => {
      const field = element.dataset.touchpoint;

      if (!state.stages[index].touchpoints[0]) {
        state.stages[index].touchpoints.push({
          channel: "",
          description: "",
          sentiment: 0,
          effort: 3,
          frequency: 1,
        });
      }

      state.stages[index].touchpoints[0][field] =
        field === "channel" || field === "description"
          ? element.value
          : Number(element.value);
    });
  });

  return card;
}

function renderStages() {
  stageContainer.replaceChildren(
    ...state.stages.map((stage, index) => createStageCard(stage, index)),
  );
}

function buildJourney() {
  return {
    persona: document.querySelector("#persona").value.trim(),
    scenario: document.querySelector("#scenario").value.trim(),
    stages: state.stages,
  };
}

function renderAnalysis(result) {
  analysisOutput.innerHTML = `
    <div class="metric">
      <strong>${result.average_sentiment}</strong>
      <span>Average sentiment</span>
    </div>
    <div class="metric">
      <strong>${result.average_effort}</strong>
      <span>Average effort</span>
    </div>
    <div class="metric">
      <strong>${result.total_touchpoints}</strong>
      <span>Touchpoints</span>
    </div>
    <div class="metric">
      <strong>${result.pain_point_count}</strong>
      <span>Pain points</span>
    </div>
    <div class="metric">
      <strong>${result.opportunity_count}</strong>
      <span>Opportunities</span>
    </div>
    <p><b>Strongest sentiment stage:</b> ${titleCase(result.strongest_stage || "None")}</p>
    <p><b>Weakest sentiment stage:</b> ${titleCase(result.weakest_stage || "None")}</p>
  `;
}

async function analyzeJourney() {
  analysisOutput.textContent = "Analyzing journey...";

  try {
    const response = await fetch("/api/journeys/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildJourney()),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Journey analysis failed.");
    }

    renderAnalysis(await response.json());
  } catch (error) {
    analysisOutput.textContent = error.message;
  }
}

analyzeButton.addEventListener("click", analyzeJourney);
renderStages();

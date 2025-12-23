import { API_URL } from "../config/api.js";
import { renderCityStatus } from "../components/CityStatus.js";
import { renderExplanation } from "../components/Explanation.js";
import { renderPrediction } from "../components/Prediction.js";

document.addEventListener("DOMContentLoaded", () => {
    // UI Elements
    const systemStatus = document.getElementById("system-status");
    const revealBtn = document.getElementById("reveal-future-btn");
    const futureSection = document.getElementById("future-section");

    // Fetch Data
    async function fetchData() {
        try {
            if (systemStatus) systemStatus.textContent = "Connecting...";

            const response = await fetch(API_URL);

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const data = await response.json();
            updateUI(data);
            if (systemStatus) systemStatus.textContent = "Online";
        } catch (error) {
            console.error("Error fetching data:", error);
            if (systemStatus) systemStatus.textContent = "Error";
            renderCityStatus("Connection Failed");
        }
    }

    function updateUI(data) {
        renderCityStatus(data.status);
        renderExplanation(data.summary, data.details);
        renderPrediction(data.future);
    }

    // Interactivity
    if (revealBtn && futureSection) {
        revealBtn.addEventListener("click", () => {
            futureSection.classList.remove("hidden");
            revealBtn.style.display = "none";
        });
    }

    // Start
    fetchData();
});

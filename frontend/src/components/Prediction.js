// Component: Prediction - Handles the future risk reveal
export function renderPrediction(prediction) {
    const futureText = document.getElementById("future-text");
    if (futureText) futureText.textContent = prediction;
}

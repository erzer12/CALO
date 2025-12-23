// Component: Explanation - Shows why CALO made this decision
export function renderExplanation(summary, details) {
    const summaryEl = document.getElementById("summary-text");
    const detailsList = document.getElementById("details-list");

    if (summaryEl) summaryEl.textContent = summary;

    if (detailsList) {
        detailsList.innerHTML = "";
        details.forEach(detail => {
            const li = document.createElement("li");
            li.textContent = detail;
            detailsList.appendChild(li);
        });
    }
}

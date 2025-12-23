// Component: City Status - Displays global health of the city
export function renderCityStatus(status) {
    const el = document.getElementById("status-indicator");
    if (el) el.textContent = status;
}

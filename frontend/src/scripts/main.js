import { API_URL } from '../config/api.js';

/**
 * CALO Logic v2.1
 * Supports Dual-View: Citizen (Calm) vs Engineer (Rigorous)
 */

class CALOApp {
    constructor() {
        this.data = null;
        this.mode = 'citizen'; // 'citizen' | 'engineer'

        // Bind methods
        this.init = this.init.bind(this);
        this.toggleMode = this.toggleMode.bind(this);
    }

    async init() {
        console.log('CALO v2.1 Initializing...');
        await this.fetchData();
        this.updateUI();

        // Connection Status Indicator
        const statusDot = document.getElementById('connection-status');
        if (statusDot) {
            if (this.data && !this.data.ui_mode_engineer?.error) {
                statusDot.classList.replace('bg-slate-300', 'bg-emerald-400');
                statusDot.title = "System Online";
            } else {
                statusDot.classList.replace('bg-slate-300', 'bg-red-500');
                statusDot.title = "Connection Failed";
            }
        }
    }

    async fetchData() {
        try {
            console.log(`Connecting to Logic Engine at ${API_URL}...`);
            const response = await fetch(API_URL);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.data = await response.json();
            console.log('Logic Engine Response:', this.data);
        } catch (error) {
            console.error('Failed to load data:', error);
            // Fallback for offline testing
            this.data = {
                citizen_view: {
                    status_headline: "Unable to reach City Brain.",
                    visual_theme: "Caution"
                },
                engineer_view: {
                    confidence_score: "0.00",
                    detected_risks: ["Network Failure"],
                    logic_trace: "Error: " + error.message,
                    recommended_actions: ["Check Backend Connection", "Verify API URL"]
                }
            };
        }
    }

    updateUI() {
        if (!this.data) return;

        // 1. Citizen View Bindings
        const cView = this.data.citizen_view || {};
        const summary = document.getElementById('summary-text');
        const badge = document.getElementById('status-badge');

        if (summary) summary.textContent = cView.status_headline || "System Standby";

        if (badge) {
            const theme = (cView.visual_theme || 'Normal').toLowerCase();
            badge.textContent = theme.toUpperCase();

            // Reset classes
            badge.className = "inline-flex items-center px-6 py-2 rounded-full font-semibold text-lg transition-all duration-500";

            if (theme === 'critical' || theme === 'caution') {
                badge.classList.add('bg-red-100', 'text-red-700');
            } else if (theme === 'warning') {
                badge.classList.add('bg-amber-100', 'text-amber-800');
            } else {
                badge.classList.add('bg-emerald-100', 'text-emerald-800');
            }
        }

        // 2. Engineer View Bindings
        const eView = this.data.engineer_view || {};

        document.getElementById('eng-confidence').textContent = (eView.confidence_score || 0) + "%";

        const risks = eView.detected_risks || [];
        document.getElementById('eng-risk-count').textContent = risks.length;

        // Signal Matrix
        const signals = eView.raw_signals || { weather: 0, complaints: 0, trends: 0 };
        document.getElementById('sig-weather').style.width = (signals.weather * 100) + '%';
        document.getElementById('sig-complaints').style.width = (signals.complaints * 100) + '%';
        document.getElementById('sig-trends').style.width = (signals.trends * 100) + '%';

        // Logic Trace with Typing Effect (Simple)
        const traceBox = document.getElementById('eng-logic-trace');
        if (traceBox) {
            // Only type if text changed
            const newText = eView.logic_trace || "No logic trace available.";
            if (traceBox.textContent !== newText) {
                traceBox.textContent = newText;
                // Note: For a true typing effect, we'd need a recursive timeout,
                // but direct textContent is safer for rapid updates.
            }
        }

        const actionsList = document.getElementById('eng-actions');
        if (actionsList) {
            actionsList.innerHTML = '';
            (eView.recommended_actions || []).forEach(action => {
                const li = document.createElement('li');
                li.className = "flex items-start gap-3 text-slate-700 p-2 bg-slate-50 rounded border border-slate-100";
                li.innerHTML = `
                    <div class="mt-1 w-1.5 h-1.5 rounded-full bg-blue-500 flex-shrink-0"></div>
                    <span class="text-xs font-medium">${action}</span>
                `;
                actionsList.appendChild(li);
            });
        }
    }

    toggleMode() {
        const homeView = document.getElementById('view-home');
        const engView = document.getElementById('view-engineer');
        const btn = document.getElementById('mode-toggle');

        if (this.mode === 'citizen') {
            // Switch to Engineer
            this.mode = 'engineer';
            homeView.classList.add('hidden', 'opacity-0');
            engView.classList.remove('hidden');
            setTimeout(() => engView.classList.remove('opacity-0'), 50);

            btn.textContent = "Exit Engineer Mode";
            btn.classList.add('bg-slate-800', 'text-white');
            document.body.classList.add('bg-slate-200'); // Darker bg for context switch
        } else {
            // Switch to Citizen
            this.mode = 'citizen';
            engView.classList.add('hidden', 'opacity-0');
            homeView.classList.remove('hidden');
            setTimeout(() => homeView.classList.remove('opacity-0'), 50);

            btn.textContent = "Engineer Mode";
            btn.classList.remove('bg-slate-800', 'text-white');
            document.body.classList.remove('bg-slate-200');
        }
    }
}

// Initialize
const app = new CALOApp();
window.app = app;
document.addEventListener('DOMContentLoaded', app.init);

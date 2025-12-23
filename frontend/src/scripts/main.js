import { API_URL } from '../config/api.js';

/**
 * CALO Logic - Professional Redesign
 * Handles view navigation and data binding.
 */

class CALOApp {
    constructor() {
        this.data = null;
        this.views = ['home', 'explain', 'predict'];
        this.currentView = 'home';

        // Bind methods
        this.init = this.init.bind(this);
        this.navigateTo = this.navigateTo.bind(this);
        this.revealFuture = this.revealFuture.bind(this);
    }

    async init() {
        console.log('CALO System Initializing...');
        await this.fetchData();
        this.bindEvents();
        this.updateUI();

        // Simulate connection status
        setTimeout(() => {
            const statusDot = document.getElementById('connection-status');
            if (statusDot) {
                // If data fetch was successful (we have a valid status), show green
                if (this.data && !this.data.status.includes('Error')) {
                    statusDot.classList.replace('bg-slate-300', 'bg-emerald-400');
                    statusDot.title = "System Online";
                } else {
                    statusDot.classList.replace('bg-slate-300', 'bg-red-500');
                    statusDot.title = "Connection Failed";
                }
            }
        }, 1000);
    }

    async fetchData() {
        try {
            console.log(`Connecting to CALO Brain at ${API_URL}...`);
            const response = await fetch(API_URL);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.data = await response.json();
            console.log('Data loaded:', this.data);
        } catch (error) {
            console.error('Failed to load data:', error);
            // Fallback data
            this.data = {
                status: "Connection Error",
                summary: "Could not reach the City Intelligence Network.",
                details: ["Backend might be offline", "Check API URL configuration: " + API_URL],
                future: "Please try again later."
            };
        }
    }

    bindEvents() {
        const revealBtn = document.getElementById('reveal-btn');
        if (revealBtn) {
            revealBtn.addEventListener('click', this.revealFuture);
        }
    }

    updateUI() {
        if (!this.data) return;

        // 1. Home View Updates
        const badge = document.getElementById('status-badge');
        const summary = document.getElementById('summary-text');

        if (badge) {
            badge.textContent = this.data.status;
            // Apply color classes based on status
            const statusLower = this.data.status.toLowerCase();
            badge.className = "inline-flex items-center px-6 py-2 rounded-full font-semibold text-lg transition-all duration-500 ";

            if (statusLower.includes('stress') || statusLower.includes('high') || statusLower.includes('error')) {
                badge.classList.add('bg-red-100', 'text-red-700');
            } else if (statusLower.includes('watch') || statusLower.includes('warning')) {
                badge.classList.add('bg-amber-100', 'text-amber-800');
            } else {
                badge.classList.add('bg-emerald-100', 'text-emerald-800');
            }
        }

        if (summary) summary.textContent = this.data.summary;

        // 2. Explain View Updates
        const listContainer = document.getElementById('details-list');
        if (listContainer && this.data.details) {
            listContainer.innerHTML = ''; // Clear skeleton
            // Handle if details is a string (rare error case) or array
            const detailsArray = Array.isArray(this.data.details) ? this.data.details : [this.data.details];

            detailsArray.forEach(item => {
                const li = document.createElement('li');
                li.className = "flex items-start gap-3";
                li.innerHTML = `
                    <span class="mt-1.5 w-1.5 h-1.5 rounded-full bg-slate-400 flex-shrink-0"></span>
                    <span>${item}</span>
                `;
                listContainer.appendChild(li);
            });
        }

        // 3. Predict View Updates
        const futureText = document.getElementById('future-blur');
        if (futureText) futureText.textContent = this.data.future;
    }

    navigateTo(viewId) {
        if (!this.views.includes(viewId)) return;

        // Hide all views
        this.views.forEach(v => {
            const el = document.getElementById(`view-${v}`);
            if (el) {
                el.classList.add('hidden', 'opacity-0');
                el.classList.remove('flex', 'opacity-100');
            }
        });

        // Show target view
        const target = document.getElementById(`view-${viewId}`);
        if (target) {
            target.classList.remove('hidden');
            // Small delay to allow display:block to apply before opacity transition
            setTimeout(() => {
                target.classList.remove('opacity-0');
            }, 50);
        }

        this.currentView = viewId;
        window.scrollTo(0, 0);
    }

    revealFuture() {
        const blurEl = document.getElementById('future-blur');
        const btn = document.getElementById('reveal-btn');

        if (blurEl) {
            blurEl.classList.remove('blur-md', 'select-none');
        }

        if (btn) {
            btn.textContent = "Analysis Revealed";
            btn.disabled = true;
            btn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }
}

// Initialize and attach to window for HTML access
const app = new CALOApp();
window.app = app;

document.addEventListener('DOMContentLoaded', app.init);

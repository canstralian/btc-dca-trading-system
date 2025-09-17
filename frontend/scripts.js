// DCAlytics Frontend JavaScript

class DCAlyticsDashboard {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.portfolioChart = null;
        this.btcPriceChart = null;
        this.currentSimulation = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeDateInputs();
        this.loadCurrentBTCPrice();
        this.initializeCharts();
    }

    setupEventListeners() {
        // Strategy form submission
        document.getElementById('strategy-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.runSimulation();
        });

        // Hedge percentage slider
        const hedgeSlider = document.getElementById('hedge-percentage');
        const hedgeDisplay = document.getElementById('hedge-percentage-display');
        
        hedgeSlider.addEventListener('input', (e) => {
            hedgeDisplay.textContent = `${e.target.value}%`;
        });

        // Real-time updates
        setInterval(() => {
            this.loadCurrentBTCPrice();
        }, 30000); // Update every 30 seconds
    }

    initializeDateInputs() {
        const startDateInput = document.getElementById('start-date');
        const endDateInput = document.getElementById('end-date');
        
        // Set default dates (1 year ago to today)
        const today = new Date();
        const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());
        
        startDateInput.value = oneYearAgo.toISOString().split('T')[0];
        endDateInput.value = today.toISOString().split('T')[0];
    }

    async loadCurrentBTCPrice() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/btc-price/current`);
            const data = await response.json();
            
            const priceElement = document.getElementById('current-btc-price');
            priceElement.innerHTML = `
                <i class="fas fa-bitcoin text-orange-500"></i>
                $${this.formatNumber(data.price)}
            `;
        } catch (error) {
            console.error('Failed to load BTC price:', error);
            document.getElementById('current-btc-price').textContent = 'Price unavailable';
        }
    }

    async runSimulation() {
        const loadingOverlay = document.getElementById('loading-overlay');
        const runButton = document.getElementById('run-simulation');
        
        try {
            // Show loading state
            loadingOverlay.classList.remove('hidden');
            runButton.disabled = true;
            runButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Running...';

            // Get form data
            const formData = this.getFormData();
            
            // Validate data
            if (!this.validateFormData(formData)) {
                throw new Error('Please fill in all required fields correctly');
            }

            // Run simulation
            const response = await fetch(`${this.apiBaseUrl}/api/simulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    strategy: formData,
                    use_historical_data: true
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Simulation failed');
            }

            const result = await response.json();
            this.currentSimulation = result;
            
            // Update UI with results
            this.updateMetrics(result);
            this.updateCharts(result);
            
        } catch (error) {
            console.error('Simulation error:', error);
            this.showError(error.message);
        } finally {
            // Hide loading state
            loadingOverlay.classList.add('hidden');
            runButton.disabled = false;
            runButton.innerHTML = '<i class="fas fa-play mr-2"></i>Run Simulation';
        }
    }

    getFormData() {
        return {
            investment_amount: parseFloat(document.getElementById('investment-amount').value),
            frequency_days: parseInt(document.getElementById('frequency-days').value),
            hedge_percentage: parseFloat(document.getElementById('hedge-percentage').value),
            start_date: new Date(document.getElementById('start-date').value).toISOString(),
            end_date: new Date(document.getElementById('end-date').value).toISOString()
        };
    }

    validateFormData(data) {
        if (!data.investment_amount || data.investment_amount <= 0) return false;
        if (!data.frequency_days || data.frequency_days <= 0) return false;
        if (data.hedge_percentage < 0 || data.hedge_percentage > 100) return false;
        if (!data.start_date || !data.end_date) return false;
        if (new Date(data.start_date) >= new Date(data.end_date)) return false;
        
        return true;
    }

    updateMetrics(result) {
        // Update performance metrics
        document.getElementById('total-return').textContent = `${this.formatPercentage(result.total_return)}%`;
        document.getElementById('annualized-return').textContent = `${this.formatPercentage(result.annualized_return)}%`;
        document.getElementById('max-drawdown').textContent = `${this.formatPercentage(result.max_drawdown)}%`;
        document.getElementById('sharpe-ratio').textContent = this.formatNumber(result.sharpe_ratio, 2);

        // Update portfolio summary
        const finalPortfolio = result.final_portfolio;
        document.getElementById('total-invested').textContent = `$${this.formatNumber(finalPortfolio.total_invested)}`;
        document.getElementById('btc-holdings').textContent = `${this.formatNumber(finalPortfolio.btc_holdings, 6)} BTC`;
        document.getElementById('portfolio-value').textContent = `$${this.formatNumber(finalPortfolio.total_value)}`;

        // Apply color coding
        this.applyColorCoding('total-return', result.total_return);
        this.applyColorCoding('annualized-return', result.annualized_return);
    }

    updateCharts(result) {
        this.updatePortfolioChart(result);
        this.updateBTCPriceChart(result);
    }

    updatePortfolioChart(result) {
        const ctx = document.getElementById('portfolio-chart').getContext('2d');
        
        if (this.portfolioChart) {
            this.portfolioChart.destroy();
        }

        const portfolioData = result.portfolio_history.map(snapshot => ({
            x: new Date(snapshot.timestamp),
            y: snapshot.total_value
        }));

        const investedData = result.portfolio_history.map(snapshot => ({
            x: new Date(snapshot.timestamp),
            y: snapshot.total_invested
        }));

        this.portfolioChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: 'Portfolio Value',
                        data: portfolioData,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Total Invested',
                        data: investedData,
                        borderColor: '#6b7280',
                        backgroundColor: 'transparent',
                        borderDash: [5, 5],
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#e5e7eb'
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month'
                        },
                        ticks: {
                            color: '#9ca3af'
                        },
                        grid: {
                            color: '#374151'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#9ca3af',
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        },
                        grid: {
                            color: '#374151'
                        }
                    }
                }
            }
        });
    }

    async updateBTCPriceChart(result) {
        try {
            const startDate = new Date(result.strategy.start_date);
            const endDate = new Date(result.strategy.end_date);
            
            const response = await fetch(
                `${this.apiBaseUrl}/api/btc-price?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}&limit=1000`
            );
            const priceData = await response.json();

            const ctx = document.getElementById('btc-price-chart').getContext('2d');
            
            if (this.btcPriceChart) {
                this.btcPriceChart.destroy();
            }

            const chartData = priceData.map(point => ({
                x: new Date(point.timestamp),
                y: point.price
            }));

            this.btcPriceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'BTC Price (USD)',
                        data: chartData,
                        borderColor: '#f97316',
                        backgroundColor: 'rgba(249, 115, 22, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#e5e7eb'
                            }
                        }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'month'
                            },
                            ticks: {
                                color: '#9ca3af'
                            },
                            grid: {
                                color: '#374151'
                            }
                        },
                        y: {
                            ticks: {
                                color: '#9ca3af',
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            },
                            grid: {
                                color: '#374151'
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Failed to update BTC price chart:', error);
        }
    }

    initializeCharts() {
        // Initialize empty charts
        const portfolioCtx = document.getElementById('portfolio-chart').getContext('2d');
        const btcCtx = document.getElementById('btc-price-chart').getContext('2d');

        this.portfolioChart = new Chart(portfolioCtx, {
            type: 'line',
            data: { datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });

        this.btcPriceChart = new Chart(btcCtx, {
            type: 'line',
            data: { datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    }

    applyColorCoding(elementId, value) {
        const element = document.getElementById(elementId);
        element.classList.remove('text-green-400', 'text-red-400', 'text-gray-400');
        
        if (value > 0) {
            element.classList.add('text-green-400');
        } else if (value < 0) {
            element.classList.add('text-red-400');
        } else {
            element.classList.add('text-gray-400');
        }
    }

    formatNumber(number, decimals = 0) {
        if (number === null || number === undefined) return '-';
        return number.toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    formatPercentage(number, decimals = 2) {
        if (number === null || number === undefined) return '-';
        return number.toFixed(decimals);
    }

    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-4 rounded-lg shadow-lg z-50';
        errorDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-triangle mr-3"></i>
                <span>${message}</span>
                <button class="ml-4 text-red-200 hover:text-white" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DCAlyticsDashboard();
});

// Export for testing purposes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DCAlyticsDashboard;
}
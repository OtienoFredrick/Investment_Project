document.addEventListener('DOMContentLoaded', () => {
    loadInvestmentData();

    async function loadInvestmentData() {
        const apiKey = '0H6O9AQCHH77Y2PX'; // Replace with your actual API key
        const symbols = ['AAPL', 'GOOGL', 'MSFT']; // Replace with your desired stock symbols
        const tableBody = document.getElementById('investment-table-body');

        // Clear existing rows
        tableBody.innerHTML = '';

        for (const symbol of symbols) {
            const url = `https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=${symbol}&interval=5min&apikey=${apiKey}`;

            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                // Check for API rate limit or invalid response
                if (data['Note']) {
                    throw new Error('API rate limit exceeded. Please try again later.');
                }
                if (!data['Time Series (5min)']) {
                    throw new Error(`No valid data available for the selected stock symbol: ${symbol}`);
                }

                const timeSeries = data['Time Series (5min)'];
                const latestTime = Object.keys(timeSeries)[0];
                const priceData = timeSeries[latestTime];
                const changePercentage = calculateChangePercentage(priceData);

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${symbol}</td>
                    <td>100</td> <!-- Example quantity -->
                    <td>$${parseFloat(priceData['1. open']).toFixed(2)}</td>
                    <td>$${parseFloat(priceData['4. close']).toFixed(2)}</td>
                    <td class="${changePercentage >= 0 ? 'positive' : 'negative'}">
                        ${changePercentage.toFixed(2)}%
                    </td>
                    <td>$${(100 * parseFloat(priceData['4. close'])).toFixed(2)}</td>
                `;
                tableBody.appendChild(row);
            } catch (error) {
                console.error(`Error loading data for ${symbol}:`, error);

                // Display error message in the table
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td colspan="6">Error loading data for ${symbol}: ${error.message}</td>
                `;
                tableBody.appendChild(row);
            }
        }
    }

    function calculateChangePercentage(priceData) {
        const openPrice = parseFloat(priceData['1. open']);
        const closePrice = parseFloat(priceData['4. close']);
        return ((closePrice - openPrice) / openPrice) * 100;
    }
});

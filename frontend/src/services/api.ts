const API_BASE_URL = 'http://127.0.0.1:8000';

export const getStockPrediction = async (symbol: string) => {
    const response = await fetch(`${API_BASE_URL}/plaid/ml/predict/${symbol}`);
    if (!response.ok) throw new Error('Failed to fetch prediction');
    return response.json();
};

export const getStockSentiment = async (symbol: string) => {
    const response = await fetch(`${API_BASE_URL}/plaid/ml/sentiment/${symbol}`);
    if (!response.ok) throw new Error('Failed to fetch sentiment');
    return response.json();
};

export const getPortfolioInsights = async () => {
    const response = await fetch(`${API_BASE_URL}/plaid/ml/portfolio-insights`);
    if (!response.ok) throw new Error('Failed to fetch portfolio insights');
    return response.json();
};
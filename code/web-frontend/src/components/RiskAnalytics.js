import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

export default function RiskAnalytics() {
  const [riskData, setRiskData] = useState([]);

  useEffect(() => {
    fetch('/api/risk-metrics')
      .then(res => res.json())
      .then(data => setRiskData([
        { metric: 'VaR (95%)', value: data.var },
        { metric: 'Sharpe Ratio', value: data.sharpe },
        { metric: 'Volatility', value: data.volatility }
      ]));
  }, []);

  return (
    <BarChart width={500} height={300} data={riskData}>
      <XAxis dataKey="metric" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="value" fill="#8884d8" />
    </BarChart>
  );
}

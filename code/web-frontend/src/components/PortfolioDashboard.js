import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip } from 'recharts';

export default function PortfolioDashboard() {
  const [portfolio, setPortfolio] = useState([]);
  const [address] = useState('0xUserAddress'); // Replace with wallet integration

  useEffect(() => {
    fetch(`/api/portfolio/${address}`)
      .then(res => res.json())
      .then(data => {
        const formatted = data.assets.map((asset, i) => ({
          name: asset,
          value: data.allocations[i]
        }));
        setPortfolio(formatted);
      });
  }, [address]);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <PieChart width={400} height={400}>
      <Pie
        data={portfolio}
        cx={200}
        cy={200}
        innerRadius={60}
        outerRadius={80}
        paddingAngle={5}
        dataKey="value"
      >
        {portfolio.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
        ))}
      </Pie>
      <Tooltip />
    </PieChart>
  );
}

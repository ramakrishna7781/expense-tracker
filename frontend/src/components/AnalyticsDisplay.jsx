import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './AnalyticsDisplay.css';

// Colors for the pie chart slices
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF', '#FF1943'];

const AnalyticsDisplay = ({ analyticsData }) => {
  // The backend sends {_id: "Category", total: 123}, recharts needs {name: "Category", value: 123}
  const chartData = analyticsData.map(item => ({
    name: item._id,
    value: item.total
  }));

  return (
    <div className="analytics-container">
      <h4>Spending Analytics</h4>
      
      <div className="analytics-content">
        {/* Table View */}
        <div className="analytics-table-wrapper">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Total Spent</th>
              </tr>
            </thead>
            <tbody>
              {chartData.map((item) => (
                <tr key={item.name}>
                  <td>{item.name}</td>
                  <td>Rs.{item.value.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pie Chart View */}
        <div className="analytics-chart-wrapper">
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                nameKey="name"
                label={(entry) => entry.name}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `Rs.${value.toFixed(2)}`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDisplay;
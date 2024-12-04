import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';

// Color palette for visualizations
const COLORS = [
  '#0088FE', '#00C49F', '#FFBB28',
  '#FF8042', '#8884D8', '#82CA9D'
];

interface DataVisualizationProps {
  data: (string | number)[][] | undefined;
  labels?: string[];
}

const DataVisualization: React.FC<DataVisualizationProps> = ({ data }) => {
  const [chartType, setChartType] = useState<'bar' | 'pie' | 'line'>('bar');

  // If no data or data is empty, return null
  if (!data || data.length === 0) return null;

  // Transform data into recharts-compatible format
  const transformedData = data.map(([name, value]) => ({
    name,
    value
  }));

  // Render chart based on selected type
  const renderChart = () => {
    const width = 500;
    const height = 300;

    switch (chartType) {
      case 'bar':
        return (
          <BarChart width={width} height={height} data={transformedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill={COLORS[0]} />
          </BarChart>
        );

      case 'pie':
        return (
          <PieChart width={width} height={height}>
            <Pie
              data={transformedData}
              cx={width / 2}
              cy={height / 2}
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {transformedData.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        );

      case 'line':
        return (
          <LineChart width={width} height={height} data={transformedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="value" stroke={COLORS[0]} />
          </LineChart>
        );
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-md">
      <div className="flex justify-center mb-4">
        <div className="inline-flex rounded-md shadow-sm" role="group">
          {['bar', 'pie', 'line'].map(type => (
            <button
              key={type}
              type="button"
              onClick={() => setChartType(type as any)}
              className={`px-4 py-2 text-sm font-medium text-gray-900 border border-gray-200 hover:bg-gray-100 
              ${chartType === type ? 'bg-green-100' : 'bg-white'}`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)} Chart
            </button>
          ))}
        </div>
      </div>
      <div className="flex justify-center">
        {renderChart()}
      </div>
    </div>
  );
};

export default DataVisualization;

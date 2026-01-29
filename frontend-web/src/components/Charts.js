// frontend-web/src/components/Charts.js
/**
 * Charts Component
 * 
 * Displays interactive charts using Chart.js:
 * - Bar chart for averages by type
 * - Pie chart for type distribution
 * - Line chart for parameter trends
 */

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function Charts({ dataset }) {
  if (!dataset || !dataset.summary_parsed) {
    return <div>No data available for charts</div>;
  }

  const summary = dataset.summary_parsed;
  const rawData = dataset.raw_data_parsed;

  // Color palette for charts
  const colors = [
    '#3498db', '#e74c3c', '#2ecc71', '#f39c12', 
    '#9b59b6', '#1abc9c', '#34495e', '#e67e22'
  ];

  // =========== Bar Chart Data (Parameter Averages) ===========
  const barChartData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [
      {
        label: 'Average Values',
        data: [
          summary.averages.flowrate,
          summary.averages.pressure,
          summary.averages.temperature
        ],
        backgroundColor: ['#3498db', '#e74c3c', '#f39c12'],
        borderColor: ['#2980b9', '#c0392b', '#d68910'],
        borderWidth: 2,
        borderRadius: 8,
      }
    ]
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: 'Average Parameter Values',
        font: { size: 16 }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: '#ecf0f1' }
      }
    }
  };

  // =========== Pie Chart Data (Type Distribution) ===========
  const typeLabels = Object.keys(summary.type_distribution);
  const typeCounts = Object.values(summary.type_distribution);

  const pieChartData = {
    labels: typeLabels,
    datasets: [
      {
        data: typeCounts,
        backgroundColor: colors.slice(0, typeLabels.length),
        borderColor: '#fff',
        borderWidth: 3,
      }
    ]
  };

  const pieChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
        labels: { padding: 20 }
      },
      title: {
        display: true,
        text: 'Equipment Type Distribution',
        font: { size: 16 }
      }
    }
  };

  // =========== Line Chart Data (Parameter Trends) ===========
  const lineChartData = {
    labels: rawData.map(item => item['Equipment Name']),
    datasets: [
      {
        label: 'Flowrate',
        data: rawData.map(item => item.Flowrate),
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Pressure',
        data: rawData.map(item => item.Pressure),
        borderColor: '#e74c3c',
        backgroundColor: 'rgba(231, 76, 60, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Temperature',
        data: rawData.map(item => item.Temperature),
        borderColor: '#f39c12',
        backgroundColor: 'rgba(243, 156, 18, 0.1)',
        tension: 0.4,
        fill: true,
      }
    ]
  };

  const lineChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: {
        display: true,
        text: 'Parameter Trends Across Equipment',
        font: { size: 16 }
      }
    },
    scales: {
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45
        }
      },
      y: {
        beginAtZero: true,
        grid: { color: '#ecf0f1' }
      }
    }
  };

  // =========== Grouped Bar Chart (Min/Max/Avg) ===========
  const comparisonData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [
      {
        label: 'Minimum',
        data: [
          summary.minimums.flowrate,
          summary.minimums.pressure,
          summary.minimums.temperature
        ],
        backgroundColor: '#3498db',
      },
      {
        label: 'Average',
        data: [
          summary.averages.flowrate,
          summary.averages.pressure,
          summary.averages.temperature
        ],
        backgroundColor: '#2ecc71',
      },
      {
        label: 'Maximum',
        data: [
          summary.maximums.flowrate,
          summary.maximums.pressure,
          summary.maximums.temperature
        ],
        backgroundColor: '#e74c3c',
      }
    ]
  };

  const comparisonOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: {
        display: true,
        text: 'Parameter Comparison (Min/Avg/Max)',
        font: { size: 16 }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: '#ecf0f1' }
      }
    }
  };

  return (
    <div className="charts-container">
      <h2>📈 Data Visualization</h2>
      
      <div className="charts-grid">
        {/* Pie Chart - Type Distribution */}
        <div className="chart-card">
          <Pie data={pieChartData} options={pieChartOptions} />
        </div>
        
        {/* Bar Chart - Averages */}
        <div className="chart-card">
          <Bar data={barChartData} options={barChartOptions} />
        </div>
        
        {/* Line Chart - Trends */}
        <div className="chart-card" style={{ gridColumn: '1 / -1' }}>
          <Line data={lineChartData} options={lineChartOptions} />
        </div>
        
        {/* Grouped Bar Chart - Comparison */}
        <div className="chart-card" style={{ gridColumn: '1 / -1' }}>
          <Bar data={comparisonData} options={comparisonOptions} />
        </div>
      </div>
    </div>
  );
}

export default Charts;
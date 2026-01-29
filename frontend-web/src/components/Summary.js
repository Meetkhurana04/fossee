// frontend-web/src/components/Summary.js
/**
 * Summary Component
 * 
 * Displays key statistics and metrics from the dataset:
 * - Total count of equipment
 * - Average values for each parameter
 * - Min/Max ranges
 * - Type distribution
 */

import React from 'react';

function Summary({ dataset }) {
  if (!dataset || !dataset.summary_parsed) {
    return <div>No summary available</div>;
  }

  const summary = dataset.summary_parsed;

  return (
    <div className="summary-container">
      <h2>📊 Dataset Summary: {dataset.name}</h2>
      
      {/* Main Statistics Cards */}
      <div className="summary-grid">
        <div className="summary-card">
          <h3>Total Equipment</h3>
          <div className="value">{summary.total_count}</div>
        </div>
        
        <div className="summary-card green">
          <h3>Avg Flowrate</h3>
          <div className="value">{summary.averages.flowrate}</div>
        </div>
        
        <div className="summary-card orange">
          <h3>Avg Pressure</h3>
          <div className="value">{summary.averages.pressure}</div>
        </div>
        
        <div className="summary-card purple">
          <h3>Avg Temperature</h3>
          <div className="value">{summary.averages.temperature}°</div>
        </div>
      </div>

      {/* Statistics Table */}
      <div style={{ marginTop: '2rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>📈 Parameter Statistics</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>Parameter</th>
              <th>Minimum</th>
              <th>Average</th>
              <th>Maximum</th>
              <th>Std Deviation</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Flowrate</strong></td>
              <td>{summary.minimums.flowrate}</td>
              <td>{summary.averages.flowrate}</td>
              <td>{summary.maximums.flowrate}</td>
              <td>{summary.std_deviations.flowrate}</td>
            </tr>
            <tr>
              <td><strong>Pressure</strong></td>
              <td>{summary.minimums.pressure}</td>
              <td>{summary.averages.pressure}</td>
              <td>{summary.maximums.pressure}</td>
              <td>{summary.std_deviations.pressure}</td>
            </tr>
            <tr>
              <td><strong>Temperature</strong></td>
              <td>{summary.minimums.temperature}°</td>
              <td>{summary.averages.temperature}°</td>
              <td>{summary.maximums.temperature}°</td>
              <td>{summary.std_deviations.temperature}°</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Type Distribution */}
      <div className="type-distribution">
        <h3>🏭 Equipment Type Distribution</h3>
        <div className="type-list">
          {Object.entries(summary.type_distribution).map(([type, count]) => (
            <div key={type} className="type-item">
              <span>{type}</span>
              <span className="count">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Summary;
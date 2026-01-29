// frontend-web/src/components/DataTable.js
/**
 * DataTable Component
 * 
 * Displays equipment data in a sortable, searchable table.
 * Supports column sorting and text filtering.
 */

import React, { useState, useMemo } from 'react';

function DataTable({ data }) {
  // Search/filter state
  const [searchTerm, setSearchTerm] = useState('');
  
  // Sorting state
  const [sortConfig, setSortConfig] = useState({
    key: null,
    direction: 'asc'
  });

  /**
   * Filter and sort data based on current state
   */
  const processedData = useMemo(() => {
    if (!data) return [];
    
    let filtered = [...data];
    
    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(item =>
        item['Equipment Name'].toLowerCase().includes(term) ||
        item['Type'].toLowerCase().includes(term)
      );
    }
    
    // Apply sorting
    if (sortConfig.key) {
      filtered.sort((a, b) => {
        let aVal = a[sortConfig.key];
        let bVal = b[sortConfig.key];
        
        // Handle numeric sorting
        if (typeof aVal === 'number') {
          return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
        }
        
        // Handle string sorting
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();
        
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    
    return filtered;
  }, [data, searchTerm, sortConfig]);

  /**
   * Handle column header click for sorting
   */
  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  /**
   * Get sort indicator for column header
   */
  const getSortIndicator = (key) => {
    if (sortConfig.key !== key) return '↕️';
    return sortConfig.direction === 'asc' ? '⬆️' : '⬇️';
  };

  if (!data || data.length === 0) {
    return (
      <div className="data-table-container">
        <p>No data available. Please upload a CSV file.</p>
      </div>
    );
  }

  return (
    <div className="data-table-container">
      <h2>📋 Equipment Data Table</h2>
      
      {/* Search input */}
      <div style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="🔍 Search by name or type..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            padding: '0.75rem 1rem',
            width: '100%',
            maxWidth: '400px',
            border: '2px solid #ddd',
            borderRadius: '8px',
            fontSize: '1rem'
          }}
        />
      </div>
      
      {/* Results count */}
      <p style={{ marginBottom: '1rem', color: '#666' }}>
        Showing {processedData.length} of {data.length} records
      </p>
      
      {/* Data table */}
      <table className="data-table">
        <thead>
          <tr>
            <th onClick={() => handleSort('Equipment Name')} style={{ cursor: 'pointer' }}>
              Equipment Name {getSortIndicator('Equipment Name')}
            </th>
            <th onClick={() => handleSort('Type')} style={{ cursor: 'pointer' }}>
              Type {getSortIndicator('Type')}
            </th>
            <th onClick={() => handleSort('Flowrate')} style={{ cursor: 'pointer' }}>
              Flowrate {getSortIndicator('Flowrate')}
            </th>
            <th onClick={() => handleSort('Pressure')} style={{ cursor: 'pointer' }}>
              Pressure {getSortIndicator('Pressure')}
            </th>
            <th onClick={() => handleSort('Temperature')} style={{ cursor: 'pointer' }}>
              Temperature {getSortIndicator('Temperature')}
            </th>
          </tr>
        </thead>
        <tbody>
          {processedData.map((item, index) => (
            <tr key={index}>
              <td><strong>{item['Equipment Name']}</strong></td>
              <td>
                <span style={{
                  background: getTypeColor(item['Type']),
                  color: 'white',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '20px',
                  fontSize: '0.85rem'
                }}>
                  {item['Type']}
                </span>
              </td>
              <td>{item['Flowrate']}</td>
              <td>{item['Pressure']}</td>
              <td>{item['Temperature']}°</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * Get color for equipment type badge
 */
function getTypeColor(type) {
  const colors = {
    'Pump': '#3498db',
    'Compressor': '#e74c3c',
    'Valve': '#2ecc71',
    'HeatExchanger': '#f39c12',
    'Reactor': '#9b59b6',
    'Condenser': '#1abc9c'
  };
  return colors[type] || '#95a5a6';
}

export default DataTable;
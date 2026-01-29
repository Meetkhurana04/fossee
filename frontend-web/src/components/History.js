// frontend-web/src/components/History.js
/**
 * History Component
 * 
 * Displays the last 5 uploaded datasets.
 * Allows users to select a dataset to view its details.
 */

import React, { useState, useEffect } from 'react';
import { getHistory, getDataset, deleteDataset } from '../services/api';

function History({ onSelectDataset }) {
  // List of datasets
  const [datasets, setDatasets] = useState([]);
  
  // Loading state
  const [loading, setLoading] = useState(true);
  
  // Error state
  const [error, setError] = useState(null);

  // Load history on component mount
  useEffect(() => {
    loadHistory();
  }, []);

  /**
   * Fetch history from API
   */
  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await getHistory();
      setDatasets(data);
      setError(null);
    } catch (err) {
      setError('Failed to load history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle dataset selection
   */
  const handleSelect = async (id) => {
    try {
      // Fetch full dataset with raw data
      const fullDataset = await getDataset(id);
      onSelectDataset(fullDataset);
    } catch (err) {
      setError('Failed to load dataset');
    }
  };

  /**
   * Handle dataset deletion
   */
  const handleDelete = async (e, id) => {
    e.stopPropagation(); // Prevent triggering select
    
    if (window.confirm('Are you sure you want to delete this dataset?')) {
      try {
        await deleteDataset(id);
        // Refresh the list
        loadHistory();
      } catch (err) {
        setError('Failed to delete dataset');
      }
    }
  };

  /**
   * Format date for display
   */
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="history-container">
        <h2>🕐 Upload History</h2>
        <div className="loading">
          <div className="spinner"></div>
          <span>Loading history...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-container">
        <h2>🕐 Upload History</h2>
        <div className="error-banner">{error}</div>
        <button onClick={loadHistory} className="btn-upload">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="history-container">
      <h2>🕐 Upload History (Last 5 Datasets)</h2>
      
      {datasets.length === 0 ? (
        <div className="no-history">
          <p>📭 No datasets uploaded yet.</p>
          <p>Upload a CSV file to get started!</p>
        </div>
      ) : (
        <div className="history-list">
          {datasets.map((dataset) => (
            <div
              key={dataset.id}
              className="history-item"
              onClick={() => handleSelect(dataset.id)}
            >
              <div className="history-item-info">
                <h4>📄 {dataset.name}</h4>
                <p>Uploaded: {formatDate(dataset.uploaded_at)}</p>
              </div>
              
              <div className="history-item-stats">
                <div className="stat">
                  <div className="stat-value">{dataset.record_count}</div>
                  <div className="stat-label">Records</div>
                </div>
                
                {dataset.summary_parsed && (
                  <>
                    <div className="stat">
                      <div className="stat-value">
                        {dataset.summary_parsed.averages.flowrate}
                      </div>
                      <div className="stat-label">Avg Flow</div>
                    </div>
                    
                    <div className="stat">
                      <div className="stat-value">
                        {Object.keys(dataset.summary_parsed.type_distribution).length}
                      </div>
                      <div className="stat-label">Types</div>
                    </div>
                  </>
                )}
                
                <button
                  onClick={(e) => handleDelete(e, dataset.id)}
                  style={{
                    background: '#e74c3c',
                    color: 'white',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Refresh button */}
      <button
        onClick={loadHistory}
        style={{
          marginTop: '1rem',
          padding: '0.75rem 1.5rem',
          background: '#3498db',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer'
        }}
      >
        🔄 Refresh History
      </button>
    </div>
  );
}

export default History;
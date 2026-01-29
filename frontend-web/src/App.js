// frontend-web/src/App.js
/**
 * Main Application Component
 * 
 * This is the root component that manages:
 * - Authentication state
 * - Current dataset state
 * - Navigation between sections
 * - Layout and styling
 */

import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import DataTable from './components/DataTable';
import Charts from './components/Charts';
import Summary from './components/Summary';
import History from './components/History';
import Login from './components/Login';
import { getLatestDataset, logout, downloadPDF } from './services/api';
import './App.css';

function App() {
  // State for current dataset being displayed
  const [currentDataset, setCurrentDataset] = useState(null);
  
  // Loading state for async operations
  const [loading, setLoading] = useState(false);
  
  // Error message state
  const [error, setError] = useState(null);
  
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  
  // Active tab for navigation
  const [activeTab, setActiveTab] = useState('upload');

  // Check for existing auth on mount
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      setIsAuthenticated(true);
      setUser(JSON.parse(savedUser));
    }
    
    // Load latest dataset on mount
    loadLatestDataset();
  }, []);

  /**
   * Load the most recently uploaded dataset
   */
  const loadLatestDataset = async () => {
    try {
      setLoading(true);
      const data = await getLatestDataset();
      setCurrentDataset(data);
      setError(null);
    } catch (err) {
      // No dataset found is not an error
      if (err.response?.status !== 404) {
        console.error('Error loading dataset:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle successful file upload
   */
  const handleUploadSuccess = (data) => {
    setCurrentDataset(data.dataset);
    setActiveTab('summary');
    setError(null);
  };

  /**
   * Handle dataset selection from history
   */
  const handleSelectDataset = (dataset) => {
    setCurrentDataset(dataset);
    setActiveTab('summary');
  };

  /**
   * Handle login success
   */
  const handleLoginSuccess = (userData, token) => {
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setIsAuthenticated(true);
    setUser(userData);
  };

  /**
   * Handle logout
   */
  const handleLogout = async () => {
    await logout();
    setIsAuthenticated(false);
    setUser(null);
  };

  /**
   * Handle PDF download
   */
  const handleDownloadPDF = async () => {
    if (currentDataset) {
      try {
        await downloadPDF(currentDataset.id);
      } catch (err) {
        setError('Failed to download PDF');
      }
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>⚗️ Chemical Equipment Visualizer</h1>
          <div className="header-actions">
            {isAuthenticated ? (
              <div className="user-info">
                <span>Welcome, {user?.username}</span>
                <button onClick={handleLogout} className="btn-logout">
                  Logout
                </button>
              </div>
            ) : (
              <button 
                onClick={() => setActiveTab('login')} 
                className="btn-login"
              >
                Login
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="app-nav">
        <button 
          className={`nav-btn ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📤 Upload
        </button>
        <button 
          className={`nav-btn ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
          disabled={!currentDataset}
        >
          📊 Summary
        </button>
        <button 
          className={`nav-btn ${activeTab === 'table' ? 'active' : ''}`}
          onClick={() => setActiveTab('table')}
          disabled={!currentDataset}
        >
          📋 Data Table
        </button>
        <button 
          className={`nav-btn ${activeTab === 'charts' ? 'active' : ''}`}
          onClick={() => setActiveTab('charts')}
          disabled={!currentDataset}
        >
          📈 Charts
        </button>
        <button 
          className={`nav-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          🕐 History
        </button>
      </nav>

      {/* Main Content */}
      <main className="app-main">
        {/* Error Display */}
        {error && (
          <div className="error-banner">
            {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <span>Loading...</span>
          </div>
        )}

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'login' && !isAuthenticated && (
            <Login onLoginSuccess={handleLoginSuccess} />
          )}

          {activeTab === 'upload' && (
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          )}

          {activeTab === 'summary' && currentDataset && (
            <div className="summary-section">
              <Summary dataset={currentDataset} />
              <button 
                className="btn-download-pdf"
                onClick={handleDownloadPDF}
              >
                📄 Download PDF Report
              </button>
            </div>
          )}

          {activeTab === 'table' && currentDataset && (
            <DataTable data={currentDataset.raw_data_parsed} />
          )}

          {activeTab === 'charts' && currentDataset && (
            <Charts dataset={currentDataset} />
          )}

          {activeTab === 'history' && (
            <History onSelectDataset={handleSelectDataset} />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Chemical Equipment Parameter Visualizer © 2024</p>
      </footer>
    </div>
  );
}

export default App;
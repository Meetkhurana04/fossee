// frontend-web/src/components/FileUpload.js
/**
 * FileUpload Component
 * 
 * Provides drag-and-drop file upload functionality.
 * Validates file type and sends to backend API.
 */

import React, { useState, useRef } from 'react';
import { uploadCSV } from '../services/api';

function FileUpload({ onUploadSuccess }) {
  // Selected file state
  const [selectedFile, setSelectedFile] = useState(null);
  
  // Upload status states
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  
  // Drag state for visual feedback
  const [isDragOver, setIsDragOver] = useState(false);
  
  // File input reference for programmatic clicking
  const fileInputRef = useRef(null);

  /**
   * Handle file selection from input
   */
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    validateAndSetFile(file);
  };

  /**
   * Validate file and set state
   */
  const validateAndSetFile = (file) => {
    setError(null);
    
    if (!file) return;
    
    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setError('Please select a CSV file');
      return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }
    
    setSelectedFile(file);
  };

  /**
   * Handle drag over event
   */
  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  /**
   * Handle drag leave event
   */
  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  /**
   * Handle file drop
   */
  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const file = event.dataTransfer.files[0];
    validateAndSetFile(file);
  };

  /**
   * Upload file to backend
   */
  const handleUpload = async () => {
    if (!selectedFile) return;
    
    try {
      setUploading(true);
      setError(null);
      
      // Call API to upload file
      const response = await uploadCSV(selectedFile);
      
      // Call success callback with response data
      onUploadSuccess(response);
      
      // Reset state
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload">
      <h2>📤 Upload Equipment Data</h2>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>
        Upload a CSV file containing equipment parameters
      </p>
      
      {/* Drop zone area */}
      <div
        className={`upload-area ${isDragOver ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="upload-icon">📁</div>
        <h3>Drag & Drop your CSV file here</h3>
        <p>or click to browse</p>
        
        {/* Hidden file input */}
        <input
          type="file"
          ref={fileInputRef}
          className="file-input"
          accept=".csv"
          onChange={handleFileSelect}
        />
      </div>
      
      {/* Selected file display */}
      {selectedFile && (
        <div className="selected-file">
          <span>📄</span>
          <strong>{selectedFile.name}</strong>
          <span>({(selectedFile.size / 1024).toFixed(1)} KB)</span>
        </div>
      )}
      
      {/* Error display */}
      {error && (
        <div className="form-error" style={{ marginTop: '1rem' }}>
          ⚠️ {error}
        </div>
      )}
      
      {/* Upload button */}
      <button
        className="btn-upload"
        onClick={handleUpload}
        disabled={!selectedFile || uploading}
      >
        {uploading ? '⏳ Uploading...' : '🚀 Upload & Analyze'}
      </button>
      
      {/* Instructions */}
      <div style={{ marginTop: '2rem', color: '#666', fontSize: '0.9rem' }}>
        <h4>Required CSV Format:</h4>
        <code style={{ 
          display: 'block', 
          marginTop: '0.5rem',
          padding: '1rem',
          background: '#f1f1f1',
          borderRadius: '4px'
        }}>
          Equipment Name, Type, Flowrate, Pressure, Temperature
        </code>
      </div>
    </div>
  );
}

export default FileUpload;
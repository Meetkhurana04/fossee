// frontend-web/src/components/Login.js
/**
 * Login Component
 * 
 * Provides login and registration forms.
 * Handles authentication with the backend API.
 */

import React, { useState } from 'react';
import { login, register } from '../services/api';

function Login({ onLoginSuccess }) {
  // Form mode: 'login' or 'register'
  const [mode, setMode] = useState('login');
  
  // Form data
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  // Loading and error states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Handle form input changes
   */
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(null);
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    // Validate form
    if (!formData.username || !formData.password) {
      setError('Please fill in all required fields');
      return;
    }
    
    if (mode === 'register') {
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        return;
      }
      if (formData.password.length < 6) {
        setError('Password must be at least 6 characters');
        return;
      }
    }
    
    try {
      setLoading(true);
      
      let response;
      if (mode === 'login') {
        response = await login({
          username: formData.username,
          password: formData.password
        });
      } else {
        response = await register({
          username: formData.username,
          email: formData.email,
          password: formData.password
        });
      }
      
      // Call success callback
      onLoginSuccess(response.user, response.token);
      
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Toggle between login and register modes
   */
  const toggleMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError(null);
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    });
  };

  return (
    <div className="login-container">
      <h2>{mode === 'login' ? '🔐 Login' : '📝 Register'}</h2>
      
      <form className="login-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Enter your username"
            required
          />
        </div>
        
        {mode === 'register' && (
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
            />
          </div>
        )}
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter your password"
            required
          />
        </div>
        
        {mode === 'register' && (
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
              required
            />
          </div>
        )}
        
        {error && <div className="form-error">⚠️ {error}</div>}
        
        <button type="submit" className="btn-submit" disabled={loading}>
          {loading ? '⏳ Please wait...' : mode === 'login' ? 'Login' : 'Register'}
        </button>
      </form>
      
      <div className="login-toggle">
        <p>
          {mode === 'login' 
            ? "Don't have an account? " 
            : "Already have an account? "}
          <button onClick={toggleMode}>
            {mode === 'login' ? 'Register' : 'Login'}
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;
import React, { useState } from 'react';
import { 
  Leaf, 
  User, 
  ShieldCheck, 
  ArrowRight, 
  Camera, 
  FileText, 
  BookOpen, 
  BarChart3, 
  Map, 
  Flame,
  Sparkles,
  Lock,
  Mail,
  Key,
  AlertCircle,
  Loader2,
  CheckCircle2,
  UserPlus,
  LogIn
} from 'lucide-react';
import { authApi } from '../services/api';

export default function LoginRoleSelect({ onLoginSuccess }) {
  const [activeTab, setActiveTab] = useState('login'); // 'login' | 'register'
  const [selectedRole, setSelectedRole] = useState('user'); // 'user' | 'admin'
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Switch role context without inserting fake credentials
  const handleSelectRoleCard = (role) => {
    setSelectedRole(role);
    setErrorMessage('');
    setSuccessMessage('');
    if (role === 'admin') {
      setActiveTab('login');
    }
    const formElement = document.getElementById('auth-form-card');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    const trimmedEmail = email.trim();
    const trimmedName = name.trim();

    // 1. Validation
    if (!trimmedEmail) {
      setErrorMessage('Please enter your email address.');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmedEmail)) {
      setErrorMessage('Please enter a valid email address.');
      return;
    }

    if (!password) {
      setErrorMessage('Please enter your password.');
      return;
    }

    if (password.length < 6) {
      setErrorMessage('Password must be at least 6 characters long.');
      return;
    }

    if (activeTab === 'register') {
      if (!trimmedName) {
        setErrorMessage('Please enter your full name for registration.');
        return;
      }
      if (trimmedName.length < 2) {
        setErrorMessage('Full name must be at least 2 characters long.');
        return;
      }
    }

    setIsLoading(true);

    try {
      if (activeTab === 'register') {
        // Register new citizen user (backend always creates role='user')
        await authApi.register({
          name: trimmedName,
          email: trimmedEmail,
          password,
        });

        setSuccessMessage('Account created successfully! Authenticating...');

        // Authenticate with the database
        const loginRes = await authApi.login({ email: trimmedEmail, password });
        if (!loginRes?.access_token) {
          throw new Error('Authentication token not received from server.');
        }

        setTimeout(() => {
          if (onLoginSuccess) {
            onLoginSuccess(loginRes.user, loginRes.user.role);
          }
        }, 400);
      } else {
        // Authenticate existing user/admin with the database
        const res = await authApi.login({ email: trimmedEmail, password });
        if (!res?.access_token) {
          throw new Error('Authentication token not received from server.');
        }

        // Verify role privilege if administrator portal was specifically requested
        if (selectedRole === 'admin' && res.user.role !== 'admin') {
          authApi.logout?.();
          throw new Error('Access denied: This account does not possess municipal administrator privileges.');
        }

        setSuccessMessage(`Welcome back, ${res.user?.name || 'User'}!`);
        setTimeout(() => {
          if (onLoginSuccess) {
            onLoginSuccess(res.user, res.user.role);
          }
        }, 400);
      }
    } catch (err) {
      console.warn('Authentication error:', err);
      // Map error messages cleanly
      let displayError = err.message || 'Authentication failed. Please verify your credentials.';
      if (err.status === 401) {
        displayError = 'Invalid email or password.';
      } else if (err.status === 404) {
        displayError = 'Account not found with this email.';
      } else if (err.status === 400 && displayError.toLowerCase().includes('already exists')) {
        displayError = 'An account with this email already exists.';
      }
      setErrorMessage(displayError);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page-wrapper">
      <div className="container login-container" style={{ maxWidth: '880px' }}>
        {/* Brand Header */}
        <div className="login-brand-header">
          <div className="login-logo-group">
            <div className="logo-icon-wrapper" style={{ width: 44, height: 44, borderRadius: 12 }}>
              <Leaf size={24} strokeWidth={2.2} />
            </div>
            <span style={{ fontSize: '1.65rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              EcoCycle
            </span>
          </div>

          <div className="badge-pill" style={{ margin: '0.85rem auto 0 auto' }}>
            <Sparkles size={13} />
            <span>Community Waste Management Platform</span>
          </div>

          <h1 className="login-title">
            Welcome to EcoCycle
          </h1>
          <p className="subheading login-subtitle">
            Choose your access role or sign in with your credentials.
          </p>
        </div>

        {/* 2 Large Role Cards Grid */}
        <div className="role-cards-grid" style={{ marginBottom: '2rem' }}>
          {/* Card 1: Regular User */}
          <div 
            className={`role-card ${selectedRole === 'user' ? 'selected' : ''}`}
            style={{
              cursor: 'pointer',
              border: selectedRole === 'user' ? '2px solid var(--sage-600)' : '1px solid var(--border-color)',
              transform: selectedRole === 'user' ? 'translateY(-2px)' : 'none',
              boxShadow: selectedRole === 'user' ? '0 8px 24px rgba(85, 117, 92, 0.15)' : 'none'
            }}
            onClick={() => handleSelectRoleCard('user')}
          >
            <div className="role-card-top">
              <div className="role-icon-box user-icon-box">
                <User size={28} strokeWidth={2} />
              </div>
              <span className="role-type-badge">Citizen Access</span>
            </div>

            <div className="role-card-body">
              <h2 className="role-name">Regular User</h2>
              <p className="role-desc">
                Scan waste, report waste, track your reports, and learn about responsible waste disposal.
              </p>

              <div className="role-features-list">
                <div className="role-feature-item">
                  <Camera size={15} className="text-sage-accent" />
                  <span>AI Waste Identification</span>
                </div>
                <div className="role-feature-item">
                  <FileText size={15} className="text-sage-accent" />
                  <span>Report Community Waste</span>
                </div>
                <div className="role-feature-item">
                  <BookOpen size={15} className="text-sage-accent" />
                  <span>Interactive Recycling Guide</span>
                </div>
              </div>
            </div>

            <div className="role-card-footer">
              <button 
                type="button" 
                className="btn btn-primary role-cta-btn"
                disabled={isLoading}
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelectRoleCard('user');
                }}
              >
                <span>Continue as User</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>

          {/* Card 2: Administrator */}
          <div 
            className={`role-card ${selectedRole === 'admin' ? 'selected' : ''}`}
            style={{
              cursor: 'pointer',
              border: selectedRole === 'admin' ? '2px solid var(--sage-700)' : '1px solid var(--border-color)',
              transform: selectedRole === 'admin' ? 'translateY(-2px)' : 'none',
              boxShadow: selectedRole === 'admin' ? '0 8px 24px rgba(49, 82, 115, 0.15)' : 'none'
            }}
            onClick={() => handleSelectRoleCard('admin')}
          >
            <div className="role-card-top">
              <div className="role-icon-box admin-icon-box">
                <ShieldCheck size={28} strokeWidth={2} />
              </div>
              <span className="role-type-badge" style={{ backgroundColor: '#EAF0F6', color: '#315273' }}>
                Municipal Dispatch
              </span>
            </div>

            <div className="role-card-body">
              <h2 className="role-name">Administrator</h2>
              <p className="role-desc">
                Monitor waste reports, locations, hotspots, and waste-management analytics.
              </p>

              <div className="role-features-list">
                <div className="role-feature-item">
                  <BarChart3 size={15} className="text-sage-accent" />
                  <span>Live Municipal Dashboard</span>
                </div>
                <div className="role-feature-item">
                  <Map size={15} className="text-sage-accent" />
                  <span>Hotspot Map & Area Surveillance</span>
                </div>
                <div className="role-feature-item">
                  <Flame size={15} className="text-sage-accent" />
                  <span>Priority Resolution Pipeline</span>
                </div>
              </div>
            </div>

            <div className="role-card-footer">
              <button 
                type="button" 
                className="btn btn-primary role-cta-btn"
                disabled={isLoading}
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelectRoleCard('admin');
                }}
              >
                <span>Continue as Administrator</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Authentication Card (Login & Register Form) */}
        <div id="auth-form-card" style={{
          backgroundColor: 'var(--bg-card)',
          borderRadius: 'var(--radius-md)',
          padding: '1.75rem',
          border: '1px solid var(--border-color)',
          boxShadow: '0 4px 16px rgba(0,0,0,0.04)',
          maxWidth: '520px',
          margin: '0 auto',
        }}>
          {/* Form Toggle Header */}
          <div style={{
            display: 'flex',
            borderBottom: '1px solid var(--border-color)',
            marginBottom: '1.25rem',
            paddingBottom: '0.5rem',
            gap: '1rem',
          }}>
            <button
              type="button"
              style={{
                background: 'none',
                border: 'none',
                fontWeight: activeTab === 'login' ? 700 : 500,
                color: activeTab === 'login' ? 'var(--sage-700)' : 'var(--text-muted)',
                borderBottom: activeTab === 'login' ? '2px solid var(--sage-700)' : '2px solid transparent',
                padding: '0.4rem 0.6rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                fontSize: '0.95rem',
              }}
              onClick={() => { setActiveTab('login'); setErrorMessage(''); }}
            >
              <LogIn size={16} />
              <span>Sign In</span>
            </button>

            {selectedRole === 'user' && (
              <button
                type="button"
                style={{
                  background: 'none',
                  border: 'none',
                  fontWeight: activeTab === 'register' ? 700 : 500,
                  color: activeTab === 'register' ? 'var(--sage-700)' : 'var(--text-muted)',
                  borderBottom: activeTab === 'register' ? '2px solid var(--sage-700)' : '2px solid transparent',
                  padding: '0.4rem 0.6rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontSize: '0.95rem',
                }}
                onClick={() => { setActiveTab('register'); setErrorMessage(''); }}
              >
                <UserPlus size={16} />
                <span>Create Citizen Account</span>
              </button>
            )}
          </div>

          {/* Feedback Messages */}
          {errorMessage && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              backgroundColor: '#FDF7F7',
              border: '1px solid #EAC8C8',
              color: '#A83B3B',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.875rem',
              marginBottom: '1rem',
            }}>
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <span>{errorMessage}</span>
            </div>
          )}

          {successMessage && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              backgroundColor: '#F2F8F4',
              border: '1px solid #B8D6C0',
              color: '#2A5A35',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.875rem',
              marginBottom: '1rem',
            }}>
              <CheckCircle2 size={16} style={{ flexShrink: 0 }} />
              <span>{successMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
            {activeTab === 'register' && (
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                  Full Name
                </label>
                <div style={{ position: 'relative' }}>
                  <User size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input
                    type="text"
                    required
                    placeholder="e.g. John Doe"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.65rem 0.75rem 0.65rem 2.2rem',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border-color)',
                      fontSize: '0.9rem',
                    }}
                  />
                </div>
              </div>
            )}

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                Email Address
              </label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="email"
                  required
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.75rem 0.65rem 2.2rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color)',
                    fontSize: '0.9rem',
                  }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Key size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="password"
                  required
                  minLength={6}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.75rem 0.65rem 2.2rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color)',
                    fontSize: '0.9rem',
                  }}
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading}
              style={{
                width: '100%',
                marginTop: '0.5rem',
                padding: '0.75rem',
                justifyContent: 'center',
                fontWeight: 600,
              }}
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="spin-animate" />
                  <span>Connecting...</span>
                </>
              ) : activeTab === 'register' ? (
                <>
                  <UserPlus size={16} />
                  <span>Create Account & Log In</span>
                </>
              ) : (
                <>
                  <LogIn size={16} />
                  <span>Sign In ({selectedRole === 'admin' ? 'Admin' : 'User'})</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Trust & Security Footnote */}
        <div className="login-footnote" style={{ marginTop: '1.5rem' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <Lock size={13} />
            <span>Secure JWT authentication powered by FastAPI backend</span>
          </div>
        </div>
      </div>
    </div>
  );
}

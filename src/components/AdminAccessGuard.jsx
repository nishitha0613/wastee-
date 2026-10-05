import React from 'react';
import { ShieldAlert, Home, ArrowLeft } from 'lucide-react';

export default function AdminAccessGuard({ onNavigate, attemptedTab = 'Dashboard' }) {
  return (
    <section className="access-guard-section">
      <div className="container">
        <div className="access-guard-card">
          <div className="access-guard-icon-box">
            <ShieldAlert size={38} strokeWidth={2.1} />
          </div>

          <div className="badge-pill" style={{ marginBottom: '1.25rem', color: 'var(--sage-700)', borderColor: 'var(--sage-300)' }}>
            Restricted Page • {attemptedTab}
          </div>

          <h1 className="access-guard-title">Administrator Access Required</h1>

          <p className="access-guard-subtitle">
            Only administrators can access this section.
          </p>

          <div className="access-guard-notice-box">
            <p>
              You are currently browsing as a <strong>Regular User</strong>. Administrative tools such as municipal analytics, hotspot maps, and dispatch controls require administrator privileges.
            </p>
          </div>

          <div className="access-guard-actions">
            <button 
              type="button" 
              className="btn btn-primary"
              id="return-home-btn"
              onClick={() => onNavigate('Home')}
            >
              <Home size={17} />
              <span>Return Home</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

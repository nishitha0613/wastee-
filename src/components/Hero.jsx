import React from 'react';
import { Camera, MapPin, Sparkles, CheckCircle2 } from 'lucide-react';

export default function Hero({ onAction }) {
  return (
    <section className="hero-section">
      <div className="container hero-grid">
        {/* Left Column: Hero Content */}
        <div className="hero-content">
          <div>
            <div className="badge-pill" style={{ marginBottom: '1.25rem' }}>
              <Sparkles size={15} />
              <span>Smart Community Platform</span>
            </div>
            
            <h1 className="heading-primary">
              Smarter Waste Management, <span className="text-sage-accent">Cleaner Communities.</span>
            </h1>
          </div>

          <p className="subheading">
            A simple platform to identify, report, and understand waste for cleaner communities.
          </p>

          <div className="hero-cta-group">
            <button 
              className="btn btn-primary"
              onClick={() => onAction('Scan Waste')}
            >
              <Camera size={18} />
              <span>Scan Waste</span>
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => onAction('Report Waste')}
            >
              <MapPin size={18} className="text-sage-accent" />
              <span>Report Waste</span>
            </button>
          </div>

          {/* Key Trust Signals */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginTop: '1rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <CheckCircle2 size={16} className="text-sage-accent" />
              <span>Instant AI Identification</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <CheckCircle2 size={16} className="text-sage-accent" />
              <span>Community Hotspot Map</span>
            </div>
          </div>
        </div>

        {/* Right Column: Hero Sustainability Visual */}
        <div className="hero-visual">
          <div className="hero-visual-card">
            <div className="hero-image-wrapper">
              <img 
                src="/hero-visual.jpg" 
                alt="EcoCycle Waste Management & Sustainability Illustration" 
                loading="eager"
              />
            </div>
            
            <div className="hero-floating-tag">
              <div className="floating-icon-bubble">
                <Sparkles size={16} />
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Community Goal</div>
                <div style={{ fontSize: '0.9rem', color: 'var(--sage-800)', fontWeight: 700 }}>Zero Waste Hotspots</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

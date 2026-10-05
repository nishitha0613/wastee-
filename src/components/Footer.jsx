import React from 'react';
import { Leaf, Heart } from 'lucide-react';

export default function Footer({ onNavigate, currentRole }) {
  const handleLinkClick = (e, target) => {
    e.preventDefault();
    onNavigate(target);
  };

  const isUser = currentRole === 'user';

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          {/* Brand Info */}
          <div className="footer-brand">
            <a href="#" className="logo" onClick={(e) => handleLinkClick(e, isUser ? 'Home' : 'Dashboard')}>
              <div className="logo-icon-wrapper">
                <Leaf size={20} strokeWidth={2.2} />
              </div>
              <span>EcoCycle</span>
            </a>
            <p className="footer-description">
              A modern, community-driven platform transforming municipal waste management through intelligent scanning, reporting, and hotspot tracking.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="footer-column-title">Platform Navigation</h4>
            <ul className="footer-links">
              {isUser ? (
                <>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Home')}>Home</a>
                  </li>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Waste Scanner')}>Waste Scanner</a>
                  </li>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Report Waste')}>Report Waste</a>
                  </li>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'My Reports')}>My Reports</a>
                  </li>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Learn & Recycle')}>Learn & Recycle</a>
                  </li>
                </>
              ) : (
                <>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Dashboard')}>Dashboard</a>
                  </li>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Waste Map')}>Waste Map</a>
                  </li>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'All Reports')}>All Reports</a>
                  </li>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Analytics')}>Analytics</a>
                  </li>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Environmental Impact')}>Environmental Impact</a>
                  </li>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Learn & Recycle')}>Learn & Recycle</a>
                  </li>
                </>
              )}
            </ul>
          </div>

          {/* Impact & Community */}
          <div>
            <h4 className="footer-column-title">Community & Impact</h4>
            <ul className="footer-links">
              <li>
                <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Recycling Guide')}>Recycling Guidelines</a>
              </li>
              {!isUser ? (
                <>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Waste Map')}>Neighborhood Hotspot Map</a>
                  </li>
                  <li>
                    <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Environmental Impact')}>Environmental Impact</a>
                  </li>
                </>
              ) : (
                <li>
                  <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Impact Report')}>2026 Impact Report</a>
                </li>
              )}
              <li>
                <a href="#" className="footer-link" onClick={(e) => handleLinkClick(e, 'Support')}>Help & Support</a>
              </li>
            </ul>
          </div>
        </div>

        {/* Footer Bottom */}
        <div className="footer-bottom">
          <div>
            &copy; {new Date().getFullYear()} EcoCycle Sustainability Inc. All rights reserved.
          </div>
          <div className="sustainability-note">
            <Heart size={15} style={{ fill: '#6E8B74', stroke: '#5B7861' }} />
            <span>Building cleaner, sustainable communities everywhere.</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

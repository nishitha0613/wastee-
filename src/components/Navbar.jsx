import React, { useState } from 'react';
import { Leaf, Menu, X, ArrowRight, LogOut } from 'lucide-react';

export default function Navbar({ activeTab, onNavigate, currentRole, currentUser, onLogout }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNavClick = (tabName) => {
    onNavigate(tabName);
    setMobileMenuOpen(false);
  };

  const isUserRole = currentRole === 'user';

  // Navigation items strictly based on role:
  // Regular User: Home, Waste Scanner, Report Waste, My Reports, Learn & Recycle
  // Administrator: Dashboard, Waste Map, All Reports, Analytics, Environmental Impact, Learn & Recycle, Logout
  const navItems = isUserRole
    ? [
        { label: 'Home', tab: 'Home' },
        { label: 'Waste Scanner', tab: 'Waste Scanner' },
        { label: 'Report Waste', tab: 'Report Waste' },
        { label: 'My Reports', tab: 'My Reports' },
        { label: 'Learn & Recycle', tab: 'Learn & Recycle' },
      ]
    : [
        { label: 'Dashboard', tab: 'Dashboard' },
        { label: 'Waste Map', tab: 'Waste Map' },
        { label: 'All Reports', tab: 'All Reports' },
        { label: 'Analytics', tab: 'Analytics' },
        { label: 'Environmental Impact', tab: 'Environmental Impact' },
        { label: 'Learn & Recycle', tab: 'Learn & Recycle' },
        { label: 'Logout', tab: 'Logout', isLogout: true },
      ];

  const handleItemClick = (item) => {
    if (item.isLogout) {
      setMobileMenuOpen(false);
      if (onLogout) onLogout();
    } else {
      handleNavClick(item.tab);
    }
  };

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        {/* Brand Logo - routes to Dashboard for admin, Home for regular user */}
        <a 
          href="#" 
          className="logo" 
          onClick={(e) => { 
            e.preventDefault(); 
            handleNavClick(isUserRole ? 'Home' : 'Dashboard'); 
          }}
        >
          <div className="logo-icon-wrapper">
            <Leaf size={20} strokeWidth={2.2} />
          </div>
          <span>EcoCycle</span>
        </a>

        {/* Desktop Navigation Links */}
        <nav aria-label="Main Navigation">
          <ul className="nav-links">
            {navItems.map((item) => (
              <li key={item.tab}>
                <button 
                  className={`nav-link ${activeTab === item.tab ? 'active' : ''} ${item.isLogout ? 'nav-link-logout' : ''}`}
                  id={item.isLogout ? 'navbar-logout-btn' : undefined}
                  onClick={() => handleItemClick(item)}
                >
                  {item.isLogout && (
                    <LogOut size={14} style={{ marginRight: '0.35rem', verticalAlign: 'middle' }} />
                  )}
                  <span>{item.label}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* Desktop CTA Action */}
        <div className="nav-actions">
          {currentRole && (
            <div 
              className="role-indicator-badge" 
              title={currentUser?.email ? `${currentUser.name} (${currentUser.email})` : `Current role: ${currentRole === 'admin' ? 'Administrator' : 'Regular User'}`}
            >
              <span className="role-dot" />
              <span>{currentUser?.name || (currentRole === 'admin' ? 'Admin' : 'User')}</span>
            </div>
          )}

          {/* Regular User Logout Button */}
          {isUserRole && onLogout && (
            <button 
              type="button"
              className="btn btn-secondary"
              style={{ padding: '0.55rem 0.95rem', fontSize: '0.85rem' }}
              onClick={onLogout}
              title="Return to login page"
              id="navbar-logout-btn-user"
            >
              <LogOut size={14} />
              <span>Logout</span>
            </button>
          )}

          {/* Regular User Get Started Action (routes to Waste Scanner) */}
          {isUserRole && (
            <button 
              className="btn btn-primary"
              onClick={() => handleNavClick('Get Started')}
            >
              Get Started
              <ArrowRight size={16} />
            </button>
          )}
        </div>

        {/* Mobile Hamburger Toggle */}
        <button 
          className="mobile-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle Navigation Menu"
        >
          {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile Nav Dropdown */}
      {mobileMenuOpen && (
        <div className="mobile-menu container">
          {navItems.map((item) => (
            <button 
              key={item.tab}
              className={`mobile-nav-link ${activeTab === item.tab ? 'active' : ''} ${item.isLogout ? 'mobile-nav-link-logout' : ''}`}
              onClick={() => handleItemClick(item)}
            >
              {item.isLogout && (
                <LogOut size={15} style={{ marginRight: '0.45rem', verticalAlign: 'middle' }} />
              )}
              <span>{item.label}</span>
            </button>
          ))}

          {/* Regular User mobile actions */}
          {isUserRole && currentRole && onLogout && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.85rem 0.5rem', borderTop: '1px solid var(--border-color)', marginTop: '0.5rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                Role: <strong>User</strong>
              </span>
              <button 
                type="button"
                className="btn btn-secondary"
                style={{ padding: '0.45rem 0.85rem', fontSize: '0.8rem' }}
                onClick={() => { setMobileMenuOpen(false); onLogout(); }}
              >
                <LogOut size={13} />
                <span>Logout</span>
              </button>
            </div>
          )}

          {isUserRole && (
            <button 
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '0.5rem' }}
              onClick={() => handleNavClick('Get Started')}
            >
              Get Started
              <ArrowRight size={16} />
            </button>
          )}
        </div>
      )}
    </header>
  );
}

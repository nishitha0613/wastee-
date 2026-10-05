import React, { useState } from 'react';
import { 
  Map, 
  MapPin, 
  AlertTriangle, 
  CheckCircle2, 
  Flame, 
  Layers, 
  X, 
  Calendar, 
  Filter, 
  RotateCcw,
  Sparkles,
  Info
} from 'lucide-react';

export default function WasteMap() {
  const [selectedWasteType, setSelectedWasteType] = useState('All');
  const [selectedSeverity, setSelectedSeverity] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [activeMarker, setActiveMarker] = useState(null);

  // 4 Top Statistics Cards (Demo Data)
  const stats = [
    { label: 'Total Reports', value: '320', icon: Layers },
    { label: 'Active Hotspots', value: '18', icon: Flame },
    { label: 'Resolved', value: '284', icon: CheckCircle2 },
    { label: 'High Priority', value: '12', icon: AlertTriangle },
  ];

  // Demo Waste Markers
  const demoMarkers = [
    {
      id: 1,
      x: 48,
      y: 42,
      wasteType: 'Plastic Waste',
      location: 'MG Road',
      severity: 'High',
      date: '20 Sep 2026',
      status: 'Pending',
    },
    {
      id: 2,
      x: 72,
      y: 35,
      wasteType: 'Mixed Waste',
      location: 'Indiranagar',
      severity: 'High',
      date: '19 Sep 2026',
      status: 'In Progress',
    },
    {
      id: 3,
      x: 84,
      y: 56,
      wasteType: 'E-waste',
      location: 'Whitefield',
      severity: 'Medium',
      date: '18 Sep 2026',
      status: 'Pending',
    },
    {
      id: 4,
      x: 34,
      y: 68,
      wasteType: 'Organic Waste',
      location: 'Jayanagar',
      severity: 'Low',
      date: '19 Sep 2026',
      status: 'Resolved',
    },
    {
      id: 5,
      x: 58,
      y: 62,
      wasteType: 'Plastic Waste',
      location: 'Koramangala',
      severity: 'Medium',
      date: '17 Sep 2026',
      status: 'In Progress',
    },
    {
      id: 6,
      x: 22,
      y: 28,
      wasteType: 'Hazardous Waste',
      location: 'Peenya',
      severity: 'High',
      date: '16 Sep 2026',
      status: 'Pending',
    },
    {
      id: 7,
      x: 33,
      y: 36,
      wasteType: 'Paper Waste',
      location: 'Malleshwaram',
      severity: 'Low',
      date: '20 Sep 2026',
      status: 'Resolved',
    },
    {
      id: 8,
      x: 46,
      y: 19,
      wasteType: 'Mixed Waste',
      location: 'Hebbal',
      severity: 'Medium',
      date: '18 Sep 2026',
      status: 'Pending',
    }
  ];

  // Demo Hotspots List
  const hotspots = [
    {
      id: 1,
      area: 'Indiranagar',
      reportsCount: '24 Reports',
      commonType: 'Mostly Plastic',
      severity: 'High Priority',
      status: 'Active Hotspot',
      severityLevel: 'High'
    },
    {
      id: 2,
      area: 'MG Road',
      reportsCount: '18 Reports',
      commonType: 'Mostly Mixed Waste',
      severity: 'High Priority',
      status: 'Active Hotspot',
      severityLevel: 'High'
    },
    {
      id: 3,
      area: 'Whitefield',
      reportsCount: '15 Reports',
      commonType: 'Mostly E-waste',
      severity: 'Medium Priority',
      status: 'Under Review',
      severityLevel: 'Medium'
    },
    {
      id: 4,
      area: 'Koramangala',
      reportsCount: '9 Reports',
      commonType: 'Mostly Packaging Paper',
      severity: 'Low Priority',
      status: 'Monitored',
      severityLevel: 'Low'
    }
  ];

  // Filtering Logic
  const filteredMarkers = demoMarkers.filter((m) => {
    const matchType = selectedWasteType === 'All' || m.wasteType.toLowerCase().includes(selectedWasteType.toLowerCase());
    const matchSeverity = selectedSeverity === 'All' || m.severity.toLowerCase() === selectedSeverity.toLowerCase();
    const matchStatus = selectedStatus === 'All' || m.status.toLowerCase() === selectedStatus.toLowerCase();
    return matchType && matchSeverity && matchStatus;
  });

  const handleResetFilters = () => {
    setSelectedWasteType('All');
    setSelectedSeverity('All');
    setSelectedStatus('All');
  };

  const renderStatusBadge = (status) => {
    switch (status) {
      case 'Resolved':
        return <span className="status-badge status-badge-resolved">Resolved</span>;
      case 'In Progress':
        return <span className="status-badge status-badge-in-progress">In Progress</span>;
      case 'Pending':
      default:
        return <span className="status-badge status-badge-pending">Pending</span>;
    }
  };

  const renderSeverityTag = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high':
      case 'high priority':
        return <span className="severity-tag severity-tag-high">High</span>;
      case 'medium':
      case 'medium priority':
        return <span className="severity-tag severity-tag-medium">Medium</span>;
      case 'low':
      case 'low priority':
      default:
        return <span className="severity-tag severity-tag-low">Low</span>;
    }
  };

  return (
    <section className="waste-map-section">
      <div className="container waste-map-container">
        {/* Page Title & Subtitle */}
        <div className="waste-map-header">
          <div className="badge-pill">
            <Map size={14} />
            <span>Municipal Waste Monitoring</span>
          </div>
          <h1 className="page-title">Waste Map</h1>
          <p className="subheading" style={{ maxWidth: '580px' }}>
            Explore reported waste locations and identify areas that need attention.
          </p>
        </div>

        {/* 4 Top Statistics Cards */}
        <div className="map-stats-grid">
          {stats.map((st, idx) => {
            const IconComp = st.icon;
            return (
              <div key={idx} className="map-stat-card">
                <div className="map-stat-icon-wrap">
                  <IconComp size={20} strokeWidth={2} />
                </div>
                <div>
                  <div className="map-stat-num">{st.value}</div>
                  <div className="map-stat-label">{st.label}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Map Card Wrapper */}
        <div className="map-card-wrapper">
          {/* Controls: Filter Section & Legend */}
          <div className="map-controls-bar">
            {/* Filters */}
            <div className="map-filters-group">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                <Filter size={15} className="text-sage-accent" />
                <span>Filters:</span>
              </div>

              {/* Waste Type Filter */}
              <select 
                className="filter-select"
                value={selectedWasteType}
                onChange={(e) => setSelectedWasteType(e.target.value)}
                aria-label="Filter by Waste Type"
              >
                <option value="All">All Waste Types</option>
                <option value="Plastic">Plastic</option>
                <option value="Mixed">Mixed Waste</option>
                <option value="E-waste">E-waste</option>
                <option value="Organic">Organic</option>
                <option value="Paper">Paper</option>
                <option value="Hazardous">Hazardous</option>
              </select>

              {/* Severity Filter */}
              <select 
                className="filter-select"
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                aria-label="Filter by Severity"
              >
                <option value="All">All Severities</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>

              {/* Status Filter */}
              <select 
                className="filter-select"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                aria-label="Filter by Status"
              >
                <option value="All">All Statuses</option>
                <option value="Pending">Pending</option>
                <option value="In Progress">In Progress</option>
                <option value="Resolved">Resolved</option>
              </select>

              {(selectedWasteType !== 'All' || selectedSeverity !== 'All' || selectedStatus !== 'All') && (
                <button 
                  type="button" 
                  onClick={handleResetFilters}
                  style={{ fontSize: '0.8rem', color: 'var(--sage-700)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem', padding: '0.3rem 0.5rem' }}
                >
                  <RotateCcw size={13} />
                  <span>Reset</span>
                </button>
              )}
            </div>

            {/* Severity Legend */}
            <div className="map-legend">
              <div className="legend-item">
                <span className="legend-dot legend-dot-low" />
                <span>Low</span>
              </div>
              <div className="legend-item">
                <span className="legend-dot legend-dot-medium" />
                <span>Medium</span>
              </div>
              <div className="legend-item">
                <span className="legend-dot legend-dot-high" />
                <span>High</span>
              </div>
            </div>
          </div>

          {/* Interactive Map Viewport with Styled Vector Grid */}
          <div className="map-viewport" onClick={() => setActiveMarker(null)}>
            <svg 
              className="map-svg-canvas" 
              viewBox="0 0 1000 540" 
              preserveAspectRatio="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Soft Land Mass */}
              <rect width="1000" height="540" fill="#E8ECE6" />

              {/* District Zones & Green Parks */}
              <path d="M 50 40 Q 150 20 220 70 T 320 180 Q 200 240 100 200 Z" fill="#DEE6DD" opacity="0.8" />
              <path d="M 680 80 Q 820 60 920 120 T 960 280 Q 840 320 740 240 Z" fill="#DCE5DC" opacity="0.8" />
              <path d="M 120 340 Q 280 320 340 420 T 260 520 Q 100 520 80 440 Z" fill="#DEE6DD" opacity="0.8" />
              <path d="M 580 360 Q 720 340 820 420 T 780 520 Q 640 520 540 460 Z" fill="#D8E2D7" opacity="0.8" />

              {/* Water Canal / Stream */}
              <path 
                d="M -10 260 C 220 240, 340 310, 520 270 S 760 190, 1020 220" 
                fill="none" 
                stroke="#D2DFD7" 
                strokeWidth="16" 
                strokeLinecap="round" 
              />

              {/* Road Grid Network */}
              {/* Major Arterial Roads */}
              <path d="M -10 160 L 1010 160" stroke="#F6F8F5" strokeWidth="6" />
              <path d="M -10 380 L 1010 380" stroke="#F6F8F5" strokeWidth="6" />
              <path d="M 310 -10 L 310 550" stroke="#F6F8F5" strokeWidth="6" />
              <path d="M 690 -10 L 690 550" stroke="#F6F8F5" strokeWidth="6" />

              {/* Diagonal Avenues */}
              <path d="M 50 -10 L 620 550" stroke="#F6F8F5" strokeWidth="4.5" />
              <path d="M 950 -10 L 380 550" stroke="#F6F8F5" strokeWidth="4.5" />
              <path d="M 100 550 L 850 -10" stroke="#F6F8F5" strokeWidth="4" />

              {/* Minor City Street Grid */}
              <line x1="120" y1="0" x2="120" y2="540" stroke="#F1F4EE" strokeWidth="2.5" />
              <line x1="210" y1="0" x2="210" y2="540" stroke="#F1F4EE" strokeWidth="2.5" />
              <line x1="430" y1="0" x2="430" y2="540" stroke="#F1F4EE" strokeWidth="2.5" />
              <line x1="510" y1="0" x2="510" y2="540" stroke="#F1F4EE" strokeWidth="2.5" />
              <line x1="600" y1="0" x2="600" y2="540" stroke="#F1F4EE" strokeWidth="2.5" />
              <line x1="800" y1="0" x2="800" y2="540" stroke="#F1F4EE" strokeWidth="2.5" />
              <line x1="900" y1="0" x2="900" y2="540" stroke="#F1F4EE" strokeWidth="2.5" />

              <line x1="0" y1="70" x2="1000" y2="70" stroke="#F1F4EE" strokeWidth="2.5" />
              <line x1="0" y1="230" x2="1000" y2="230" stroke="#F1F4EE" strokeWidth="2.5" />
              <line x1="0" y1="300" x2="1000" y2="300" stroke="#F1F4EE" strokeWidth="2.5" />
              <line x1="0" y1="460" x2="1000" y2="460" stroke="#F1F4EE" strokeWidth="2.5" />

              {/* Area Labels */}
              <text x="220" y="55" fill="#889A8D" fontSize="13" fontWeight="700" letterSpacing="2">PEENYA</text>
              <text x="440" y="45" fill="#889A8D" fontSize="13" fontWeight="700" letterSpacing="2">HEBBAL</text>
              <text x="250" y="240" fill="#889A8D" fontSize="13" fontWeight="700" letterSpacing="2">MALLESHWARAM</text>
              <text x="470" y="225" fill="#6A8070" fontSize="14" fontWeight="700" letterSpacing="2">CENTRAL / MG ROAD</text>
              <text x="730" y="200" fill="#6A8070" fontSize="14" fontWeight="700" letterSpacing="2">INDIRANAGAR</text>
              <text x="830" y="340" fill="#889A8D" fontSize="13" fontWeight="700" letterSpacing="2">WHITEFIELD</text>
              <text x="540" y="430" fill="#6A8070" fontSize="14" fontWeight="700" letterSpacing="2">KORAMANGALA</text>
              <text x="270" y="440" fill="#889A8D" fontSize="13" fontWeight="700" letterSpacing="2">JAYANAGAR</text>
            </svg>

            {/* Filtered Interactive Waste Markers */}
            {filteredMarkers.map((marker) => {
              const isSelected = activeMarker && activeMarker.id === marker.id;
              const severityClass = `marker-${marker.severity.toLowerCase()}`;

              return (
                <div key={marker.id}>
                  {/* Pin Button */}
                  <button
                    type="button"
                    className={`map-marker-pin ${severityClass} ${isSelected ? 'active' : ''}`}
                    style={{ left: `${marker.x}%`, top: `${marker.y}%` }}
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveMarker(marker);
                    }}
                    aria-label={`View ${marker.wasteType} at ${marker.location}`}
                  >
                    <div className="marker-bubble">
                      <div className="marker-bubble-inner">
                        <MapPin size={15} strokeWidth={2.5} />
                      </div>
                    </div>
                    <div className="marker-pulse" />
                  </button>

                  {/* Marker Popup Card */}
                  {isSelected && (
                    <div 
                      className="marker-popup"
                      style={{ left: `${marker.x}%`, top: `${marker.y}%` }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="popup-header">
                        <div className="popup-title">{marker.wasteType}</div>
                        <button 
                          type="button"
                          className="popup-close-btn"
                          onClick={() => setActiveMarker(null)}
                          aria-label="Close popup"
                        >
                          <X size={15} />
                        </button>
                      </div>

                      <div className="popup-row">
                        <MapPin size={14} className="text-sage-accent" />
                        <span style={{ fontWeight: 600 }}>{marker.location}</span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {renderSeverityTag(marker.severity)}
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                          {marker.severity} Severity
                        </span>
                      </div>

                      <div className="popup-footer">
                        <span style={{ color: 'var(--text-muted)' }}>
                          Reported: {marker.date}
                        </span>
                        {renderStatusBadge(marker.status)}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
            {/* Empty State: No matching map results */}
            {filteredMarkers.length === 0 && (
              <div 
                className="map-empty-state-overlay"
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  backgroundColor: 'rgba(255, 255, 255, 0.96)',
                  backdropFilter: 'blur(8px)',
                  padding: '1.75rem 2rem',
                  borderRadius: 'var(--radius-md)',
                  border: '1.5px solid var(--border-color)',
                  boxShadow: '0 8px 24px rgba(29, 41, 33, 0.1)',
                  textAlign: 'center',
                  maxWidth: '380px',
                  zIndex: 20
                }}
              >
                <div style={{ 
                  width: 44, 
                  height: 44, 
                  borderRadius: '50%', 
                  backgroundColor: 'var(--bg-sage-light)', 
                  color: 'var(--sage-700)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  margin: '0 auto 0.75rem auto' 
                }}>
                  <Filter size={20} />
                </div>
                <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                  No matching map results
                </div>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.1rem', lineHeight: 1.4 }}>
                  No waste locations match your selected filter criteria.
                </p>
                <button
                  type="button"
                  className="btn btn-primary"
                  style={{ fontSize: '0.85rem', padding: '0.5rem 1.1rem', margin: '0 auto' }}
                  onClick={handleResetFilters}
                >
                  <RotateCcw size={14} />
                  <span>Reset Filters</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Section 6: Active Waste Hotspots */}
        <div className="hotspots-section">
          <div className="hotspots-header">
            <h2 className="hotspots-title">Active Waste Hotspots</h2>
            <p className="subheading" style={{ fontSize: '1rem', marginTop: '0.2rem' }}>
              Neighborhoods with concentrated waste accumulation requiring priority attention.
            </p>
          </div>

          <div className="hotspots-grid">
            {hotspots.map((hs) => (
              <div key={hs.id} className="hotspot-card">
                <div className="hotspot-card-top">
                  <div className="hotspot-name">{hs.area}</div>
                  <span className="hotspot-report-count">{hs.reportsCount}</span>
                </div>

                <div className="hotspot-details">
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Type: </span>
                    <strong style={{ color: 'var(--text-primary)' }}>{hs.commonType}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Priority: </span>
                    <span style={{ fontWeight: 600 }}>{hs.severity}</span>
                  </div>
                </div>

                <div className="hotspot-footer">
                  {renderSeverityTag(hs.severityLevel)}
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--sage-700)' }}>
                    {hs.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

import React, { useState, useEffect } from 'react';
import { 
  Weight, 
  Recycle, 
  FileText, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  TrendingUp, 
  PieChart, 
  BarChart3, 
  Flame, 
  Map, 
  ArrowUpRight, 
  Sparkles,
  ChevronRight
} from 'lucide-react';
import { adminApi } from '../services/api';

export default function Dashboard({ reports = [], onNavigate }) {
  const [hoveredMonth, setHoveredMonth] = useState(null);
  const [backendStats, setBackendStats] = useState(null);

  useEffect(() => {
    adminApi.getCollectionStats()
      .then((data) => {
        if (data) setBackendStats(data);
      })
      .catch((err) => {
        console.warn('Failed to fetch dashboard stats from backend:', err);
      });
  }, []);

  // Derive dynamic stats reflecting backend stats when available, falling back to local reports state
  const totalReportsCount = backendStats 
    ? backendStats.total 
    : 320 + Math.max(0, reports.length - 3);

  const resolvedReportsCount = backendStats 
    ? backendStats.completed 
    : 284 + Math.max(0, reports.filter((r) => r.status === 'Resolved').length - 1);

  const pendingReportsCount = backendStats 
    ? (backendStats.submitted + backendStats.accepted + backendStats.scheduled + backendStats.collected) 
    : 36 + Math.max(0, reports.filter((r) => r.status === 'Pending' || r.status === 'In Progress').length - 2);

  const activeHotspotsCount = 18 + reports.filter((r) => r.severity === 'High' && r.status !== 'Resolved').length;

  const resolutionPct = totalReportsCount > 0 
    ? ((resolvedReportsCount / totalReportsCount) * 100).toFixed(1) 
    : '0.0';

  // 1. Top 6 Clean Statistics Cards (Live backend data + municipal indicators)
  const topStats = [
    {
      label: 'Total Waste Collected',
      value: '12,450 kg',
      icon: Weight,
      change: '+8.4% this month',
    },
    {
      label: 'Waste Recycled',
      value: '7,820 kg',
      icon: Recycle,
      change: '62.8% recovery',
    },
    {
      label: 'Total Reports',
      value: String(totalReportsCount),
      icon: FileText,
      change: backendStats ? `${backendStats.total} registered in system` : '+14 new',
    },
    {
      label: 'Reports Resolved',
      value: String(resolvedReportsCount),
      icon: CheckCircle2,
      change: `${resolutionPct}% resolution rate`,
    },
    {
      label: 'Pending Reports',
      value: String(pendingReportsCount),
      icon: Clock,
      change: backendStats ? `${backendStats.submitted} awaiting review` : 'Avg 4.2h response',
    },
    {
      label: 'Active Hotspots',
      value: String(activeHotspotsCount),
      icon: Flame,
      change: `${activeHotspotsCount} monitored`,
    },
  ];

  // Chart 1: 7 Months Trend Data
  const monthlyTrend = [
    { month: 'Mar', amount: 8200, label: '8,200 kg' },
    { month: 'Apr', amount: 9100, label: '9,100 kg' },
    { month: 'May', amount: 9800, label: '9,800 kg' },
    { month: 'Jun', amount: 10400, label: '10,400 kg' },
    { month: 'Jul', amount: 11200, label: '11,200 kg' },
    { month: 'Aug', amount: 11900, label: '11,900 kg' },
    { month: 'Sep', amount: 12450, label: '12,450 kg' },
  ];

  // Chart 2: Waste by Category
  const categories = [
    { name: 'Organic', percent: 35, color: '#55755C' },
    { name: 'Plastic', percent: 28, color: '#6E8B74' },
    { name: 'Paper', percent: 18, color: '#8FA895' },
    { name: 'Glass', percent: 10, color: '#AFC2B4' },
    { name: 'Metal', percent: 6, color: '#D6974B' },
    { name: 'E-waste', percent: 3, color: '#C55A52' },
  ];

  // Chart 3: Reports Status Data
  const inProgCount = 20;
  const pendingOnlyCount = Math.max(0, pendingReportsCount - inProgCount);
  const resolvedPct = ((resolvedReportsCount / totalReportsCount) * 100).toFixed(1);
  const inProgPct = ((inProgCount / totalReportsCount) * 100).toFixed(1);
  const pendingPct = (100 - parseFloat(resolvedPct) - parseFloat(inProgPct)).toFixed(1);

  const reportStatuses = [
    { name: 'Resolved', count: resolvedReportsCount, percent: `${resolvedPct}%`, color: '#55755C' },
    { name: 'In Progress', count: inProgCount, percent: `${inProgPct}%`, color: '#D6974B' },
    { name: 'Pending', count: pendingOnlyCount, percent: `${pendingPct}%`, color: '#A0B2A6' },
  ];

  // Chart 4: Waste by Area (Horizontal Bars)
  const areasData = [
    { area: 'Indiranagar', count: 78, max: 90 },
    { area: 'MG Road', count: 64, max: 90 },
    { area: 'Whitefield', count: 52, max: 90 },
    { area: 'Koramangala', count: 46, max: 90 },
    { area: 'Jayanagar', count: 38, max: 90 },
    { area: 'Peenya', count: 26, max: 90 },
  ];

  // Active Waste Hotspots Table
  const hotspotsData = [
    {
      area: 'Indiranagar',
      reports: 24,
      commonWaste: 'Plastic',
      severity: 'High',
      status: 'Attention Required',
    },
    {
      area: 'MG Road',
      reports: 18,
      commonWaste: 'Mixed Waste',
      severity: 'High',
      status: 'Attention Required',
    },
    {
      area: 'Whitefield',
      reports: 15,
      commonWaste: 'E-waste',
      severity: 'Medium',
      status: 'In Progress',
    },
    {
      area: 'Koramangala',
      reports: 9,
      commonWaste: 'Paper',
      severity: 'Low',
      status: 'Monitored',
    },
    {
      area: 'Peenya',
      reports: 7,
      commonWaste: 'Hazardous',
      severity: 'High',
      status: 'Dispatched',
    },
  ];

  const renderSeverityBadge = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return <span className="severity-tag severity-tag-high">High</span>;
      case 'medium':
        return <span className="severity-tag severity-tag-medium">Medium</span>;
      case 'low':
      default:
        return <span className="severity-tag severity-tag-low">Low</span>;
    }
  };

  const renderHotspotStatusBadge = (status) => {
    switch (status) {
      case 'Attention Required':
        return <span className="status-badge status-badge-pending" style={{ color: '#8A3333', backgroundColor: '#FBECEB', borderColor: '#EDCECE' }}>{status}</span>;
      case 'In Progress':
        return <span className="status-badge status-badge-in-progress">{status}</span>;
      case 'Dispatched':
        return <span className="status-badge status-badge-in-progress" style={{ color: '#2F5938', backgroundColor: '#EBF3ED' }}>{status}</span>;
      case 'Monitored':
      default:
        return <span className="status-badge status-badge-resolved">{status}</span>;
    }
  };

  // Helper calculation for Line Chart (monthly trend)
  const minAmount = 7000;
  const maxAmount = 13500;
  const chartW = 460;
  const chartH = 170;
  const points = monthlyTrend.map((m, idx) => {
    const x = 30 + idx * ((chartW - 60) / (monthlyTrend.length - 1));
    const y = chartH - 30 - ((m.amount - minAmount) / (maxAmount - minAmount)) * (chartH - 60);
    return { ...m, x, y };
  });

  const polylineStr = points.map((p) => `${p.x},${p.y}`).join(' ');
  const areaPolyStr = `${points[0].x},${chartH - 25} ${polylineStr} ${points[points.length - 1].x},${chartH - 25}`;

  // Helper calculation for Donut Chart
  let cumulativePercent = 0;
  const donutSegments = categories.map((cat) => {
    const startAngle = cumulativePercent * 3.6;
    cumulativePercent += cat.percent;
    const endAngle = cumulativePercent * 3.6;
    return { ...cat, startAngle, endAngle };
  });

  return (
    <section className="dashboard-section">
      <div className="container dashboard-container">
        {/* Page Header */}
        <div className="dashboard-header-wrapper">
          <div>
            <div className="badge-pill" style={{ marginBottom: '0.65rem' }}>
              <BarChart3 size={14} />
              <span>Municipal Command Center</span>
            </div>
            <h1 className="page-title">Dashboard</h1>
            <p className="subheading" style={{ marginTop: '0.25rem' }}>
              Overview of waste management activity and community reports.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500 }}>
              Showing Demo Sample Data
            </span>
            <button 
              className="btn btn-secondary"
              style={{ fontSize: '0.875rem', padding: '0.6rem 1.1rem' }}
              onClick={() => onNavigate('Waste Map')}
            >
              <Map size={16} className="text-sage-accent" />
              <span>View Map</span>
            </button>
          </div>
        </div>

        {/* 1. Six Top Statistics Cards */}
        <div className="dashboard-stats-grid">
          {topStats.map((stat, idx) => {
            const IconComp = stat.icon;
            return (
              <div key={idx} className="dash-stat-card">
                <div className="dash-stat-header">
                  <div className="dash-stat-icon">
                    <IconComp size={18} strokeWidth={2} />
                  </div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--sage-700)', fontWeight: 600, backgroundColor: 'var(--bg-sage-light)', padding: '0.15rem 0.45rem', borderRaduis: '4px' }}>
                    Sample
                  </span>
                </div>
                <div>
                  <div className="dash-stat-value">{stat.value}</div>
                  <div className="dash-stat-label">{stat.label}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* 2. Analytics Section (4 Charts Grid) */}
        <div className="analytics-grid">
          {/* Chart 1: Waste Collection Trend (Line Chart) */}
          <div className="chart-card">
            <div className="chart-header">
              <div className="chart-title">
                <TrendingUp size={18} className="text-sage-accent" />
                <span>Waste Collection Trend</span>
              </div>
              <span className="chart-badge">Last 7 Months</span>
            </div>

            <div className="chart-canvas-area" style={{ flexDirection: 'column' }}>
              <svg 
                viewBox={`0 0 ${chartW} ${chartH}`} 
                style={{ width: '100%', height: 'auto', overflow: 'visible' }}
              >
                <defs>
                  <linearGradient id="sageAreaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#55755C" stopOpacity="0.25" />
                    <stop offset="100%" stopColor="#55755C" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Horizontal Guide Grid Lines */}
                <line x1="20" y1="30" x2={chartW - 20} y2="30" stroke="#E6EEE7" strokeDasharray="3 3" />
                <line x1="20" y1="80" x2={chartW - 20} y2="80" stroke="#E6EEE7" strokeDasharray="3 3" />
                <line x1="20" y1="130" x2={chartW - 20} y2="130" stroke="#E6EEE7" strokeDasharray="3 3" />
                <line x1="20" y1={chartH - 25} x2={chartW - 20} y2={chartH - 25} stroke="#D0DCD2" />

                {/* Area Gradient Fill */}
                <polygon points={areaPolyStr} fill="url(#sageAreaGrad)" />

                {/* Main Trend Line */}
                <polyline 
                  points={polylineStr} 
                  fill="none" 
                  stroke="#55755C" 
                  strokeWidth="3" 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                />

                {/* Interactive Points and Labels */}
                {points.map((pt, i) => (
                  <g key={i} onMouseEnter={() => setHoveredMonth(pt)} onMouseLeave={() => setHoveredMonth(null)}>
                    <circle 
                      cx={pt.x} 
                      cy={pt.y} 
                      r={hoveredMonth?.month === pt.month ? 6 : 4} 
                      fill="#FFFFFF" 
                      stroke="#55755C" 
                      strokeWidth="2.5" 
                      style={{ cursor: 'pointer', transition: 'all 0.15s ease' }}
                    />
                    <text 
                      x={pt.x} 
                      y={chartH - 10} 
                      textAnchor="middle" 
                      fontSize="11" 
                      fill="#748579" 
                      fontWeight="600"
                    >
                      {pt.month}
                    </text>
                  </g>
                ))}
              </svg>

              {/* Tooltip Info */}
              <div style={{ marginTop: '0.4rem', fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                {hoveredMonth ? (
                  <span><strong>{hoveredMonth.month} 2026:</strong> {hoveredMonth.label} waste collected</span>
                ) : (
                  <span>Hover over points to inspect monthly collection totals</span>
                )}
              </div>
            </div>
          </div>

          {/* Chart 2: Waste by Category (Donut Chart) */}
          <div className="chart-card">
            <div className="chart-header">
              <div className="chart-title">
                <PieChart size={18} className="text-sage-accent" />
                <span>Waste by Category</span>
              </div>
              <span className="chart-badge">Composition %</span>
            </div>

            <div className="chart-canvas-area" style={{ flexDirection: 'column', gap: '1rem' }}>
              <div style={{ position: 'relative', width: 140, height: 140 }}>
                {/* SVG Donut Circle */}
                <svg viewBox="0 0 42 42" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                  <circle cx="21" cy="21" r="15.915" fill="none" stroke="#EAF0EB" strokeWidth="6" />
                  {categories.map((cat, idx) => {
                    const strokeDasharray = `${cat.percent} ${100 - cat.percent}`;
                    const offset = 100 - categories.slice(0, idx).reduce((acc, c) => acc + c.percent, 0);
                    return (
                      <circle
                        key={cat.name}
                        cx="21"
                        cy="21"
                        r="15.915"
                        fill="none"
                        stroke={cat.color}
                        strokeWidth="6"
                        strokeDasharray={strokeDasharray}
                        strokeDashoffset={offset}
                      />
                    );
                  })}
                </svg>
                {/* Donut Center Label */}
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Total</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>100%</div>
                </div>
              </div>

              {/* Donut Legend */}
              <div className="donut-legend" style={{ width: '100%' }}>
                {categories.map((c) => (
                  <div key={c.name} className="donut-legend-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <span className="legend-color-dot" style={{ backgroundColor: c.color }} />
                      <span style={{ color: 'var(--text-secondary)' }}>{c.name}</span>
                    </div>
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{c.percent}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Chart 3: Reports Status */}
          <div className="chart-card">
            <div className="chart-header">
              <div className="chart-title">
                <CheckCircle2 size={18} className="text-sage-accent" />
                <span>Reports Status</span>
              </div>
              <span className="chart-badge">{totalReportsCount} Total Filed</span>
            </div>

            <div className="status-breakdown-list">
              {/* Segmented Bar */}
              <div style={{ display: 'flex', width: '100%', height: 14, borderRadius: 9999, overflow: 'hidden', border: '1px solid var(--border-color)' }}>
                <div style={{ width: `${resolvedPct}%`, backgroundColor: '#55755C' }} title={`Resolved: ${resolvedPct}%`} />
                <div style={{ width: `${inProgPct}%`, backgroundColor: '#D6974B' }} title={`In Progress: ${inProgPct}%`} />
                <div style={{ width: `${pendingPct}%`, backgroundColor: '#A0B2A6' }} title={`Pending: ${pendingPct}%`} />
              </div>

              {/* Status Items Breakdown */}
              {reportStatuses.map((st) => (
                <div key={st.name} className="status-stat-item">
                  <div className="status-stat-label">
                    <span className="legend-color-dot" style={{ backgroundColor: st.color, width: 11, height: 11 }} />
                    <span>{st.name}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <span style={{ fontSize: '0.825rem', color: 'var(--text-muted)', fontWeight: 600 }}>{st.percent}</span>
                    <span className="status-stat-count">{st.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chart 4: Waste by Area (Horizontal Bar Chart) */}
          <div className="chart-card">
            <div className="chart-header">
              <div className="chart-title">
                <BarChart3 size={18} className="text-sage-accent" />
                <span>Waste by Area</span>
              </div>
              <span className="chart-badge">Top 6 Neighborhoods</span>
            </div>

            <div className="bar-chart-list">
              {areasData.map((item) => (
                <div key={item.area} className="bar-item">
                  <div className="bar-label-row">
                    <span>{item.area}</span>
                    <span>{item.count} Reports</span>
                  </div>
                  <div className="bar-track">
                    <div 
                      className="bar-fill" 
                      style={{ width: `${(item.count / item.max) * 100}%` }} 
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 3. Below Charts: Active Waste Hotspots Section */}
        <div className="dash-hotspots-section">
          <div className="dash-hotspots-header">
            <div>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                Active Waste Hotspots
              </h2>
              <p className="subheading" style={{ fontSize: '0.925rem', marginTop: '0.2rem' }}>
                Locations requiring immediate cleanup dispatch or ongoing surveillance.
              </p>
            </div>

            <button 
              className="btn btn-primary"
              style={{ fontSize: '0.875rem', padding: '0.65rem 1.25rem' }}
              onClick={() => onNavigate('Waste Map')}
            >
              <Map size={16} />
              <span>View Map</span>
            </button>
          </div>

          {/* Desktop Hotspots Table */}
          <div className="reports-table-responsive">
            <table className="reports-table">
              <thead>
                <tr>
                  <th>Area</th>
                  <th>Reports</th>
                  <th>Most Common Waste</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {hotspotsData.map((row) => (
                  <tr key={row.area} className="clickable-row" onClick={() => onNavigate('Waste Map')}>
                    <td style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                      {row.area}
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: 'var(--sage-800)' }}>{row.reports}</span>
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>
                      {row.commonWaste}
                    </td>
                    <td>
                      {renderSeverityBadge(row.severity)}
                    </td>
                    <td>
                      {renderHotspotStatusBadge(row.status)}
                    </td>
                    <td>
                      <button 
                        type="button" 
                        style={{ color: 'var(--sage-700)', display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.825rem', fontWeight: 600 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onNavigate('Waste Map');
                        }}
                      >
                        <span>Inspect on Map</span>
                        <ArrowUpRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}

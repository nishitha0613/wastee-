import React, { useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  PieChart, 
  Clock, 
  CheckCircle2, 
  MapPin, 
  ArrowUpRight, 
  Sparkles,
  Calendar,
  Layers,
  Zap,
  Leaf
} from 'lucide-react';

export default function Analytics({ reports = [], onNavigate }) {
  const [timeframe, setTimeframe] = useState('6m');
  const [hoveredMonth, setHoveredMonth] = useState(null);

  const totalReportsCount = 320 + Math.max(0, reports.length - 3);
  const resolvedReportsCount = 284 + Math.max(0, reports.filter((r) => r.status === 'Resolved').length - 1);
  const resolutionRate = ((resolvedReportsCount / totalReportsCount) * 100).toFixed(1);

  const kpis = [
    {
      title: 'Total Managed Volume',
      value: '12,450 kg',
      trend: '+8.4% vs last period',
      icon: Layers,
      trendPositive: true
    },
    {
      title: 'Recycling Recovery Rate',
      value: '62.8%',
      trend: '+4.5% efficiency',
      icon: Leaf,
      trendPositive: true
    },
    {
      title: 'Mean Resolution Time',
      value: '4.2 hrs',
      trend: '-1.1 hrs faster turnaround',
      icon: Clock,
      trendPositive: true
    },
    {
      title: 'Overall Clearance Rate',
      value: `${resolutionRate}%`,
      trend: `${resolvedReportsCount} of ${totalReportsCount} cases`,
      icon: CheckCircle2,
      trendPositive: true
    },
  ];

  const monthlyTrend = [
    { month: 'Mar', amount: 8200, target: 8000, label: '8,200 kg' },
    { month: 'Apr', amount: 9100, target: 8500, label: '9,100 kg' },
    { month: 'May', amount: 9800, target: 9200, label: '9,800 kg' },
    { month: 'Jun', amount: 10400, target: 9900, label: '10,400 kg' },
    { month: 'Jul', amount: 11200, target: 10600, label: '11,200 kg' },
    { month: 'Aug', amount: 11900, target: 11200, label: '11,900 kg' },
    { month: 'Sep', amount: 12450, target: 11800, label: '12,450 kg' },
  ];

  const categories = [
    { name: 'Organic', percent: 35, weight: '4,357 kg', color: '#55755C' },
    { name: 'Plastic', percent: 28, weight: '3,486 kg', color: '#6E8B74' },
    { name: 'Paper', percent: 18, weight: '2,241 kg', color: '#8FA895' },
    { name: 'Glass', percent: 10, weight: '1,245 kg', color: '#AFC2B4' },
    { name: 'Metal', percent: 6, weight: '747 kg', color: '#D6974B' },
    { name: 'E-waste', percent: 3, weight: '374 kg', color: '#C55A52' },
  ];

  const districtData = [
    { area: 'Indiranagar', resolved: 72, pending: 6, rate: '92.3%' },
    { area: 'MG Road', resolved: 58, pending: 6, rate: '90.6%' },
    { area: 'Whitefield', resolved: 44, pending: 8, rate: '84.6%' },
    { area: 'Koramangala', resolved: 42, pending: 4, rate: '91.3%' },
    { area: 'Jayanagar', resolved: 36, pending: 2, rate: '94.7%' },
    { area: 'Peenya', resolved: 21, pending: 5, rate: '80.8%' },
  ];

  const chartW = 540;
  const chartH = 190;
  const minAmount = 7000;
  const maxAmount = 13500;

  const points = monthlyTrend.map((m, idx) => {
    const x = 35 + idx * ((chartW - 70) / (monthlyTrend.length - 1));
    const y = chartH - 35 - ((m.amount - minAmount) / (maxAmount - minAmount)) * (chartH - 70);
    const yTarget = chartH - 35 - ((m.target - minAmount) / (maxAmount - minAmount)) * (chartH - 70);
    return { ...m, x, y, yTarget };
  });

  const polylineStr = points.map((p) => `${p.x},${p.y}`).join(' ');
  const targetPolylineStr = points.map((p) => `${p.x},${p.yTarget}`).join(' ');
  const areaPolyStr = `${points[0].x},${chartH - 30} ${polylineStr} ${points[points.length - 1].x},${chartH - 30}`;

  return (
    <section className="dashboard-section" style={{ minHeight: '85vh', paddingBottom: '4rem' }}>
      <div className="container dashboard-container">
        {/* Header */}
        <div className="dashboard-header-wrapper">
          <div>
            <div className="badge-pill" style={{ marginBottom: '0.65rem' }}>
              <BarChart3 size={14} />
              <span>Municipal Intelligence</span>
            </div>
            <h1 className="page-title">Analytics</h1>
            <p className="subheading" style={{ marginTop: '0.25rem' }}>
              Deep-dive metrics, material recovery efficiency, and neighborhood resolution dynamics.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginRight: '0.5rem' }}>Timeframe:</span>
            {[
              { label: '30 Days', id: '30d' },
              { label: '6 Months', id: '6m' },
              { label: '1 Year', id: '1y' },
            ].map((tf) => (
              <button
                key={tf.id}
                type="button"
                className={`btn ${timeframe === tf.id ? 'btn-primary' : 'btn-outline'}`}
                style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
                onClick={() => setTimeframe(tf.id)}
              >
                {tf.label}
              </button>
            ))}
          </div>
        </div>

        {/* 4 KPI Cards */}
        <div className="dashboard-stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))' }}>
          {kpis.map((kpi, idx) => {
            const IconComp = kpi.icon;
            return (
              <div key={idx} className="dash-stat-card">
                <div className="dash-stat-header">
                  <div className="dash-stat-icon">
                    <IconComp size={18} strokeWidth={2} />
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--sage-700)', fontWeight: 600 }}>
                    {kpi.trend}
                  </span>
                </div>
                <div>
                  <div className="dash-stat-value">{kpi.value}</div>
                  <div className="dash-stat-label">{kpi.title}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Charts Grid */}
        <div className="analytics-grid" style={{ marginTop: '2rem' }}>
          {/* Chart 1: Collection Volume Trend vs Target */}
          <div className="chart-card">
            <div className="chart-header">
              <div className="chart-title">
                <TrendingUp size={18} className="text-sage-accent" />
                <span>Monthly Volume vs Targeted Baseline</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.78rem' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', color: 'var(--sage-800)', fontWeight: 600 }}>
                  <span style={{ width: 10, height: 3, backgroundColor: 'var(--sage-700)', borderRadius: 2 }} /> Actual
                </span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', color: 'var(--text-muted)' }}>
                  <span style={{ width: 10, height: 2, borderTop: '2px dashed #99AB9F' }} /> Target
                </span>
              </div>
            </div>

            <div className="chart-canvas-area" style={{ flexDirection: 'column' }}>
              <svg viewBox={`0 0 ${chartW} ${chartH}`} style={{ width: '100%', height: 'auto', overflow: 'visible' }}>
                <defs>
                  <linearGradient id="analyticsAreaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#55755C" stopOpacity="0.25" />
                    <stop offset="100%" stopColor="#55755C" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Grid guidelines */}
                <line x1="20" y1="35" x2={chartW - 20} y2="35" stroke="#E6EEE7" strokeDasharray="3 3" />
                <line x1="20" y1="85" x2={chartW - 20} y2="85" stroke="#E6EEE7" strokeDasharray="3 3" />
                <line x1="20" y1="135" x2={chartW - 20} y2="135" stroke="#E6EEE7" strokeDasharray="3 3" />
                <line x1="20" y1={chartH - 30} x2={chartW - 20} y2={chartH - 30} stroke="#D0DCD2" />

                {/* Shaded Area */}
                <polygon points={areaPolyStr} fill="url(#analyticsAreaGrad)" />

                {/* Target Baseline (Dashed) */}
                <polyline points={targetPolylineStr} fill="none" stroke="#99AB9F" strokeWidth="2" strokeDasharray="4 4" />

                {/* Actual Collection Line */}
                <polyline points={polylineStr} fill="none" stroke="#55755C" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" />

                {/* Points */}
                {points.map((pt, i) => (
                  <g key={i} onMouseEnter={() => setHoveredMonth(pt)} onMouseLeave={() => setHoveredMonth(null)}>
                    <circle 
                      cx={pt.x} 
                      cy={pt.y} 
                      r={hoveredMonth?.month === pt.month ? 6.5 : 4} 
                      fill="#FFFFFF" 
                      stroke="#55755C" 
                      strokeWidth="2.5" 
                      style={{ cursor: 'pointer', transition: 'all 0.15s ease' }}
                    />
                    <text x={pt.x} y={chartH - 12} textAnchor="middle" fontSize="11" fill="#748579" fontWeight="600">
                      {pt.month}
                    </text>
                  </g>
                ))}
              </svg>

              <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                {hoveredMonth ? (
                  <span><strong>{hoveredMonth.month} 2026:</strong> {hoveredMonth.label} collected (Target: {hoveredMonth.target.toLocaleString()} kg)</span>
                ) : (
                  <span>Hover data points to inspect recorded collections vs municipal benchmarks</span>
                )}
              </div>
            </div>
          </div>

          {/* Chart 2: Material Stream Composition */}
          <div className="chart-card">
            <div className="chart-header">
              <div className="chart-title">
                <PieChart size={18} className="text-sage-accent" />
                <span>Material Stream Composition</span>
              </div>
              <span className="chart-badge">12,450 kg Total</span>
            </div>

            <div className="chart-canvas-area" style={{ flexDirection: 'column', gap: '1rem' }}>
              <div style={{ position: 'relative', width: 140, height: 140 }}>
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
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>6 Streams</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>100%</div>
                </div>
              </div>

              <div className="donut-legend" style={{ width: '100%' }}>
                {categories.map((c) => (
                  <div key={c.name} className="donut-legend-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <span className="legend-color-dot" style={{ backgroundColor: c.color }} />
                      <span style={{ color: 'var(--text-secondary)' }}>{c.name}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{c.weight}</span>
                      <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{c.percent}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Neighborhood Efficiency Comparison Table & Resolution Performance */}
        <div className="dash-hotspots-section" style={{ marginTop: '2rem' }}>
          <div className="dash-hotspots-header">
            <div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                District Resolution Performance
              </h2>
              <p className="subheading" style={{ fontSize: '0.9rem', marginTop: '0.15rem' }}>
                Municipal cleanup turnaround across 6 primary city zones.
              </p>
            </div>

            <button 
              className="btn btn-secondary"
              style={{ fontSize: '0.85rem' }}
              onClick={() => onNavigate('Waste Map')}
            >
              <MapPin size={15} className="text-sage-accent" />
              <span>Inspect on Hotspot Map</span>
            </button>
          </div>

          <div className="reports-table-responsive">
            <table className="reports-table">
              <thead>
                <tr>
                  <th>District Zone</th>
                  <th>Resolved Cases</th>
                  <th>Pending Actions</th>
                  <th>Resolution Progress</th>
                  <th style={{ textAlign: 'right' }}>Efficiency Score</th>
                </tr>
              </thead>
              <tbody>
                {districtData.map((d) => {
                  const total = d.resolved + d.pending;
                  const pct = Math.round((d.resolved / total) * 100);
                  return (
                    <tr key={d.area}>
                      <td style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{d.area}</td>
                      <td style={{ color: 'var(--sage-800)', fontWeight: 600 }}>{d.resolved}</td>
                      <td style={{ color: d.pending > 5 ? '#A04040' : 'var(--text-muted)', fontWeight: 600 }}>{d.pending}</td>
                      <td style={{ width: '40%' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div style={{ flex: 1, height: 8, borderRadius: 9999, backgroundColor: 'var(--bg-sage-light)', border: '1px solid var(--border-color)', overflow: 'hidden' }}>
                            <div style={{ width: `${pct}%`, height: '100%', backgroundColor: 'var(--sage-600)' }} />
                          </div>
                          <span style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', fontWeight: 600, minWidth: '40px' }}>
                            {pct}%
                          </span>
                        </div>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 700, color: 'var(--sage-900)' }}>
                        {d.rate}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}

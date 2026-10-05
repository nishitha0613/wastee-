import React from 'react';
import { 
  Leaf, 
  Trees, 
  Zap, 
  Droplets, 
  Wind, 
  Globe2, 
  Award, 
  CheckCircle2, 
  ArrowUpRight,
  Sparkles,
  BarChart3,
  Flame,
  Recycle
} from 'lucide-react';

export default function EnvironmentalImpact({ onNavigate }) {
  const impactStats = [
    {
      title: 'CO₂ Emissions Prevented',
      value: '18.6 Tons',
      subtext: 'Equal to 4 passenger cars off road for 1 yr',
      icon: Wind,
      color: 'var(--sage-700)',
      bg: 'var(--bg-sage-light)'
    },
    {
      title: 'Mature Trees Preserved',
      value: '312 Trees',
      subtext: 'Through paper recycling & urban wood diversion',
      icon: Trees,
      color: 'var(--sage-800)',
      bg: 'var(--bg-sage-light)'
    },
    {
      title: 'Landfill Space Diverted',
      value: '42.8 m³',
      subtext: 'Compressed volume prevented from landfills',
      icon: Recycle,
      color: '#496B50',
      bg: 'var(--bg-sage-light)'
    },
    {
      title: 'Clean Energy Conserved',
      value: '38,400 kWh',
      subtext: 'Powers 35 residential homes for a month',
      icon: Zap,
      color: '#B27B2B',
      bg: '#FAF4E8'
    },
    {
      title: 'Water Conserved',
      value: '145,000 L',
      subtext: 'Savings through closed-loop recycling loops',
      icon: Droplets,
      color: '#326789',
      bg: '#EDF5FB'
    },
    {
      title: 'Recycling Recovery Rate',
      value: '62.8%',
      subtext: '+4.5% above state municipal standards',
      icon: Award,
      color: 'var(--sage-900)',
      bg: 'var(--bg-sage-light)'
    }
  ];

  const materialImpacts = [
    {
      material: 'Plastics & Polymers',
      collected: '3,486 kg',
      co2Saved: '5.2 Tons CO₂',
      benefit: 'Prevented 140,000 single-use bottles from contaminating storm drains and rivers.',
      icon: Sparkles
    },
    {
      material: 'Organic & Green Waste',
      collected: '4,357 kg',
      co2Saved: '6.8 Tons CO₂e',
      benefit: 'Diverted to municipal aerobic composting, generating 1.8 tons of nutrient-rich soil enricher.',
      icon: Leaf
    },
    {
      material: 'Paper & Cardboard',
      collected: '2,241 kg',
      co2Saved: '3.6 Tons CO₂',
      benefit: 'Spared 38 mature pine trees and conserved 58,000 liters of industrial pulping water.',
      icon: Trees
    },
    {
      material: 'Glass & Recyclable Metals',
      collected: '1,992 kg',
      co2Saved: '2.4 Tons CO₂',
      benefit: '100% infinitely recyclable material streams with near-zero degradation loss.',
      icon: Recycle
    },
    {
      material: 'Electronic Waste',
      collected: '374 kg',
      co2Saved: '0.6 Tons CO₂',
      benefit: 'Neutralized toxic cadmium, lead, and recovered precious copper and rare-earth elements safely.',
      icon: Zap
    }
  ];

  const municipalGoals = [
    { name: 'City Zero-Landfill Target', current: 78, target: 85, deadline: 'Q4 2026' },
    { name: 'Commercial Organic Waste Composting', current: 92, target: 90, deadline: 'Achieved' },
    { name: 'Hazardous & E-waste Safe Neutralization', current: 84, target: 95, deadline: 'Q2 2027' },
    { name: 'Neighborhood Hotspot Remediation Speed', current: 88, target: 90, deadline: 'Q3 2026' }
  ];

  return (
    <section className="dashboard-section" style={{ minHeight: '85vh', paddingBottom: '4rem' }}>
      <div className="container dashboard-container">
        {/* Header */}
        <div className="dashboard-header-wrapper">
          <div>
            <div className="badge-pill" style={{ marginBottom: '0.65rem' }}>
              <Globe2 size={14} />
              <span>Ecological Sustainability Index</span>
            </div>
            <h1 className="page-title">Environmental Impact</h1>
            <p className="subheading" style={{ marginTop: '0.25rem' }}>
              Quantifying greenhouse emissions prevented, natural resources saved, and ecological restoration.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <button 
              className="btn btn-secondary"
              style={{ fontSize: '0.85rem' }}
              onClick={() => onNavigate('Analytics')}
            >
              <BarChart3 size={15} className="text-sage-accent" />
              <span>View Analytics</span>
            </button>
          </div>
        </div>

        {/* 6 Top Environmental Impact Cards */}
        <div className="dashboard-stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
          {impactStats.map((item, idx) => {
            const IconComp = item.icon;
            return (
              <div key={idx} className="dash-stat-card" style={{ padding: '1.4rem' }}>
                <div className="dash-stat-header">
                  <div className="dash-stat-icon" style={{ backgroundColor: item.bg, color: item.color }}>
                    <IconComp size={20} strokeWidth={2.2} />
                  </div>
                  <span className="badge-pill" style={{ fontSize: '0.725rem', padding: '0.15rem 0.5rem', color: item.color, borderColor: 'var(--border-color)' }}>
                    Verified Ecological Impact
                  </span>
                </div>
                <div style={{ marginTop: '0.75rem' }}>
                  <div className="dash-stat-value" style={{ fontSize: '1.85rem' }}>{item.value}</div>
                  <div className="dash-stat-label" style={{ fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.2rem' }}>{item.title}</div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.35rem', lineHeight: 1.4 }}>
                    {item.subtext}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Material Stream Breakdown Section */}
        <div style={{ marginTop: '2.5rem' }}>
          <div style={{ marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Ecological Dividend by Waste Stream
            </h2>
            <p className="subheading" style={{ fontSize: '0.925rem', marginTop: '0.2rem' }}>
              Resource lifecycle offsets achieved through municipal sorting and certified recycling facilities.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {materialImpacts.map((m) => {
              const IconComp = m.icon;
              return (
                <div 
                  key={m.material} 
                  style={{
                    backgroundColor: 'var(--bg-card)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    padding: '1.35rem',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    boxShadow: 'var(--shadow-sm)'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <div style={{ width: 34, height: 34, borderRadius: 8, backgroundColor: 'var(--bg-sage-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--sage-700)' }}>
                          <IconComp size={18} />
                        </div>
                        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                          {m.material}
                        </h3>
                      </div>
                      <span className="badge-pill" style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--sage-800)' }}>
                        {m.co2Saved}
                      </span>
                    </div>

                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.65rem' }}>
                      Recovered: <strong>{m.collected}</strong>
                    </div>

                    <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                      {m.benefit}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 2026 Municipal Sustainability Benchmarks */}
        <div className="dash-hotspots-section" style={{ marginTop: '2.5rem' }}>
          <div className="dash-hotspots-header">
            <div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                2026 Municipal Sustainability Benchmarks
              </h2>
              <p className="subheading" style={{ fontSize: '0.9rem', marginTop: '0.15rem' }}>
                Key sustainability metrics audited against national clean-city benchmarks.
              </p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
            {municipalGoals.map((g) => (
              <div 
                key={g.name}
                style={{
                  backgroundColor: 'var(--bg-card)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color)',
                  padding: '1.25rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                    {g.name}
                  </span>
                  <span style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem', borderRadius: 4, backgroundColor: 'var(--bg-sage-light)', color: 'var(--sage-800)', fontWeight: 600 }}>
                    {g.deadline}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', margin: '0.75rem 0 0.35rem 0', fontSize: '0.85rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Current: <strong>{g.current}%</strong></span>
                  <span style={{ color: 'var(--text-muted)' }}>Target: {g.target}%</span>
                </div>

                <div style={{ height: 8, borderRadius: 9999, backgroundColor: 'var(--bg-sage-light)', border: '1px solid var(--border-color)', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      width: `${Math.min(100, (g.current / g.target) * 100)}%`, 
                      height: '100%', 
                      backgroundColor: g.current >= g.target ? 'var(--sage-600)' : 'var(--sage-700)' 
                    }} 
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

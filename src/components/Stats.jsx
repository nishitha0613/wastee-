import React from 'react';
import { Weight, Recycle, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function Stats({ 
  wasteCollected = 0, 
  recycled = 0, 
  resolvedCount = 0, 
  activeCount = 0 
}) {
  const statItems = [
    {
      id: 1,
      value: `${wasteCollected} kg`,
      label: 'Waste Collected',
      icon: Weight,
      badge: `${wasteCollected} kg Collected`,
    },
    {
      id: 2,
      value: `${recycled} kg`,
      label: 'Recycled',
      icon: Recycle,
      badge: `${recycled} kg Recycled`,
    },
    {
      id: 3,
      value: `${resolvedCount}`,
      label: 'Reports Resolved',
      icon: CheckCircle2,
      badge: `${resolvedCount} Resolved`,
    },
    {
      id: 4,
      value: `${activeCount}`,
      label: 'Active Hotspots',
      icon: AlertTriangle,
      badge: `${activeCount} Active`,
    },
  ];

  return (
    <section className="stats-section" aria-label="Community Statistics">
      <div className="container">
        <div className="stats-grid">
          {statItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <div key={item.id} className="stat-card">
                <div className="stat-header">
                  <div className="stat-icon">
                    <IconComponent size={22} strokeWidth={2} />
                  </div>
                  <span className="stat-badge">{item.badge}</span>
                </div>
                <div>
                  <div className="stat-value">{item.value}</div>
                  <div className="stat-label">{item.label}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

import React from 'react';
import { Scan, AlertCircle, LineChart, ArrowRight } from 'lucide-react';

export default function HowItWorks({ onAction, currentRole }) {
  const isUser = currentRole === 'user';

  const steps = [
    {
      stepNumber: '01',
      title: 'Scan',
      icon: Scan,
      description: 'Point your camera at any waste item. Our AI instantly classifies materials and guides you on proper disposal and recycling steps.',
      actionText: 'Try Waste Scanner',
      target: 'Waste Scanner',
    },
    {
      stepNumber: '02',
      title: 'Report',
      icon: AlertCircle,
      description: 'Notice uncollected trash or illegal dumping? Snap a quick photo with auto-tagged GPS location to notify municipal cleanup teams.',
      actionText: 'Report a Location',
      target: 'Report Waste',
    },
    {
      stepNumber: '03',
      title: 'Track',
      icon: LineChart,
      description: isUser 
        ? 'Follow the progress of your submitted waste reports in real time as municipal cleanup crews resolve each issue.'
        : 'Follow report updates in real time. Watch community stats grow as waste is successfully collected, sorted, and recycled.',
      actionText: isUser ? 'View My Reports' : 'View Live Dashboard',
      target: isUser ? 'My Reports' : 'Dashboard',
    },
  ];

  return (
    <section className="how-it-works-section container">
      <div className="section-header">
        <div className="badge-pill">Simple 3-Step Process</div>
        <h2 className="section-title">How EcoCycle Works</h2>
        <p className="subheading">
          Empowering citizens and local teams to collaborate seamlessly for cleaner streets and sustainable recycling.
        </p>
      </div>

      <div className="steps-grid">
        {steps.map((step) => {
          const StepIcon = step.icon;
          return (
            <div key={step.stepNumber} className="step-card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div className="step-icon-area">
                  <StepIcon size={24} strokeWidth={2} />
                </div>
                <div className="step-number-tag">{step.stepNumber}</div>
              </div>

              <div>
                <h3 className="step-title" style={{ marginBottom: '0.5rem' }}>{step.title}</h3>
                <p className="step-description">{step.description}</p>
              </div>

              <div style={{ marginTop: 'auto', paddingTop: '0.75rem' }}>
                <button 
                  className="btn btn-outline" 
                  style={{ width: '100%', fontSize: '0.875rem' }}
                  onClick={() => onAction(step.target)}
                >
                  <span>{step.actionText}</span>
                  <ArrowRight size={15} />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modern Call To Action Banner */}
      <div className="cta-banner">
        <div className="cta-banner-content">
          <h3 className="cta-title">Ready to clean up your neighborhood?</h3>
          <p className="cta-text">
            Join thousands of active community members using EcoCycle to build greener, cleaner cities together.
          </p>
          <button 
            className="btn btn-cta"
            onClick={() => onAction('Get Started')}
          >
            Get Started Now
            <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </section>
  );
}

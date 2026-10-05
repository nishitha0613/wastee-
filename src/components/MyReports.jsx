import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  CheckCircle2, 
  Clock, 
  Plus, 
  MapPin, 
  Calendar, 
  ChevronRight, 
  X, 
  ArrowRight, 
  Inbox,
  Sparkles,
  AlertCircle,
  Trash2,
  RefreshCw,
  Camera
} from 'lucide-react';
import { collectionApi, wasteApi, getImageUrl } from '../services/api';

export default function MyReports({ 
  onNavigate, 
  currentRole
}) {
  const [activeTab, setActiveTab] = useState('collections'); // 'collections' | 'scans'
  const [collectionRequests, setCollectionRequests] = useState([]);
  const [wasteReports, setWasteReports] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState(null);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [colRes, wasteRes] = await Promise.all([
        collectionApi.getAll().catch((err) => {
          console.warn('Failed to load collections:', err);
          return [];
        }),
        wasteApi.getReports().catch((err) => {
          console.warn('Failed to load waste reports:', err);
          return [];
        }),
      ]);

      setCollectionRequests(Array.isArray(colRes) ? colRes : (colRes?.items || []));
      setWasteReports(Array.isArray(wasteRes) ? wasteRes : (wasteRes?.items || []));
    } catch (err) {
      setError(err.message || 'Failed to load reports from server.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Map wasteReport image lookup by ID
  const wasteReportMap = React.useMemo(() => {
    const map = {};
    wasteReports.forEach((wr) => {
      map[wr.id] = wr;
    });
    return map;
  }, [wasteReports]);

  // Map backend collection requests to UI model
  const mappedCollections = React.useMemo(() => {
    return collectionRequests.map((req) => {
      const linkedReport = req.waste_report_id ? wasteReportMap[req.waste_report_id] : null;
      const stageMap = {
        submitted: 1,
        accepted: 2,
        scheduled: 3,
        collected: 4,
        completed: 5,
        rejected: 0,
      };

      return {
        id: `CR-${req.id}`,
        dbId: req.id,
        waste_report_id: req.waste_report_id,
        wasteType: req.waste_type || (linkedReport ? linkedReport.waste_type : 'General Waste'),
        location: req.location,
        date: new Date(req.requested_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
        scheduledDate: req.scheduled_date ? new Date(req.scheduled_date).toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : null,
        completedAt: req.completed_at ? new Date(req.completed_at).toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : null,
        status: req.status,
        rawStatus: req.status,
        severity: req.quantity?.includes('High') ? 'High' : req.quantity?.includes('Low') ? 'Low' : 'Medium',
        image: linkedReport?.image_path ? getImageUrl(linkedReport.image_path) : null,
        description: req.additional_notes || (linkedReport?.description) || 'No additional notes provided.',
        currentStage: stageMap[req.status] || 1,
        isCollection: true,
      };
    });
  }, [collectionRequests, wasteReportMap]);

  // Map backend waste reports to UI model
  const mappedWasteReports = React.useMemo(() => {
    return wasteReports.map((wr) => {
      return {
        id: `WR-${wr.id}`,
        dbId: wr.id,
        wasteType: wr.waste_type,
        location: 'Identified via AI Scanner',
        date: new Date(wr.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
        confidence: Math.round((wr.confidence || 0.9) * 100),
        status: 'Identified',
        rawStatus: 'identified',
        severity: 'Medium',
        image: wr.image_path ? getImageUrl(wr.image_path) : null,
        description: wr.description || 'AI-identified waste item.',
        disposal_guidance: wr.disposal_guidance,
        currentStage: 1,
        isWasteReport: true,
      };
    });
  }, [wasteReports]);

  const activeItems = activeTab === 'collections' ? mappedCollections : mappedWasteReports;

  // Stats calculation
  const totalCollections = mappedCollections.length;
  const completedCollections = mappedCollections.filter((r) => r.rawStatus === 'completed').length;
  const pendingCollections = mappedCollections.filter((r) => ['submitted', 'accepted', 'scheduled', 'collected'].includes(r.rawStatus)).length;

  const stats = [
    { label: 'Collection Requests', value: totalCollections, icon: FileText },
    { label: 'Completed Cleanups', value: completedCollections, icon: CheckCircle2 },
    { label: 'In Progress / Pending', value: pendingCollections, icon: Clock },
  ];

  const renderStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'resolved':
        return <span className="status-badge status-badge-resolved">Completed</span>;
      case 'accepted':
        return <span className="status-badge status-badge-in-progress">Accepted</span>;
      case 'scheduled':
        return <span className="status-badge status-badge-in-progress" style={{ backgroundColor: '#EBF3ED', color: '#2F5938' }}>Scheduled</span>;
      case 'collected':
        return <span className="status-badge status-badge-in-progress" style={{ backgroundColor: '#FDF3E7', color: '#9B7126' }}>Collected</span>;
      case 'rejected':
        return <span className="status-badge status-badge-pending" style={{ backgroundColor: '#FBECEB', color: '#8A3333', borderColor: '#EDCECE' }}>Rejected</span>;
      case 'identified':
        return <span className="status-badge status-badge-in-progress" style={{ backgroundColor: '#F0F6F1', color: '#386343' }}>AI Identified</span>;
      case 'submitted':
      case 'pending':
      default:
        return <span className="status-badge status-badge-pending">Submitted</span>;
    }
  };

  const renderSeverityTag = (severity = 'Low') => {
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

  const progressSteps = ['Submitted', 'Accepted', 'Scheduled', 'Collected', 'Completed'];

  const handleCancelRequest = async (requestId) => {
    if (!window.confirm('Are you sure you want to cancel this collection request?')) return;
    setActionLoading(true);
    try {
      await collectionApi.cancel(requestId);
      setActionMessage('Collection request cancelled successfully.');
      setSelectedReport(null);
      await fetchData();
      setTimeout(() => setActionMessage(null), 4000);
    } catch (err) {
      alert(err.message || 'Failed to cancel collection request.');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <section className="my-reports-section">
      <div className="container my-reports-container">
        {/* Header with Title and "Report New Waste" CTA */}
        <div className="my-reports-header-wrapper">
          <div>
            <div className="badge-pill" style={{ marginBottom: '0.65rem' }}>
              <FileText size={14} />
              <span>Citizen Tracking Portal</span>
            </div>
            <h1 className="page-title">My Reports</h1>
            <p className="subheading" style={{ marginTop: '0.25rem' }}>
              Track your waste collection requests and AI identification history.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.85rem', padding: '0.55rem 0.9rem' }}
              onClick={fetchData}
              disabled={isLoading}
              title="Refresh reports"
            >
              <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
              <span>Refresh</span>
            </button>
            <button 
              className="btn btn-primary"
              onClick={() => onNavigate('Report Waste')}
            >
              <Plus size={18} />
              <span>Request Collection</span>
            </button>
          </div>
        </div>

        {/* 3 Top Statistics Cards */}
        <div className="reports-stats-grid">
          {stats.map((st, idx) => {
            const IconComp = st.icon;
            return (
              <div key={idx} className="report-stat-card">
                <div className="report-stat-icon-wrap">
                  <IconComp size={22} strokeWidth={2} />
                </div>
                <div>
                  <div className="report-stat-number">{st.value}</div>
                  <div className="report-stat-title">{st.label}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* View Switcher Tabs */}
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          margin: '1.5rem 0 1rem 0',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '0.5rem'
        }}>
          <button
            type="button"
            className={`btn ${activeTab === 'collections' ? 'btn-primary' : 'btn-outline'}`}
            style={{ fontSize: '0.85rem', padding: '0.45rem 1rem' }}
            onClick={() => setActiveTab('collections')}
          >
            <span>Collection Requests ({mappedCollections.length})</span>
          </button>
          <button
            type="button"
            className={`btn ${activeTab === 'scans' ? 'btn-primary' : 'btn-outline'}`}
            style={{ fontSize: '0.85rem', padding: '0.45rem 1rem' }}
            onClick={() => setActiveTab('scans')}
          >
            <span>AI Waste Scans ({mappedWasteReports.length})</span>
          </button>
        </div>

        {/* Action alert message */}
        {actionMessage && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            backgroundColor: '#F0F6F1',
            border: '1.5px solid #C8DEC9',
            color: '#285430',
            borderRadius: 'var(--radius-sm)',
            padding: '0.85rem 1.25rem',
            marginBottom: '1rem',
            fontSize: '0.9rem',
            fontWeight: 500
          }}>
            <CheckCircle2 size={18} />
            <span>{actionMessage}</span>
          </div>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="empty-reports-card" style={{ padding: '3.5rem 1.5rem' }}>
            <div className="spinner-sage" style={{ width: 36, height: 36, margin: '0 auto 1rem auto' }} />
            <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)' }}>Loading your reports...</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>Fetching latest status from municipal backend</p>
          </div>
        ) : error ? (
          /* Error State */
          <div className="empty-reports-card" style={{ padding: '3rem 1.5rem', borderColor: '#EAC8C8' }}>
            <AlertCircle size={36} style={{ color: '#A83B3B', margin: '0 auto 1rem auto' }} />
            <h3 style={{ fontSize: '1.2rem', color: '#A83B3B', marginBottom: '0.4rem' }}>Unable to Load Reports</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', maxWidth: '440px', margin: '0 auto 1.25rem auto' }}>
              {error}
            </p>
            <button type="button" className="btn btn-secondary" onClick={fetchData}>
              Try Again
            </button>
          </div>
        ) : activeItems.length === 0 ? (
          /* Empty State */
          <div className="empty-reports-card">
            <div className="empty-reports-icon">
              <Inbox size={30} strokeWidth={1.8} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
                {activeTab === 'collections' ? 'No collection requests found' : 'No scanned waste history found'}
              </h2>
              <p className="subheading" style={{ maxWidth: '460px', margin: '0 auto', fontSize: '0.95rem' }}>
                {activeTab === 'collections'
                  ? 'You have not submitted any waste collection requests yet. Scan an item or report waste in your area to get started.'
                  : 'You have not scanned any waste items yet. Use the AI Waste Scanner to identify materials and receive guidance.'}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
              {activeTab === 'collections' ? (
                <button 
                  className="btn btn-primary"
                  onClick={() => onNavigate('Report Waste')}
                >
                  <Plus size={16} />
                  <span>Request Waste Collection</span>
                </button>
              ) : (
                <button 
                  className="btn btn-primary"
                  onClick={() => onNavigate('Waste Scanner')}
                >
                  <Camera size={16} />
                  <span>Scan Waste Now</span>
                </button>
              )}
            </div>
          </div>
        ) : (
          <>
            {/* Desktop View: Reports Table */}
            <div className="reports-table-card">
              <div className="reports-table-responsive">
                <table className="reports-table">
                  <thead>
                    <tr>
                      <th>Report ID</th>
                      <th>Waste Type</th>
                      <th>Location / Method</th>
                      <th>Date</th>
                      <th>{activeTab === 'collections' ? 'Severity' : 'AI Confidence'}</th>
                      <th>Status</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeItems.map((item) => (
                      <tr 
                        key={item.id} 
                        className="clickable-row"
                        onClick={() => setSelectedReport(item)}
                      >
                        <td style={{ fontWeight: 700, color: 'var(--sage-800)' }}>
                          {item.id}
                        </td>
                        <td style={{ fontWeight: 600 }}>
                          {item.wasteType}
                        </td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                            <MapPin size={15} className="text-sage-accent" />
                            <span>{item.location}</span>
                          </div>
                        </td>
                        <td style={{ color: 'var(--text-secondary)' }}>
                          {item.date}
                        </td>
                        <td>
                          {activeTab === 'collections' ? (
                            renderSeverityTag(item.severity)
                          ) : (
                            <span style={{ fontWeight: 600, color: 'var(--sage-700)' }}>{item.confidence}%</span>
                          )}
                        </td>
                        <td>
                          {renderStatusBadge(item.status)}
                        </td>
                        <td style={{ textAlign: 'right', color: 'var(--text-muted)' }}>
                          <ChevronRight size={18} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Mobile View: Stacked Cards */}
            <div className="mobile-reports-list">
              {activeItems.map((item) => (
                <div 
                  key={item.id} 
                  className="mobile-report-card"
                  onClick={() => setSelectedReport(item)}
                >
                  <div className="mobile-card-top">
                    <span style={{ fontWeight: 700, color: 'var(--sage-800)', fontSize: '1rem' }}>
                      {item.id}
                    </span>
                    {renderStatusBadge(item.status)}
                  </div>

                  <div className="mobile-card-body">
                    <div style={{ fontWeight: 600, fontSize: '1.05rem', color: 'var(--text-primary)' }}>
                      {item.wasteType}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                      <MapPin size={14} className="text-sage-accent" />
                      <span>{item.location}</span>
                    </div>
                  </div>

                  <div className="mobile-card-bottom">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      <Calendar size={14} />
                      <span>{item.date}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {activeTab === 'collections' ? renderSeverityTag(item.severity) : `${item.confidence}%`}
                      <ChevronRight size={16} style={{ color: 'var(--text-muted)' }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Modal: Report Detail View */}
        {selectedReport && (
          <div className="modal-overlay" onClick={() => setSelectedReport(null)}>
            <div className="detail-modal-card" onClick={(e) => e.stopPropagation()}>
              {/* Modal Header */}
              <div className="detail-modal-header">
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                    {selectedReport.isCollection ? 'Municipal Collection Request' : 'Scanned Waste Report'}
                  </div>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {selectedReport.id}
                  </h2>
                </div>
                <button 
                  type="button" 
                  className="detail-close-btn"
                  onClick={() => setSelectedReport(null)}
                  aria-label="Close detail modal"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Progress Indicator for Collection Requests */}
              {selectedReport.isCollection && selectedReport.rawStatus !== 'rejected' && (
                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.65rem' }}>
                    Pickup Resolution Progress
                  </div>
                  <div className="progress-pipeline">
                    {progressSteps.map((stepName, sIdx) => {
                      const stepNum = sIdx + 1;
                      const isCompleted = stepNum < (selectedReport.currentStage || 1);
                      const isCurrent = stepNum === (selectedReport.currentStage || 1);
                      return (
                        <div 
                          key={stepName} 
                          className={`pipeline-step ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}
                        >
                          <div className="step-bullet">
                            {isCompleted ? '✓' : stepNum}
                          </div>
                          <span className="step-text">{stepName}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Rejection Notice if applicable */}
              {selectedReport.rawStatus === 'rejected' && (
                <div style={{
                  padding: '1rem',
                  backgroundColor: '#FBECEB',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid #EDCECE',
                  color: '#8A3333',
                  fontSize: '0.9rem'
                }}>
                  <strong>Notice:</strong> This collection request was reviewed and rejected by municipal dispatch.
                </div>
              )}

              {/* Report Information Grid */}
              <div className="detail-grid">
                <div className="detail-image-box">
                  {selectedReport.image ? (
                    <img src={selectedReport.image} alt="Reported waste photograph" />
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                      No photo attached
                    </div>
                  )}
                </div>

                <div className="detail-fields">
                  <div className="detail-row">
                    <span className="detail-row-label">Waste Type</span>
                    <span className="detail-row-value">{selectedReport.wasteType}</span>
                  </div>

                  <div className="detail-row">
                    <span className="detail-row-label">Location</span>
                    <span className="detail-row-value">{selectedReport.location}</span>
                  </div>

                  <div className="detail-row">
                    <span className="detail-row-label">Date Submitted</span>
                    <span className="detail-row-value">{selectedReport.date}</span>
                  </div>

                  {selectedReport.scheduledDate && (
                    <div className="detail-row">
                      <span className="detail-row-label">Scheduled Pickup</span>
                      <span className="detail-row-value" style={{ color: 'var(--sage-800)', fontWeight: 600 }}>
                        {selectedReport.scheduledDate}
                      </span>
                    </div>
                  )}

                  {selectedReport.completedAt && (
                    <div className="detail-row">
                      <span className="detail-row-label">Completed Date</span>
                      <span className="detail-row-value" style={{ color: 'var(--sage-800)', fontWeight: 600 }}>
                        {selectedReport.completedAt}
                      </span>
                    </div>
                  )}

                  <div className="detail-row">
                    <span className="detail-row-label">Current Status</span>
                    <div>{renderStatusBadge(selectedReport.status)}</div>
                  </div>
                </div>
              </div>

              {/* Description / Additional Notes */}
              <div style={{ backgroundColor: 'var(--bg-main)', padding: '1.25rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                <div className="detail-row-label" style={{ marginBottom: '0.4rem' }}>
                  {selectedReport.isCollection ? 'Pickup Notes' : 'AI Analysis Description'}
                </div>
                <p style={{ fontSize: '0.925rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {selectedReport.description}
                </p>
              </div>

              {/* Disposal Guidance for AI Scans */}
              {selectedReport.disposal_guidance && (
                <div style={{ backgroundColor: 'var(--bg-sage-light)', padding: '1.25rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                  <div className="detail-row-label" style={{ marginBottom: '0.5rem', color: 'var(--sage-900)' }}>
                    Recommended Disposal Guidance ({selectedReport.disposal_guidance.disposal_method || 'Segregation & Recycling'})
                  </div>
                  <ul style={{ paddingLeft: '1.25rem', fontSize: '0.9rem', color: 'var(--sage-900)', lineHeight: 1.6 }}>
                    {(selectedReport.disposal_guidance.do || selectedReport.disposal_guidance.instructions || [
                      `Segregate clean ${selectedReport.wasteType} according to municipal guidelines.`
                    ]).map((inst, i) => (
                      <li key={i}>{inst}</li>
                    ))}
                  </ul>
                  {selectedReport.disposal_guidance.dont && selectedReport.disposal_guidance.dont.length > 0 && (
                    <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px dashed var(--border-color)' }}>
                      <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#A83B3B', marginBottom: '0.35rem' }}>Precautions to Avoid:</div>
                      <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', color: '#8A3333', lineHeight: 1.5 }}>
                        {selectedReport.disposal_guidance.dont.map((warning, i) => (
                          <li key={i}>{warning}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Modal Footer */}
              <div className="detail-modal-footer">
                {selectedReport.isCollection && selectedReport.rawStatus === 'submitted' && (
                  <button 
                    type="button" 
                    className="btn btn-outline"
                    style={{ borderColor: '#EAC8C8', color: '#A83B3B' }}
                    onClick={() => handleCancelRequest(selectedReport.dbId)}
                    disabled={actionLoading}
                  >
                    <Trash2 size={15} />
                    <span>Cancel Request</span>
                  </button>
                )}

                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setSelectedReport(null)}
                >
                  Close
                </button>

                {selectedReport.isWasteReport && (
                  <button 
                    type="button" 
                    className="btn btn-primary"
                    onClick={() => {
                      const wr = selectedReport;
                      setSelectedReport(null);
                      onNavigate('Report Waste');
                    }}
                  >
                    <Plus size={16} />
                    <span>Request Collection</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

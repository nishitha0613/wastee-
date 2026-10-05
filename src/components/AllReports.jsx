import React, { useState, useEffect, useMemo } from 'react';
import { 
  FileText, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  Calendar, 
  Filter, 
  Search, 
  X, 
  ChevronRight, 
  AlertTriangle, 
  ArrowUpRight,
  ShieldCheck,
  Eye,
  SlidersHorizontal,
  RefreshCw,
  AlertCircle,
  Truck,
  Check,
  Ban,
  User
} from 'lucide-react';
import { adminApi, getImageUrl } from '../services/api';

export default function AllReports({ onNavigate }) {
  const [reports, setReports] = useState([]);
  const [statsData, setStatsData] = useState({
    total: 0,
    submitted: 0,
    accepted: 0,
    scheduled: 0,
    collected: 0,
    completed: 0,
    rejected: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [severityFilter, setSeverityFilter] = useState('All');
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [scheduleDateTime, setScheduleDateTime] = useState('');

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [requestsRes, statsRes] = await Promise.all([
        adminApi.getCollectionRequests(),
        adminApi.getCollectionStats(),
      ]);

      setReports(Array.isArray(requestsRes) ? requestsRes : (requestsRes?.items || []));
      if (statsRes) setStatsData(statsRes);
    } catch (err) {
      setError(err.message || 'Failed to fetch collection requests from server.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const totalCount = statsData.total || reports.length;
  const pendingCount = statsData.submitted || 0;
  const inProgressCount = (statsData.accepted || 0) + (statsData.scheduled || 0) + (statsData.collected || 0);
  const resolvedCount = statsData.completed || 0;

  const stats = [
    { label: 'Total Requests Filed', value: totalCount, icon: FileText, color: 'var(--sage-700)' },
    { label: 'Pending Review', value: pendingCount, icon: Clock, color: '#9B7126' },
    { label: 'Cleanup In Progress', value: inProgressCount, icon: AlertTriangle, color: '#C07D32' },
    { label: 'Resolved & Completed', value: resolvedCount, icon: CheckCircle2, color: 'var(--sage-800)' },
  ];

  const renderStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return <span className="status-badge status-badge-resolved">Completed</span>;
      case 'accepted':
        return <span className="status-badge status-badge-in-progress">Accepted</span>;
      case 'scheduled':
        return <span className="status-badge status-badge-in-progress" style={{ backgroundColor: '#EBF3ED', color: '#2F5938' }}>Scheduled</span>;
      case 'collected':
        return <span className="status-badge status-badge-in-progress" style={{ backgroundColor: '#FDF3E7', color: '#9B7126' }}>Collected</span>;
      case 'rejected':
        return <span className="status-badge status-badge-pending" style={{ backgroundColor: '#FBECEB', color: '#8A3333', borderColor: '#EDCECE' }}>Rejected</span>;
      case 'submitted':
      default:
        return <span className="status-badge status-badge-pending">Submitted</span>;
    }
  };

  const renderSeverityTag = (severity = 'Medium') => {
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

  const getStageNumber = (status) => {
    switch (status?.toLowerCase()) {
      case 'submitted': return 1;
      case 'accepted': return 2;
      case 'scheduled': return 3;
      case 'collected': return 4;
      case 'completed': return 5;
      default: return 0;
    }
  };

  // Perform workflow transition
  const handleWorkflowAction = async (action, requestId, payload = null) => {
    setActionLoading(true);
    setActionError(null);
    try {
      let updated;
      if (action === 'accept') {
        updated = await adminApi.acceptRequest(requestId);
      } else if (action === 'schedule') {
        const dateToSchedule = payload || scheduleDateTime || new Date(Date.now() + 86400000).toISOString();
        updated = await adminApi.scheduleRequest(requestId, dateToSchedule);
      } else if (action === 'collect') {
        updated = await adminApi.collectRequest(requestId);
      } else if (action === 'complete') {
        updated = await adminApi.completeRequest(requestId);
      } else if (action === 'reject') {
        const reason = payload || prompt('Reason for rejection (optional):') || 'Disposal guidelines not met.';
        updated = await adminApi.rejectRequest(requestId, reason);
      }

      // Update state immediately
      setReports((prev) => prev.map((r) => (r.id === requestId ? { ...r, ...updated } : r)));
      if (selectedReport && selectedReport.id === requestId) {
        setSelectedReport((prev) => ({ ...prev, ...updated }));
      }

      // Refresh stats
      const statsRes = await adminApi.getCollectionStats();
      if (statsRes) setStatsData(statsRes);
    } catch (err) {
      setActionError(err.message || 'Failed to update request status.');
    } finally {
      setActionLoading(false);
    }
  };

  // Filter and search reports
  const filteredReports = useMemo(() => {
    return reports.filter((report) => {
      const displayId = `CR-${report.id}`;
      const matchesSearch = 
        !searchQuery ||
        displayId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.waste_type?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.location?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.additional_notes?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.user?.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.user?.email?.toLowerCase().includes(searchQuery.toLowerCase());

      const statusMap = {
        'Pending': 'submitted',
        'In Progress': ['accepted', 'scheduled', 'collected'],
        'Resolved': 'completed',
        'Rejected': 'rejected',
      };

      let matchesStatus = true;
      if (statusFilter !== 'All') {
        const expected = statusMap[statusFilter];
        if (Array.isArray(expected)) {
          matchesStatus = expected.includes(report.status);
        } else {
          matchesStatus = report.status === expected;
        }
      }

      const severity = report.quantity?.includes('High') ? 'High' : report.quantity?.includes('Low') ? 'Low' : 'Medium';
      const matchesSeverity = 
        severityFilter === 'All' || severity.toLowerCase() === severityFilter.toLowerCase();

      return matchesSearch && matchesStatus && matchesSeverity;
    });
  }, [reports, searchQuery, statusFilter, severityFilter]);

  return (
    <section className="my-reports-section" style={{ minHeight: '85vh', paddingBottom: '4rem' }}>
      <div className="container my-reports-container">
        {/* Admin Header */}
        <div className="my-reports-header-wrapper">
          <div>
            <div className="badge-pill" style={{ marginBottom: '0.65rem' }}>
              <ShieldCheck size={14} />
              <span>Municipal Dispatch Authority</span>
            </div>
            <h1 className="page-title">All Reports</h1>
            <p className="subheading" style={{ marginTop: '0.25rem' }}>
              Comprehensive municipal registry of community waste collection requests and dispatch workflow.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.85rem', padding: '0.55rem 0.9rem' }}
              onClick={loadData}
              disabled={isLoading}
              title="Refresh requests"
            >
              <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
              <span>Refresh</span>
            </button>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              Showing {filteredReports.length} of {totalCount} total records
            </span>
          </div>
        </div>

        {/* 4 Admin Statistics Cards */}
        <div className="reports-stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))' }}>
          {stats.map((st, idx) => {
            const IconComp = st.icon;
            return (
              <div key={idx} className="report-stat-card">
                <div className="report-stat-icon-wrap" style={{ color: st.color }}>
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

        {/* Filter and Search Bar */}
        <div style={{
          backgroundColor: 'var(--bg-card)',
          borderRadius: 'var(--radius-md)',
          padding: '1.25rem',
          border: '1px solid var(--border-color)',
          marginTop: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', justifyContent: 'space-between' }}>
            {/* Search Input */}
            <div style={{ position: 'relative', flex: '1 1 280px', maxWidth: '420px' }}>
              <Search size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input 
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by ID, citizen, waste type, or area..."
                className="input-field"
                style={{ paddingLeft: '2.5rem', fontSize: '0.88rem' }}
              />
              {searchQuery && (
                <button 
                  type="button" 
                  onClick={() => setSearchQuery('')}
                  style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}
                >
                  <X size={15} />
                </button>
              )}
            </div>

            {/* Filter Controls */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                <Filter size={15} />
                <span>Status:</span>
              </div>
              {['All', 'Pending', 'In Progress', 'Resolved'].map((st) => (
                <button
                  key={st}
                  type="button"
                  onClick={() => setStatusFilter(st)}
                  className={`btn ${statusFilter === st ? 'btn-primary' : 'btn-outline'}`}
                  style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
                >
                  {st}
                </button>
              ))}

              <div style={{ height: '1.25rem', width: '1px', backgroundColor: 'var(--border-color)', margin: '0 0.25rem' }} />

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                <SlidersHorizontal size={15} />
                <span>Severity:</span>
              </div>
              {['All', 'High', 'Medium', 'Low'].map((sev) => (
                <button
                  key={sev}
                  type="button"
                  onClick={() => setSeverityFilter(sev)}
                  className={`btn ${severityFilter === sev ? 'btn-primary' : 'btn-outline'}`}
                  style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
                >
                  {sev}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Global Action Error Notice */}
        {actionError && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            backgroundColor: '#FDF7F7',
            border: '1.5px solid #EAC8C8',
            color: '#A83B3B',
            borderRadius: 'var(--radius-sm)',
            padding: '0.85rem 1.25rem',
            marginTop: '1rem',
            fontSize: '0.9rem'
          }}>
            <AlertCircle size={18} />
            <span>{actionError}</span>
          </div>
        )}

        {/* Reports Content: Loading, Error, Empty, or Table */}
        <div style={{ marginTop: '1.5rem' }}>
          {isLoading ? (
            <div className="empty-reports-card" style={{ padding: '3.5rem 1.5rem', textAlign: 'center' }}>
              <div className="spinner-sage" style={{ width: 36, height: 36, margin: '0 auto 1rem auto' }} />
              <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)' }}>Loading municipal records...</h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>Connecting to collection management service</p>
            </div>
          ) : error ? (
            <div className="empty-reports-card" style={{ padding: '3rem 1.5rem', borderColor: '#EAC8C8', textAlign: 'center' }}>
              <AlertCircle size={36} style={{ color: '#A83B3B', margin: '0 auto 1rem auto' }} />
              <h3 style={{ fontSize: '1.2rem', color: '#A83B3B', marginBottom: '0.4rem' }}>Error Loading Records</h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', maxWidth: '440px', margin: '0 auto 1.25rem auto' }}>
                {error}
              </p>
              <button type="button" className="btn btn-secondary" onClick={loadData}>
                Retry
              </button>
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="empty-reports-card" style={{ padding: '3.5rem 1.5rem', textAlign: 'center' }}>
              <FileText size={42} style={{ margin: '0 auto 1rem auto', color: 'var(--sage-400)' }} />
              <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
                No Matching Requests Found
              </h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', maxWidth: '420px', margin: '0 auto 1.25rem auto' }}>
                Try adjusting your search query or reset the status/severity filters to view records.
              </p>
              <button 
                type="button"
                className="btn btn-outline"
                style={{ fontSize: '0.85rem' }}
                onClick={() => { setSearchQuery(''); setStatusFilter('All'); setSeverityFilter('All'); }}
              >
                Clear All Filters
              </button>
            </div>
          ) : (
            <div className="reports-table-responsive">
              <table className="reports-table">
                <thead>
                  <tr>
                    <th>Request ID</th>
                    <th>Waste Type</th>
                    <th>Location</th>
                    <th>Citizen</th>
                    <th>Date Reported</th>
                    <th>Status</th>
                    <th style={{ textAlign: 'right' }}>Dispatch Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredReports.map((report) => {
                    const displayId = `CR-${report.id}`;
                    const severity = report.quantity?.includes('High') ? 'High' : report.quantity?.includes('Low') ? 'Low' : 'Medium';
                    const dateStr = new Date(report.requested_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });

                    return (
                      <tr 
                        key={report.id}
                        className="clickable-row"
                        onClick={() => setSelectedReport(report)}
                      >
                        <td style={{ fontWeight: 700, color: 'var(--sage-900)' }}>
                          {displayId}
                        </td>
                        <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                          {report.waste_type}
                        </td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--text-secondary)' }}>
                            <MapPin size={14} className="text-sage-accent" />
                            <span>{report.location}</span>
                          </div>
                        </td>
                        <td>
                          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                            {report.user?.name || `User #${report.user_id}`}
                          </div>
                        </td>
                        <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                          {dateStr}
                        </td>
                        <td>
                          {renderStatusBadge(report.status)}
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }} onClick={(e) => e.stopPropagation()}>
                            {/* Workflow Quick Action Buttons */}
                            {report.status === 'submitted' && (
                              <>
                                <button 
                                  type="button"
                                  className="btn btn-primary"
                                  style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                                  disabled={actionLoading}
                                  onClick={() => handleWorkflowAction('accept', report.id)}
                                  title="Accept this collection request"
                                >
                                  Accept
                                </button>
                                <button 
                                  type="button"
                                  className="btn btn-outline"
                                  style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', borderColor: '#EAC8C8', color: '#A83B3B' }}
                                  disabled={actionLoading}
                                  onClick={() => handleWorkflowAction('reject', report.id)}
                                  title="Reject request"
                                >
                                  Reject
                                </button>
                              </>
                            )}

                            {report.status === 'accepted' && (
                              <button 
                                type="button"
                                className="btn btn-primary"
                                style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem', backgroundColor: '#386343' }}
                                disabled={actionLoading}
                                onClick={() => {
                                  const tomorrow = new Date(Date.now() + 86400000);
                                  tomorrow.setHours(10, 0, 0, 0);
                                  handleWorkflowAction('schedule', report.id, tomorrow.toISOString());
                                }}
                                title="Schedule for pickup tomorrow at 10 AM"
                              >
                                Schedule
                              </button>
                            )}

                            {report.status === 'scheduled' && (
                              <button 
                                type="button"
                                className="btn btn-primary"
                                style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem', backgroundColor: '#9B7126' }}
                                disabled={actionLoading}
                                onClick={() => handleWorkflowAction('collect', report.id)}
                                title="Mark as collected by vehicle"
                              >
                                Collect
                              </button>
                            )}

                            {report.status === 'collected' && (
                              <button 
                                type="button"
                                className="btn btn-primary"
                                style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }}
                                disabled={actionLoading}
                                onClick={() => handleWorkflowAction('complete', report.id)}
                                title="Mark collection completed"
                              >
                                Complete
                              </button>
                            )}

                            <button 
                              type="button"
                              className="btn btn-secondary"
                              style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                              onClick={() => setSelectedReport(report)}
                              title="Inspect full details"
                            >
                              <Eye size={13} />
                              <span>Details</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal: Full Report Details & Municipal Resolution */}
        {selectedReport && (
          <div className="modal-overlay" onClick={() => setSelectedReport(null)}>
            <div className="detail-modal-card" onClick={(e) => e.stopPropagation()}>
              <div className="detail-modal-header">
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
                    <span className="badge-pill" style={{ fontSize: '0.75rem', padding: '0.2rem 0.55rem' }}>
                      CR-{selectedReport.id}
                    </span>
                    {renderSeverityTag(selectedReport.quantity?.includes('High') ? 'High' : selectedReport.quantity?.includes('Low') ? 'Low' : 'Medium')}
                  </div>
                  <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {selectedReport.waste_type}
                  </h2>
                </div>

                <button 
                  type="button" 
                  className="detail-close-btn"
                  onClick={() => setSelectedReport(null)}
                  aria-label="Close modal"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Resolution Pipeline Stages */}
              {selectedReport.status !== 'rejected' && (
                <div className="progress-stepper">
                  {progressSteps.map((stepName, idx) => {
                    const stepNumber = idx + 1;
                    const stageNum = getStageNumber(selectedReport.status);
                    const isCompleted = stageNum >= stepNumber;
                    const isCurrent = stageNum === stepNumber;

                    return (
                      <div key={stepName} className="stepper-step">
                        <div className={`stepper-circle ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}>
                          {isCompleted ? <CheckCircle2 size={15} /> : stepNumber}
                        </div>
                        <span className={`stepper-label ${isCompleted ? 'completed' : ''}`}>
                          {stepName}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Rejection Alert */}
              {selectedReport.status === 'rejected' && (
                <div style={{
                  padding: '1rem',
                  backgroundColor: '#FBECEB',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid #EDCECE',
                  color: '#8A3333',
                  fontSize: '0.9rem',
                  marginBottom: '1rem'
                }}>
                  <strong>Status:</strong> This collection request has been rejected.
                </div>
              )}

              {/* Admin Workflow Action Panel */}
              <div style={{
                backgroundColor: 'var(--bg-sage-light)',
                padding: '1.25rem',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
                marginBottom: '1.25rem'
              }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--sage-900)', marginBottom: '0.75rem' }}>
                  Municipal Dispatch Workflow Actions
                </div>
                
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center' }}>
                  {selectedReport.status === 'submitted' && (
                    <>
                      <button 
                        type="button" 
                        className="btn btn-primary"
                        disabled={actionLoading}
                        onClick={() => handleWorkflowAction('accept', selectedReport.id)}
                      >
                        <Check size={16} />
                        <span>Accept Request</span>
                      </button>
                      <button 
                        type="button" 
                        className="btn btn-outline"
                        style={{ borderColor: '#EAC8C8', color: '#A83B3B' }}
                        disabled={actionLoading}
                        onClick={() => handleWorkflowAction('reject', selectedReport.id)}
                      >
                        <Ban size={16} />
                        <span>Reject Request</span>
                      </button>
                    </>
                  )}

                  {selectedReport.status === 'accepted' && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center', width: '100%' }}>
                      <input 
                        type="datetime-local"
                        value={scheduleDateTime}
                        onChange={(e) => setScheduleDateTime(e.target.value)}
                        className="input-field"
                        style={{ maxWidth: '240px', fontSize: '0.85rem', padding: '0.45rem 0.75rem' }}
                      />
                      <button 
                        type="button" 
                        className="btn btn-primary"
                        disabled={actionLoading}
                        onClick={() => {
                          const dt = scheduleDateTime ? new Date(scheduleDateTime).toISOString() : new Date(Date.now() + 86400000).toISOString();
                          handleWorkflowAction('schedule', selectedReport.id, dt);
                        }}
                      >
                        <Calendar size={16} />
                        <span>Confirm Schedule</span>
                      </button>
                    </div>
                  )}

                  {selectedReport.status === 'scheduled' && (
                    <button 
                      type="button" 
                      className="btn btn-primary"
                      disabled={actionLoading}
                      onClick={() => handleWorkflowAction('collect', selectedReport.id)}
                    >
                      <Truck size={16} />
                      <span>Mark Collected by Crew</span>
                    </button>
                  )}

                  {selectedReport.status === 'collected' && (
                    <button 
                      type="button" 
                      className="btn btn-primary"
                      disabled={actionLoading}
                      onClick={() => handleWorkflowAction('complete', selectedReport.id)}
                    >
                      <CheckCircle2 size={16} />
                      <span>Mark Resolution Completed</span>
                    </button>
                  )}

                  {selectedReport.status === 'completed' && (
                    <span style={{ fontSize: '0.85rem', color: 'var(--sage-800)', fontWeight: 600 }}>
                      ✓ Cleanup lifecycle successfully completed.
                    </span>
                  )}
                </div>
              </div>

              {/* Report Information Grid */}
              <div className="report-detail-rows">
                <div className="detail-row">
                  <span className="detail-row-label">Citizen Reporter</span>
                  <span className="detail-row-value">
                    {selectedReport.user?.name ? `${selectedReport.user.name} (${selectedReport.user.email})` : `User #${selectedReport.user_id}`}
                  </span>
                </div>

                <div className="detail-row">
                  <span className="detail-row-label">Location</span>
                  <span className="detail-row-value" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <MapPin size={14} className="text-sage-accent" />
                    {selectedReport.location}
                  </span>
                </div>

                <div className="detail-row">
                  <span className="detail-row-label">Date Submitted</span>
                  <span className="detail-row-value">
                    {new Date(selectedReport.requested_at).toLocaleString()}
                  </span>
                </div>

                {selectedReport.scheduled_date && (
                  <div className="detail-row">
                    <span className="detail-row-label">Scheduled Pickup</span>
                    <span className="detail-row-value" style={{ color: 'var(--sage-800)', fontWeight: 600 }}>
                      {new Date(selectedReport.scheduled_date).toLocaleString()}
                    </span>
                  </div>
                )}

                {selectedReport.completed_at && (
                  <div className="detail-row">
                    <span className="detail-row-label">Completed Date</span>
                    <span className="detail-row-value" style={{ color: 'var(--sage-800)', fontWeight: 600 }}>
                      {new Date(selectedReport.completed_at).toLocaleString()}
                    </span>
                  </div>
                )}

                <div className="detail-row">
                  <span className="detail-row-label">Current Status</span>
                  <div>{renderStatusBadge(selectedReport.status)}</div>
                </div>

                {selectedReport.additional_notes && (
                  <div className="detail-description-box">
                    <span className="detail-row-label">Citizen Notes & Description</span>
                    <p style={{ marginTop: '0.35rem', color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.5 }}>
                      {selectedReport.additional_notes}
                    </p>
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="detail-modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setSelectedReport(null)}
                >
                  Close Record
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary"
                  onClick={() => {
                    setSelectedReport(null);
                    onNavigate('Waste Map');
                  }}
                >
                  <MapPin size={16} />
                  <span>Locate on Map</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

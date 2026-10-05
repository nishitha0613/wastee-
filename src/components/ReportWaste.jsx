import React, { useState, useEffect, useRef } from 'react';
import { 
  Camera, 
  MapPin, 
  UploadCloud, 
  Trash2, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  ArrowRight, 
  FileText, 
  RotateCcw
} from 'lucide-react';

import { collectionApi } from '../services/api';

export default function ReportWaste({ initialData, onViewMyReports, onAddReport }) {
  const [photo, setPhoto] = useState(initialData?.photo || null);
  const [photoName, setPhotoName] = useState(initialData?.photoName || '');
  const [wasteType, setWasteType] = useState(initialData?.wasteType || 'Plastic');
  const [location, setLocation] = useState(initialData?.location || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [severity, setSeverity] = useState('Medium');
  const [wasteReportId, setWasteReportId] = useState(initialData?.wasteReportId || null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [reportId, setReportId] = useState('CR-1');
  const [errors, setErrors] = useState({});
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  // Sync initialData if provided from Scanner
  useEffect(() => {
    if (initialData) {
      if (initialData.photo) setPhoto(initialData.photo);
      if (initialData.photoName) setPhotoName(initialData.photoName);
      if (initialData.wasteType) setWasteType(initialData.wasteType);
      if (initialData.description) setDescription(initialData.description);
      if (initialData.wasteReportId) setWasteReportId(initialData.wasteReportId);
    }
  }, [initialData]);

  const wasteTypes = [
    'Organic',
    'Plastic',
    'Paper',
    'Glass',
    'Metal',
    'E-waste',
    'Hazardous',
    'Mixed Waste'
  ];

  const severityLevels = ['Low', 'Medium', 'High'];

  const handlePhotoUpload = (file) => {
    if (file && file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPhoto(url);
      setPhotoName(file.name);
      setErrors((prev) => ({ ...prev, photo: null }));
    } else if (file) {
      setErrors((prev) => ({ ...prev, photo: 'Please upload a valid image file (JPG, PNG, WEBP).' }));
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handlePhotoUpload(e.dataTransfer.files[0]);
    }
  };

  const handleSamplePhoto = () => {
    setPhoto('/sample-report-waste.jpg');
    setPhotoName('oak-st-curb-waste.jpg');
    setLocation('Corner of Oak St & Maple Ave');
    setDescription('Accumulated cardboard boxes, plastic jugs, and bottles along the sidewalk curb.');
    setWasteType('Mixed Waste');
    setErrors({});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = {};

    if (!location.trim()) {
      newErrors.location = 'Please specify the location (street, landmark, or area).';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      const response = await collectionApi.create({
        waste_report_id: wasteReportId || null,
        waste_type: wasteType,
        quantity: `${severity} Volume`,
        location: location.trim(),
        additional_notes: description.trim() || undefined,
      });

      const generatedId = `CR-${response.id}`;
      setReportId(generatedId);
      setIsSubmitting(false);
      setIsSubmitted(true);

      if (onAddReport) {
        onAddReport({
          id: generatedId,
          numericId: response.id,
          wasteType: response.waste_type || wasteType,
          location: response.location,
          date: new Date(response.requested_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
          status: 'Pending',
          severity: severity,
          image: photo,
          description: response.additional_notes || description.trim() || 'No additional description provided.',
          currentStage: 1, // 1: Reported/Submitted
          rawStatus: response.status,
          scheduledDate: response.scheduled_date,
          completedAt: response.completed_at,
        });
      }
    } catch (err) {
      setIsSubmitting(false);
      setErrors({ general: err.message || 'Failed to submit collection request. Please check backend connection.' });
    }
  };

  const handleResetForm = () => {
    setPhoto(null);
    setPhotoName('');
    setWasteType('Plastic');
    setLocation('');
    setDescription('');
    setSeverity('Medium');
    setWasteReportId(null);
    setErrors({});
    setIsSubmitted(false);
  };

  return (
    <section className="report-section">
      <div className="container report-container">
        {/* Page Title & Subtitle */}
        <div className="report-header">
          <div className="badge-pill">
            <AlertCircle size={14} />
            <span>Community Action</span>
          </div>
          <h1 className="page-title">Report Waste</h1>
          <p className="subheading" style={{ maxWidth: '540px' }}>
            Help keep your community clean by reporting waste in your area.
          </p>
        </div>

        {/* State A: Report Form */}
        {!isSubmitted ? (
          <form className="report-card" onSubmit={handleSubmit} noValidate>
            {/* Top Error Alert if validation fails */}
            {(errors.photo || errors.location || errors.general) && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem',
                backgroundColor: '#FDF7F7',
                border: '1.5px solid #EAC8C8',
                color: '#A83B3B',
                borderRadius: 'var(--radius-sm)',
                padding: '0.85rem 1.25rem',
                marginBottom: '1.25rem',
                fontSize: '0.9rem',
                fontWeight: 500
              }}>
                <AlertCircle size={18} />
                <span>{errors.general || 'Required form field missing: Please specify the pickup location.'}</span>
              </div>
            )}

            {/* 1. Upload Photo */}
            <div className="form-group">
              <label className="form-label">
                <Camera size={16} className="text-sage-accent" />
                <span>Upload Waste Photo</span>
                <span className="form-label-required">*</span>
              </label>

              {!photo ? (
                <div 
                  className={`report-upload-zone ${dragActive ? 'drag-active' : ''} ${errors.photo ? 'input-error' : ''}`}
                  onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
                  onDragLeave={(e) => { e.preventDefault(); setDragActive(false); }}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current && fileInputRef.current.click()}
                >
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    style={{ display: 'none' }} 
                    accept="image/jpeg,image/png,image/webp"
                    onChange={(e) => e.target.files && handlePhotoUpload(e.target.files[0])}
                  />

                  <div className="upload-icon-wrapper" style={{ width: 50, height: 50, marginBottom: '0.85rem' }}>
                    <UploadCloud size={24} strokeWidth={2} />
                  </div>

                  <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                    Upload Waste Photo
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                    Drag and drop or click to browse (JPG, PNG, WEBP)
                  </div>

                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    style={{ padding: '0.5rem 1.1rem', fontSize: '0.85rem' }}
                    onClick={(e) => { e.stopPropagation(); fileInputRef.current && fileInputRef.current.click(); }}
                  >
                    Select File
                  </button>

                  <div style={{ marginTop: '1.25rem', paddingTop: '0.85rem', borderTop: '1px solid var(--border-subtle)', width: '100%' }} onClick={(e) => e.stopPropagation()}>
                    <button 
                      type="button" 
                      className="sample-pill-btn"
                      onClick={handleSamplePhoto}
                    >
                      <Sparkles size={13} className="text-sage-accent" />
                      <span>Use Demo Street Waste Photo</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="report-upload-preview">
                  <img src={photo} alt="Uploaded waste issue" />
                  <button 
                    type="button" 
                    className="preview-remove-overlay"
                    onClick={() => { setPhoto(null); setPhotoName(''); }}
                  >
                    <Trash2 size={13} />
                    <span>Remove Photo</span>
                  </button>
                </div>
              )}

              {errors.photo && <span className="form-error-text">{errors.photo}</span>}
            </div>

            {/* 2 & 3. Grouped Details: Waste Type & Location */}
            <div className="form-row">
              <div className="form-group">
                <label className="form-label" htmlFor="waste-type-select">
                  <span>Waste Type</span>
                </label>
                <select 
                  id="waste-type-select"
                  className="form-select"
                  value={wasteType}
                  onChange={(e) => setWasteType(e.target.value)}
                >
                  {wasteTypes.map((type) => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="location-input">
                  <span>Location</span>
                  <span className="form-label-required">*</span>
                </label>
                <div className="location-input-group">
                  <span className="location-input-icon">
                    <MapPin size={18} />
                  </span>
                  <input 
                    id="location-input"
                    type="text" 
                    className={`form-input form-input-with-icon ${errors.location ? 'input-error' : ''}`}
                    placeholder="Enter waste location"
                    value={location}
                    onChange={(e) => {
                      setLocation(e.target.value);
                      if (errors.location) setErrors((prev) => ({ ...prev, location: null }));
                    }}
                  />
                </div>
                {errors.location && <span className="form-error-text">{errors.location}</span>}
              </div>
            </div>

            {/* 4. Description */}
            <div className="form-group">
              <label className="form-label" htmlFor="description-input">
                <span>Description</span>
              </label>
              <textarea 
                id="description-input"
                className="form-textarea"
                placeholder="Describe the waste or issue..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {/* 5. Severity */}
            <div className="form-group">
              <label className="form-label">
                <span>Severity</span>
              </label>
              <div className="severity-selector">
                {severityLevels.map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    className={`severity-btn ${severity === lvl ? 'active' : ''}`}
                    onClick={() => setSeverity(lvl)}
                  >
                    <span>{lvl}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* 6. Submit Button */}
            <button 
              type="submit" 
              className="btn btn-primary"
              style={{ width: '100%', padding: '0.95rem', fontSize: '1rem', marginTop: '0.5rem' }}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <div className="spinner-sage" style={{ width: 18, height: 18, borderWidth: 2 }} />
                  <span>Submitting Report...</span>
                </>
              ) : (
                <>
                  <span>Submit Report</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>
        ) : (
          /* State B: Success State */
          <div className="report-success-card">
            <div className="success-icon-large">
              <CheckCircle2 size={40} strokeWidth={2.2} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h2 style={{ fontSize: '1.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Report Submitted Successfully
              </h2>
              <p className="subheading" style={{ fontSize: '1.05rem', maxWidth: '480px' }}>
                Your report has been recorded and will be reviewed.
              </p>
            </div>

            <div className="report-id-badge">
              <FileText size={18} className="text-sage-accent" />
              <span>Report ID: {reportId}</span>
            </div>

            {/* Report Summary Pill Details */}
            <div style={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              gap: '0.75rem', 
              justifyContent: 'center', 
              background: 'var(--bg-main)', 
              padding: '1rem 1.5rem', 
              borderRadius: 'var(--radius-md)', 
              border: '1px solid var(--border-color)',
              fontSize: '0.85rem',
              color: 'var(--text-secondary)'
            }}>
              <div><strong>Type:</strong> {wasteType}</div>
              <div>•</div>
              <div><strong>Severity:</strong> {severity}</div>
              <div>•</div>
              <div><strong>Location:</strong> {location || 'Oak St & Maple Ave'}</div>
            </div>

            <div className="success-actions">
              <button 
                type="button" 
                className="btn btn-primary"
                onClick={() => onViewMyReports(reportId)}
              >
                <span>View My Reports</span>
                <ArrowRight size={16} />
              </button>

              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={handleResetForm}
              >
                <RotateCcw size={16} />
                <span>Submit Another Report</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

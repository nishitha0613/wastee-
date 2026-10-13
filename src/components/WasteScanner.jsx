import React, { useState, useRef } from 'react';
import { 
  UploadCloud, 
  Image as ImageIcon, 
  Sparkles, 
  CheckCircle, 
  RefreshCw, 
  Trash2, 
  ShieldCheck, 
  ArrowRight,
  MapPin,
  AlertCircle,
  Leaf,
  Info,
  Cpu,
  XCircle,
  AlertTriangle
} from 'lucide-react';
import { wasteApi, getImageUrl } from '../services/api';

export default function WasteScanner({ onNavigateToReport }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageName, setImageName] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (file && (file.type.startsWith('image/') || /\.(jpg|jpeg|png|webp)$/i.test(file.name))) {
      setSelectedFile(file);
      const imageUrl = URL.createObjectURL(file);
      setSelectedImage(imageUrl);
      setImageName(file.name);
      setScanResult(null);
      setErrorMessage('');
    } else if (file) {
      setErrorMessage('Unsupported file format. Please upload JPG, PNG, or WEBP.');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleBrowseClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Convert demo sample images to real File objects so real API can be called
  const handleSampleSelect = async (samplePath, name) => {
    try {
      setSelectedImage(samplePath);
      setImageName(name);
      setScanResult(null);
      setErrorMessage('');

      // Fetch sample asset as blob
      const res = await fetch(samplePath);
      const blob = await res.blob();
      const ext = name.endsWith('.png') ? 'image/png' : 'image/jpeg';
      const file = new File([blob], name, { type: ext });
      setSelectedFile(file);
    } catch (e) {
      console.warn('Failed to load sample image file:', e);
      setSelectedFile(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile && !selectedImage) {
      setErrorMessage('No image selected. Please choose or upload a photo first.');
      return;
    }

    setErrorMessage('');
    setIsAnalyzing(true);

    try {
      let fileToUpload = selectedFile;

      // If sample was selected without pre-converting, convert now
      if (!fileToUpload && selectedImage) {
        const res = await fetch(selectedImage);
        const blob = await res.blob();
        fileToUpload = new File([blob], imageName || 'sample-waste.jpg', { type: blob.type || 'image/jpeg' });
      }

      // Real API call to FastAPI backend
      const res = await wasteApi.identify(fileToUpload);

      const confidenceVal = typeof res.confidence === 'number' ? res.confidence : 0;
      const confidencePct = `${Math.round(confidenceVal * 100)}%`;

      // Standard fallback category-to-bin mappings
      const categoryBinFallback = {
        'Plastic': 'Dry Waste / Plastic Recycling',
        'Paper': 'Paper Recycling',
        'Glass': 'Glass Recycling',
        'Metal': 'Metal Recycling',
        'Organic': 'Wet Waste / Composting',
        'E-Waste': 'Authorized E-waste Collection',
        'Hazardous': 'Appropriate Authorized Special Collection',
        'Other': 'Verification Required'
      };

      const categoryNameFallback = {
        'Plastic': 'Recyclable Waste',
        'Paper': 'Recyclable Waste',
        'Glass': 'Recyclable Waste',
        'Metal': 'Recyclable Waste',
        'Organic': 'Organic / Compostable Waste',
        'E-Waste': 'Electronic Waste',
        'Hazardous': 'Hazardous Waste',
        'Other': 'Unidentified / Other'
      };

      const binRecommendation = res.guidance?.recommended_bin || res.recommended_bin || res.guidance?.bin || categoryBinFallback[res.waste_type] || 'Verification Required';
      const category = res.guidance?.category || res.category || categoryNameFallback[res.waste_type] || 'Recyclable Waste';
      const subtype = res.guidance?.subtype || res.subtype || null;

      const whyClassification = res.guidance?.primary_method || res.guidance?.recommendation || res.guidance?.disposal_method || `Disposal recommendation for ${res.waste_type}.`;
      const recyclingMethods = res.guidance?.recycling_methods || res.recommendation?.recycling_methods || [];
      const howToDispose = res.guidance?.action_steps || res.guidance?.do || [
        'Follow local waste segregation guidelines.',
        'Ensure material is sorted cleanly before disposal.'
      ];
      const donts = res.guidance?.precautions || res.guidance?.dont || [];
      const environmentalTip = res.guidance?.environmental_impact || `Proper handling of ${res.waste_type.toLowerCase()} waste diverts recyclable materials from landfills and protects local ecosystems.`;

      setScanResult({
        id: res.id,
        type: res.waste_type,
        category,
        subtype,
        confidence: confidencePct,
        confidencePercent: `${Math.round(confidenceVal * 100)}%`,
        bin: binRecommendation,
        imagePath: res.image_path,
        guidance: res.guidance,
        recommendation: res.recommendation,
        recyclingMethods,
        isLowConfidence: res.is_low_confidence || false,
        message: res.message || null,
        modelUsed: res.model_used || null,
        whyClassification,
        howToDispose,
        donts,
        environmentalTip,
      });
    } catch (err) {
      console.error('Identification failed:', err);
      setErrorMessage(err.message || 'AI Waste classification failed. Please check backend connection.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setSelectedImage(null);
    setImageName('');
    setScanResult(null);
    setIsAnalyzing(false);
    setErrorMessage('');
  };

  const handleForwardToReport = () => {
    if (onNavigateToReport) {
      onNavigateToReport({
        wasteReportId: scanResult?.id,
        photo: getImageUrl(scanResult?.imagePath) || selectedImage,
        photoName: imageName || 'scanned-waste-item.jpg',
        wasteType: scanResult?.type || 'Plastic',
        guidance: scanResult?.guidance,
        description: `Identified as ${scanResult?.type} (${scanResult?.confidence} confidence). Recommended for ${scanResult?.bin}. ${scanResult?.whyClassification || ''}`
      });
    }
  };

  return (
    <section className="scanner-section">
      <div className="container scanner-container">
        {/* Page Heading & Subtitle */}
        <div className="scanner-header">
          <div className="badge-pill">
            <Sparkles size={14} />
            <span>AI Waste Classification</span>
          </div>
          <h1 className="page-title">Identify Your Waste</h1>
          <p className="subheading" style={{ maxWidth: '580px' }}>
            Upload a photo and find out how to dispose of it responsibly using AI guidance.
          </p>
        </div>

        {/* Error Notification Banner */}
        {errorMessage && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            backgroundColor: '#FDF7F7',
            border: '1.5px solid #EAC8C8',
            color: '#A83B3B',
            padding: '0.85rem 1.25rem',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '1.5rem',
            fontSize: '0.9rem',
            fontWeight: 500
          }}>
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Hidden File Input */}
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          accept="image/jpeg,image/png,image/webp"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileSelect(e.target.files[0]);
            }
          }}
        />

        {/* STATE 1: Upload Prompt & Drag Drop Area */}
        {!selectedImage && (
          <div 
            className={`scanner-upload-card ${dragActive ? 'drag-active' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleBrowseClick}
            style={{ cursor: 'pointer' }}
          >
            <div className="upload-icon-wrapper">
              <UploadCloud size={38} strokeWidth={1.8} />
            </div>

            <div className="upload-instructions">
              <div className="upload-main-text">
                Drop your photo here, or <span className="browse-link">browse files</span>
              </div>
              <div className="upload-subtext">
                Supports JPG, PNG, WEBP (Max 5MB)
              </div>
            </div>

            {/* Quick Demo Samples */}
            <div 
              className="sample-chips-row" 
              onClick={(e) => e.stopPropagation()}
            >
              <span className="sample-label">Or try a test image:</span>
              <button 
                type="button" 
                className="chip-btn"
                onClick={() => handleSampleSelect('/sample-bottle.jpg', 'plastic-water-bottle.jpg')}
              >
                <span>Plastic Bottle</span>
              </button>
              <button 
                type="button" 
                className="chip-btn"
                onClick={() => handleSampleSelect('/sample-report-waste.jpg', 'mixed-carton-waste.jpg')}
              >
                <span>Mixed Paper</span>
              </button>
            </div>
          </div>
        )}

        {/* STATE 2: Image Selected, Pending Analysis */}
        {selectedImage && !scanResult && !isAnalyzing && (
          <div className="scanner-preview-card">
            <div className="preview-image-box">
              <img src={selectedImage} alt="Selected waste preview" />
            </div>

            <div className="preview-info-row">
              <div className="preview-filename">
                <ImageIcon size={16} />
                <span>{imageName || 'waste-upload.jpg'}</span>
              </div>
              <span className="badge-pill" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                Ready to Classify
              </span>
            </div>

            <div className="preview-actions">
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={handleReset}
              >
                <Trash2 size={16} />
                <span>Remove</span>
              </button>

              <button 
                type="button" 
                className="btn btn-primary"
                onClick={handleAnalyze}
              >
                <Sparkles size={18} />
                <span>Analyze with AI</span>
              </button>
            </div>
          </div>
        )}

        {/* STATE 3: Loading Analysis State */}
        {isAnalyzing && (
          <div className="analysis-loader">
            <div className="spinner-sage"></div>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Analyzing your waste with AI...
              </h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                Classifying material and retrieving structured disposal guidance...
              </p>
            </div>
          </div>
        )}

        {/* STATE 4: Scan Result Display */}
        {scanResult && (
          <div className="results-card-wrapper">
            {/* Low-Confidence Advisory Alert */}
            {scanResult.isLowConfidence && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.65rem',
                backgroundColor: '#FFFBEB',
                border: '1.5px solid #FCD34D',
                color: '#92400E',
                borderRadius: 'var(--radius-sm)',
                padding: '0.9rem 1.25rem',
                marginBottom: '1rem',
                fontSize: '0.9rem',
                fontWeight: 500
              }}>
                <AlertTriangle size={20} style={{ flexShrink: 0, color: '#D97706' }} />
                <span>{scanResult.message || 'AI confidence is below verification threshold. Waste categorized as "Other". Please verify packaging or request collection.'}</span>
              </div>
            )}

            {/* 1. Main AI Analysis Result Card */}
            <div className="result-main-card">
              <div className="result-thumbnail">
                <img src={getImageUrl(scanResult.imagePath) || selectedImage} alt="Analyzed waste material" />
              </div>

              <div className="result-details">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <span className="badge-pill" style={{ backgroundColor: 'var(--bg-sage-light)' }}>
                    <ShieldCheck size={15} />
                    <span>Backend Verified AI Result</span>
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.02em' }}>
                    Report #{scanResult.id}
                  </span>
                </div>

                {/* Metric Grid: Waste Type, Category, Confidence */}
                <div className="result-metric-grid">
                  <div className="result-metric-box">
                    <div className="metric-label">Waste Type</div>
                    <div className="metric-value">{scanResult.type}</div>
                    {scanResult.subtype && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--brand-sage, #55755C)', fontWeight: 600, marginTop: '0.25rem' }}>
                        {scanResult.subtype}
                      </div>
                    )}
                  </div>
                  <div className="result-metric-box">
                    <div className="metric-label">Category</div>
                    <div className="metric-value">{scanResult.category}</div>
                  </div>
                  <div className="result-metric-box">
                    <div className="metric-label">Confidence</div>
                    <div className="metric-value">{scanResult.confidence}</div>
                  </div>
                </div>

                {/* Recommended Bin Box */}
                <div className="bin-highlight-box">
                  <div>
                    <div className="bin-highlight-title">Recommended Stream / Bin</div>
                    <div className="bin-highlight-name">{scanResult.bin}</div>
                  </div>
                  <CheckCircle size={24} className="text-sage-accent" />
                </div>

                {/* Confidence Progress Bar */}
                <div className="confidence-meter-box">
                  <div className="confidence-meter-header">
                    <span className="confidence-meter-label">
                      <Sparkles size={14} className="text-sage-accent" />
                      <span>AI Confidence Score</span>
                    </span>
                    <span className="confidence-meter-value">{scanResult.confidence} confidence</span>
                  </div>
                  <div className="confidence-track">
                    <div 
                      className="confidence-fill" 
                      style={{ width: scanResult.confidencePercent || '94%' }} 
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Section: Disposal Method */}
            <div className="why-classification-card">
              <div className="why-classification-header">
                <Info size={18} className="text-sage-accent" />
                <span>Disposal Recommendation</span>
              </div>
              <p className="why-classification-text">
                {scanResult.whyClassification}
              </p>
            </div>

            {/* Section: Recycling / Disposal Methods */}
            {scanResult.recyclingMethods && scanResult.recyclingMethods.length > 0 && (
              <div className="disposal-guide-card" style={{ borderLeft: '4px solid var(--brand-sage, #55755C)' }}>
                <h3 className="guide-title">
                  <RefreshCw size={20} className="text-sage-accent" />
                  <span>RECYCLING / DISPOSAL METHODS</span>
                </h3>

                <ul className="guide-list">
                  {scanResult.recyclingMethods.map((method, idx) => (
                    <li key={idx} className="guide-item">
                      <div className="guide-icon-bullet">
                        <span style={{ fontSize: '0.8rem', fontWeight: 700 }}>{idx + 1}</span>
                      </div>
                      <span>{method}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Section: Actionable Dos */}
            <div className="disposal-guide-card">
              <h3 className="guide-title">
                <CheckCircle size={20} className="text-sage-accent" />
                <span>Recommended Action Steps</span>
              </h3>

              <ul className="guide-list">
                {scanResult.howToDispose.map((step, idx) => (
                  <li key={idx} className="guide-item">
                    <div className="guide-icon-bullet">
                      <span style={{ fontSize: '0.8rem', fontWeight: 700 }}>{idx + 1}</span>
                    </div>
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Section: Don'ts (if provided) */}
            {scanResult.donts && scanResult.donts.length > 0 && (
              <div className="disposal-guide-card" style={{ borderLeft: '4px solid #D9534F' }}>
                <h3 className="guide-title" style={{ color: '#A83B3B' }}>
                  <XCircle size={20} color="#D9534F" />
                  <span>Important Precautions (What to Avoid)</span>
                </h3>

                <ul className="guide-list">
                  {scanResult.donts.map((warning, idx) => (
                    <li key={idx} className="guide-item">
                      <div className="guide-icon-bullet" style={{ backgroundColor: '#FDF2F2', color: '#D9534F' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700 }}>!</span>
                      </div>
                      <span style={{ color: '#555' }}>{warning}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Section: Environmental Tip */}
            <div className="environmental-tip-card">
              <div className="environmental-tip-icon-wrap">
                <Leaf size={18} strokeWidth={2.2} />
              </div>
              <div className="environmental-tip-content">
                <div className="environmental-tip-title">Environmental Impact</div>
                <p className="environmental-tip-text">
                  {scanResult.environmentalTip}
                </p>
              </div>
            </div>

            {/* Actions Bar */}
            <div className="scanner-actions-bar" style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap', marginTop: '0.5rem' }}>
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={handleReset}
              >
                <RefreshCw size={16} />
                <span>Scan Another Item</span>
              </button>

              <button 
                type="button" 
                className="btn btn-primary"
                onClick={handleForwardToReport}
              >
                <span>Request Collection for this Item</span>
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

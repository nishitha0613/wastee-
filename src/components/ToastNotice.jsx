import React from 'react';
import { Info, X } from 'lucide-react';

export default function ToastNotice({ message, onClose }) {
  if (!message) return null;

  return (
    <div className="toast-notice" role="status">
      <Info size={18} className="text-sage-accent" style={{ color: '#A3C4AA' }} />
      <span>{message}</span>
      <button 
        onClick={onClose}
        style={{ color: '#A3C4AA', display: 'flex', alignItems: 'center', marginLeft: '0.5rem' }}
        aria-label="Close notification"
      >
        <X size={16} />
      </button>
    </div>
  );
}

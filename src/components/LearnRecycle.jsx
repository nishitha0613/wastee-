import React, { useState } from 'react';
import { 
  BookOpen, 
  Apple, 
  Package, 
  FileText, 
  Wine, 
  ShieldCheck, 
  Cpu, 
  AlertTriangle, 
  Check, 
  X as CloseIcon, 
  Camera, 
  MapPin, 
  ArrowRight, 
  Sparkles, 
  RefreshCw, 
  Trash2, 
  HeartHandshake, 
  Leaf, 
  Ban,
  CheckCircle2,
  Map,
  BarChart3
} from 'lucide-react';

export default function LearnRecycle({ onNavigate, currentRole }) {
  const [activeCategory, setActiveCategory] = useState(null);

  // Section 1: Know Your Waste Categories
  const categories = [
    {
      id: 'organic',
      name: 'Organic Waste',
      shortDesc: 'Food scraps, plant trimmings, and natural biodegradable matter.',
      icon: Apple,
      recyclableStatus: 'Compostable',
      recyclableBadgeClass: 'status-badge-resolved',
      whatItIs: 'Organic waste is biodegradable material originating from plants, animals, or natural produce that decomposes naturally through microbial action.',
      commonExamples: [
        'Vegetable peelings and fruit scraps',
        'Leftover cooked meals and bread crusts',
        'Coffee grounds and unbleached tea bags',
        'Garden trimmings, leaves, and cut flowers',
        'Eggshells and nut shells'
      ],
      disposalGuide: 'Separate in a ventilated green bin or kitchen caddy. Do not bag in plastic. Compost at home or send to municipal community composting streams.'
    },
    {
      id: 'plastic',
      name: 'Plastic',
      shortDesc: 'Beverage bottles, rigid containers, wraps, and clean polymers.',
      icon: Package,
      recyclableStatus: 'Recyclable (PET #1, HDPE #2, PP #5)',
      recyclableBadgeClass: 'status-badge-resolved',
      whatItIs: 'Synthetic polymers molded into packaging, beverage bottles, and containers. Many standard plastics can be mechanically shredded and pelletized into new items.',
      commonExamples: [
        'Water and soda bottles (PET #1)',
        'Milk jugs and shampoo bottles (HDPE #2)',
        'Yogurt tubs and food takeout boxes (PP #5)',
        'Plastic bottle caps and clean jars'
      ],
      disposalGuide: 'Empty liquids and rinse clean of food residue. Flatten bottles to save bin space. Deposit in the dry recyclable waste stream.'
    },
    {
      id: 'paper',
      name: 'Paper',
      shortDesc: 'Cardboard cartons, newsprint, office documents, and clean packaging.',
      icon: FileText,
      recyclableStatus: '100% Recyclable',
      recyclableBadgeClass: 'status-badge-resolved',
      whatItIs: 'Wood-pulp cellulose fibers rolled into sheets, cardboard, and packaging. Paper can be re-pulped up to 5–7 times to produce recycled paper goods.',
      commonExamples: [
        'Corrugated shipping boxes and cartons',
        'Newspapers, magazines, and paperbacks',
        'Office copier paper and notebooks',
        'Cardboard egg cartons and paper bags'
      ],
      disposalGuide: 'Keep paper completely dry and free from grease or food oil (greasy pizza boxes belong in compost). Flatten boxes and bundle neatly.'
    },
    {
      id: 'glass',
      name: 'Glass',
      shortDesc: 'Jars, beverage bottles, and containers that can be melted endlessly.',
      icon: Wine,
      recyclableStatus: 'Infinitely Recyclable',
      recyclableBadgeClass: 'status-badge-resolved',
      whatItIs: 'Silica-based rigid containers that can be melted down and re-cast infinitely without any loss of purity, strength, or structural quality.',
      commonExamples: [
        'Clear, green, and amber beverage bottles',
        'Food jars (jam, pasta sauce, pickles)',
        'Glass cosmetic containers'
      ],
      disposalGuide: 'Rinse out leftovers. Remove plastic pumps or metal rings. Place into dry waste glass stream. Never mix with ceramic dishes or window glass.'
    },
    {
      id: 'metal',
      name: 'Metal',
      shortDesc: 'Aluminum drink cans, food tins, tin foil, and household hardware.',
      icon: ShieldCheck,
      recyclableStatus: 'Highly Recyclable',
      recyclableBadgeClass: 'status-badge-resolved',
      whatItIs: 'Ferrous and non-ferrous metals like aluminum and tin-plated steel that retain 100% of their elemental properties when smelted and remanufactured.',
      commonExamples: [
        'Aluminum soda and beverage cans',
        'Canned soup and vegetable tins',
        'Clean aluminum baking foil and trays',
        'Metal lids, crowns, and bottle caps'
      ],
      disposalGuide: 'Rinse food residue to deter pests. Empty aerosols completely before disposal. Place cleanly in the dry metal recycling stream.'
    },
    {
      id: 'ewaste',
      name: 'E-waste',
      shortDesc: 'Discarded electronics, charging cables, batteries, and circuit boards.',
      icon: Cpu,
      recyclableStatus: 'Specialized E-Waste Processing',
      recyclableBadgeClass: 'status-badge-in-progress',
      whatItIs: 'Electrical items containing printed circuit boards, heavy metals, and lithium batteries that require certified dismantling to prevent environmental leaching.',
      commonExamples: [
        'Old smartphones, laptops, and tablets',
        'Power adapters, charging cords, and USB cables',
        'Alkaline and lithium-ion batteries',
        'Broken computer mice and keyboards'
      ],
      disposalGuide: 'Never discard in household dry or wet bins. Drop off at designated municipal e-waste collection drives or authorized retailer take-back kiosks.'
    },
    {
      id: 'hazardous',
      name: 'Hazardous Waste',
      shortDesc: 'Chemicals, flammable solvents, paints, and medical materials.',
      icon: AlertTriangle,
      recyclableStatus: 'Hazardous Treatment Required',
      recyclableBadgeClass: 'status-badge-pending',
      whatItIs: 'Substances that pose substantial health or environmental risks due to toxic, corrosive, reactive, or flammable chemical properties.',
      commonExamples: [
        'Paint thinners, varnishes, and motor oils',
        'Pesticides, weedkillers, and harsh drain cleaners',
        'Fluorescent tube light bulbs (contain mercury vapor)',
        'Expired medications, syringes, and clinical waste'
      ],
      disposalGuide: 'Keep in original sealed containers with legible labels. Take directly to certified hazardous waste disposal facilities or pharmacy medicine dropboxes.'
    }
  ];

  // Section 2: Waste Segregation Guide
  const segregationStreams = [
    {
      title: 'Wet Waste',
      color: '#436B4A',
      bgColor: '#EAF3EB',
      borderColor: '#C2DEC6',
      badgeText: 'Green Stream',
      examples: 'Food scraps, vegetable peels, leftover meals, coffee grounds, eggshells, garden leaves',
      disposalTip: 'Compost naturally; avoid plastic liners.'
    },
    {
      title: 'Dry Waste',
      color: '#346182',
      bgColor: '#EBF2F8',
      borderColor: '#BED3E5',
      badgeText: 'Blue Stream',
      examples: 'Paper, cardboard, plastic bottles, containers, clean glass jars, aluminum cans',
      disposalTip: 'Keep clean and dry to ensure recyclability.'
    },
    {
      title: 'E-waste',
      color: '#8A5D19',
      bgColor: '#FAF1E3',
      borderColor: '#E8D4B5',
      badgeText: 'Amber Stream',
      examples: 'Phones, laptops, chargers, cables, batteries, computer accessories, small appliances',
      disposalTip: 'Drop off at authorized e-waste collection centers.'
    },
    {
      title: 'Hazardous Waste',
      color: '#8A3333',
      bgColor: '#FBECEB',
      borderColor: '#EDCECE',
      badgeText: 'Red Stream',
      examples: 'Paints, chemical solvents, batteries, expired medicines, fluorescent bulbs, motor oil',
      disposalTip: 'Handle with care; deliver to certified toxic disposal.'
    }
  ];

  // Section 3: Do's and Don'ts
  const dos = [
    'Separate wet and dry waste at the source in distinct bins',
    'Rinse and dry recyclable plastic, glass, and metal containers',
    'Reuse sturdy packaging, bottles, and cloth bags whenever possible',
    'Dispose of e-waste and batteries at designated collection dropboxes'
  ];

  const donts = [
    'Mix hazardous chemicals or medical items with regular household waste',
    'Throw lithium batteries or electronics into normal municipal trash bins',
    'Burn plastic packaging or yard waste which releases toxic carcinogens',
    'Dump waste in open public spaces, drains, or street corners'
  ];

  // Section 4: Practical Recycling Tips
  const tips = [
    {
      id: 1,
      title: 'Reuse before recycling',
      desc: 'Give jars, boxes, and containers a second purpose before placing them in the recycle stream.',
      icon: RefreshCw,
    },
    {
      id: 2,
      title: 'Avoid single-use plastic',
      desc: 'Carry a reusable water bottle and cloth shopping bag to prevent non-biodegradable waste at the root.',
      icon: Ban,
    },
    {
      id: 3,
      title: 'Compost organic waste',
      desc: 'Turn kitchen peels and coffee grounds into rich organic soil for plants instead of landfilling.',
      icon: Leaf,
    },
    {
      id: 4,
      title: 'Donate usable items',
      desc: 'Old clothing, working electronics, and books can find a second home through local donation hubs.',
      icon: HeartHandshake,
    },
    {
      id: 5,
      title: 'Use e-waste centers',
      desc: 'Always hand over dead gadgets to authorized recyclers who safely recover copper, gold, and silicon.',
      icon: Cpu,
    },
  ];

  return (
    <section className="learn-section">
      <div className="container learn-container">
        {/* Page Header */}
        <div className="learn-header">
          <div className="badge-pill">
            <BookOpen size={14} />
            <span>Community Knowledge Hub</span>
          </div>
          <h1 className="page-title">Learn & Recycle</h1>
          <p className="subheading" style={{ maxWidth: '600px' }}>
            Learn how to separate, recycle, and dispose of waste responsibly.
          </p>
        </div>

        {/* SECTION 1 — Know Your Waste */}
        <div className="learn-block">
          <div className="learn-block-header">
            <h2 className="learn-block-title">Know Your Waste</h2>
            <p className="subheading" style={{ fontSize: '1rem' }}>
              Understand common materials and their environmental footprint. Click any card for detailed disposal instructions.
            </p>
          </div>

          <div className="category-cards-grid">
            {categories.map((cat) => {
              const IconComp = cat.icon;
              return (
                <div 
                  key={cat.id} 
                  className="category-card"
                  onClick={() => setActiveCategory(cat)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div className="category-icon-wrap">
                      <IconComp size={22} strokeWidth={2} />
                    </div>
                    <span className={`status-badge ${cat.recyclableBadgeClass}`}>
                      {cat.recyclableStatus.split(' ')[0]}
                    </span>
                  </div>

                  <div>
                    <h3 className="category-card-name">{cat.name}</h3>
                    <p className="category-card-desc">{cat.shortDesc}</p>
                  </div>

                  <div className="category-card-link">
                    <span>Learn More</span>
                    <ArrowRight size={14} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* SECTION 2 — Waste Segregation Guide */}
        <div className="learn-block">
          <div className="learn-block-header">
            <h2 className="learn-block-title">Waste Segregation Guide</h2>
            <p className="subheading" style={{ fontSize: '1rem' }}>
              Proper segregation at source is the most critical step for zero-waste communities.
            </p>
          </div>

          <div className="segregation-grid">
            {segregationStreams.map((stream) => (
              <div 
                key={stream.title} 
                className="segregation-card"
                style={{ borderColor: stream.borderColor }}
              >
                <div 
                  className="segregation-stream-badge"
                  style={{ backgroundColor: stream.bgColor, color: stream.color }}
                >
                  <span>{stream.badgeText}</span>
                </div>

                <h3 className="segregation-title">{stream.title}</h3>

                <div className="segregation-examples-box">
                  <strong style={{ display: 'block', marginBottom: '0.25rem', color: 'var(--text-primary)' }}>Examples:</strong>
                  <span>{stream.examples}</span>
                </div>

                <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginTop: 'auto' }}>
                  <strong>Tip:</strong> {stream.disposalTip}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* SECTION 3 — Do's and Don'ts */}
        <div className="learn-block">
          <div className="learn-block-header">
            <h2 className="learn-block-title">Do's and Don'ts</h2>
            <p className="subheading" style={{ fontSize: '1rem' }}>
              Simple community ground rules to build sustainable habits every day.
            </p>
          </div>

          <div className="dos-donts-grid">
            {/* DO Card */}
            <div className="dodont-card do-card">
              <div className="dodont-header do-header">
                <CheckCircle2 size={24} />
                <span>DO</span>
              </div>
              <ul className="dodont-list">
                {dos.map((item, i) => (
                  <li key={i} className="dodont-item">
                    <div className="dodont-bullet-do">
                      <Check size={14} strokeWidth={2.5} />
                    </div>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* DON'T Card */}
            <div className="dodont-card dont-card">
              <div className="dodont-header dont-header">
                <Ban size={24} />
                <span>DON'T</span>
              </div>
              <ul className="dodont-list">
                {donts.map((item, i) => (
                  <li key={i} className="dodont-item">
                    <div className="dodont-bullet-dont">
                      <CloseIcon size={14} strokeWidth={2.5} />
                    </div>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* SECTION 4 — Recycling Tips */}
        <div className="learn-block">
          <div className="learn-block-header">
            <h2 className="learn-block-title">Practical Recycling Tips</h2>
            <p className="subheading" style={{ fontSize: '1rem' }}>
              Everyday sustainable actions with lasting environmental impact.
            </p>
          </div>

          <div className="tips-grid">
            {tips.map((tip) => {
              const TipIcon = tip.icon;
              return (
                <div key={tip.id} className="tip-card">
                  <div className="tip-icon-wrap">
                    <TipIcon size={18} strokeWidth={2} />
                  </div>
                  <h3 className="tip-title">{tip.title}</h3>
                  <p className="tip-desc">{tip.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* SECTION 5 — Call to Action */}
        <div className="learn-cta-card">
          <div className="badge-pill" style={{ backgroundColor: 'rgba(255,255,255,0.18)', color: '#FFFFFF', border: '1px solid rgba(255,255,255,0.25)' }}>
            <Sparkles size={14} />
            <span>Take Action Today</span>
          </div>

          <h2 className="learn-cta-title">Ready to make a difference?</h2>

          <p className="learn-cta-desc">
            {currentRole === 'admin' 
              ? 'Explore municipal hotspot surveillance to inspect high-density accumulation areas, or monitor district resolution trends in Analytics.'
              : 'Use our AI Waste Scanner to instantly classify items, or report roadside waste hotspots to help local cleanup crews.'}
          </p>

          <div className="learn-cta-buttons">
            {currentRole === 'admin' ? (
              <>
                <button 
                  className="btn" 
                  style={{ backgroundColor: '#FFFFFF', color: 'var(--sage-800)', fontWeight: 700 }}
                  onClick={() => onNavigate('Waste Map')}
                >
                  <Map size={18} />
                  <span>View Hotspot Map</span>
                </button>

                <button 
                  className="btn btn-outline" 
                  style={{ borderColor: '#FFFFFF', color: '#FFFFFF', backgroundColor: 'transparent' }}
                  onClick={() => onNavigate('Analytics')}
                >
                  <BarChart3 size={18} />
                  <span>View Analytics</span>
                </button>
              </>
            ) : (
              <>
                <button 
                  className="btn" 
                  style={{ backgroundColor: '#FFFFFF', color: 'var(--sage-800)', fontWeight: 700 }}
                  onClick={() => onNavigate('Waste Scanner')}
                >
                  <Camera size={18} />
                  <span>Scan Your Waste</span>
                </button>

                <button 
                  className="btn btn-outline" 
                  style={{ borderColor: '#FFFFFF', color: '#FFFFFF', backgroundColor: 'transparent' }}
                  onClick={() => onNavigate('Report Waste')}
                >
                  <MapPin size={18} />
                  <span>Report Waste</span>
                </button>
              </>
            )}
          </div>
        </div>

        {/* Modal: Category Expanded Detail View */}
        {activeCategory && (
          <div className="modal-overlay" onClick={() => setActiveCategory(null)}>
            <div className="detail-modal-card" onClick={(e) => e.stopPropagation()}>
              {/* Modal Header */}
              <div className="detail-modal-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <div className="category-icon-wrap">
                    {React.createElement(activeCategory.icon, { size: 24, strokeWidth: 2 })}
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-muted)', fontWeight: 700 }}>
                      Material Guide
                    </span>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {activeCategory.name}
                    </h2>
                  </div>
                </div>

                <button 
                  type="button" 
                  className="detail-close-btn"
                  onClick={() => setActiveCategory(null)}
                  aria-label="Close modal"
                >
                  <CloseIcon size={18} />
                </button>
              </div>

              {/* Recyclability Status Badge */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--bg-main)', padding: '0.9rem 1.25rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Recyclability Status:
                </span>
                <span className={`status-badge ${activeCategory.recyclableBadgeClass}`} style={{ fontSize: '0.85rem' }}>
                  {activeCategory.recyclableStatus}
                </span>
              </div>

              {/* What It Is */}
              <div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
                  What It Is
                </h4>
                <p style={{ fontSize: '0.925rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {activeCategory.whatItIs}
                </p>
              </div>

              {/* Common Examples */}
              <div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                  Common Examples
                </h4>
                <ul style={{ display: 'grid', gridTemplateColumns: 'repeat(1, 1fr)', gap: '0.4rem', listStyle: 'none', paddingLeft: 0 }}>
                  {activeCategory.commonExamples.map((ex, idx) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                      <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: 'var(--sage-600)' }} />
                      <span>{ex}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* How to Dispose of It */}
              <div style={{ backgroundColor: 'var(--bg-sage-light)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--sage-900)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Sparkles size={16} />
                  <span>How to Dispose of It</span>
                </h4>
                <p style={{ fontSize: '0.9rem', color: 'var(--sage-800)', lineHeight: 1.6 }}>
                  {activeCategory.disposalGuide}
                </p>
              </div>

              {/* Modal Footer */}
              <div className="detail-modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setActiveCategory(null)}
                >
                  Close
                </button>

                {currentRole !== 'admin' && (
                  <button 
                    type="button" 
                    className="btn btn-primary"
                    onClick={() => {
                      setActiveCategory(null);
                      onNavigate('Waste Scanner');
                    }}
                  >
                    <Camera size={16} />
                    <span>Scan {activeCategory.name} Item</span>
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

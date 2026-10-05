import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Stats from './components/Stats';
import HowItWorks from './components/HowItWorks';
import WasteScanner from './components/WasteScanner';
import ReportWaste from './components/ReportWaste';
import MyReports from './components/MyReports';
import WasteMap from './components/WasteMap';
import Dashboard from './components/Dashboard';
import AllReports from './components/AllReports';
import Analytics from './components/Analytics';
import EnvironmentalImpact from './components/EnvironmentalImpact';
import LearnRecycle from './components/LearnRecycle';
import Footer from './components/Footer';
import ToastNotice from './components/ToastNotice';
import LoginRoleSelect from './components/LoginRoleSelect';
import AdminAccessGuard from './components/AdminAccessGuard';
import { authApi, authStorage } from './services/api';

const DEFAULT_REPORTS = [
  {
    id: 'EC-10482',
    wasteType: 'Plastic Waste',
    location: 'MG Road',
    date: '20 Sep 2026',
    status: 'Resolved',
    severity: 'Medium',
    image: '/sample-bottle.jpg',
    description: 'Recyclable beverage bottles found clustered near the public transit stop.',
    currentStage: 4,
  },
  {
    id: 'EC-10481',
    wasteType: 'Mixed Waste',
    location: 'Indiranagar',
    date: '19 Sep 2026',
    status: 'In Progress',
    severity: 'High',
    image: '/sample-report-waste.jpg',
    description: 'Accumulated mixed cardboard packaging and unsegregated domestic refuse.',
    currentStage: 3,
  },
  {
    id: 'EC-10480',
    wasteType: 'E-waste',
    location: 'Whitefield',
    date: '18 Sep 2026',
    status: 'Pending',
    severity: 'Low',
    image: '/sample-bottle.jpg',
    description: 'Discarded electronics and computer cables placed by sidewalk curb.',
    currentStage: 1,
  },
];

const TAB_HASHES = {
  'Home': '#home',
  'Waste Scanner': '#scanner',
  'Report Waste': '#report',
  'My Reports': '#my-reports',
  'Waste Map': '#map',
  'Dashboard': '#dashboard',
  'All Reports': '#all-reports',
  'Analytics': '#analytics',
  'Environmental Impact': '#impact',
  'Learn & Recycle': '#learn',
};

const HASH_TO_TAB = {
  '#home': 'Home',
  '': 'Home',
  '#': 'Home',
  '#scanner': 'Waste Scanner',
  '#report': 'Report Waste',
  '#my-reports': 'My Reports',
  '#map': 'Waste Map',
  '#dashboard': 'Dashboard',
  '#all-reports': 'All Reports',
  '#analytics': 'Analytics',
  '#impact': 'Environmental Impact',
  '#learn': 'Learn & Recycle',
};

export default function App() {
  // Selected role: 'user' | 'admin' | null
  const [currentUser, setCurrentUser] = useState(() => {
    const token = authStorage.getToken();
    return token ? authStorage.getUser() : null;
  });
  const [currentRole, setCurrentRole] = useState(() => {
    const token = authStorage.getToken();
    return token ? authStorage.getRole() : null;
  });

  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== 'undefined' && window.location.hash) {
      const target = HASH_TO_TAB[window.location.hash] || 'Home';
      return target;
    }
    return 'Home';
  });

  const [toastMessage, setToastMessage] = useState(null);
  const [prefilledReport, setPrefilledReport] = useState(null);

  // Verify real JWT session against backend on mount
  React.useEffect(() => {
    const token = authStorage.getToken();
    if (token) {
      authApi.getMe()
        .then((user) => {
          setCurrentUser(user);
          setCurrentRole(user.role);
          authStorage.setUser(user);
        })
        .catch((err) => {
          console.warn('Stored token is invalid or expired:', err);
          authStorage.clear();
          setCurrentUser(null);
          setCurrentRole(null);
          setToastMessage('Session expired. Please log in again.');
          setTimeout(() => setToastMessage(null), 4000);
        });
    } else {
      authStorage.clear();
      setCurrentUser(null);
      setCurrentRole(null);
    }

    // Listen for unauthorized 401 events from API layer
    const handleUnauthorized = () => {
      authStorage.clear();
      setCurrentRole(null);
      setCurrentUser(null);
      setToastMessage('Session expired. Please log in again.');
      setTimeout(() => setToastMessage(null), 4000);
    };

    window.addEventListener('ecocycle_unauthorized', handleUnauthorized);
    return () => window.removeEventListener('ecocycle_unauthorized', handleUnauthorized);
  }, []);

  // Initialize reports from localStorage with fallback to DEFAULT_REPORTS
  const [reports, setReports] = useState(() => {
    try {
      const saved = localStorage.getItem('ecocycle_reports_v1');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) return parsed;
      }
    } catch (err) {
      console.warn('Could not read reports from localStorage:', err);
    }
    return DEFAULT_REPORTS;
  });

  // Ensure Admin cannot land on citizen-only views
  React.useEffect(() => {
    if (currentRole === 'admin') {
      const citizenOnlyTabs = ['Waste Scanner', 'Report Waste', 'My Reports', 'Home'];
      if (citizenOnlyTabs.includes(activeTab)) {
        setActiveTab('Dashboard');
        if (window.location.hash !== '#dashboard') {
          window.history.replaceState(null, '', '#dashboard');
        }
      }
    }
  }, [currentRole, activeTab]);

  // Sync reports to localStorage on change
  React.useEffect(() => {
    try {
      localStorage.setItem('ecocycle_reports_v1', JSON.stringify(reports));
    } catch (err) {
      console.warn('Could not save reports to localStorage:', err);
    }
  }, [reports]);

  // Handle browser back/forward buttons and hash navigation
  React.useEffect(() => {
    const handlePopState = () => {
      let tab = HASH_TO_TAB[window.location.hash] || 'Home';
      if (currentRole === 'admin' && (tab === 'Home' || tab === 'Waste Scanner' || tab === 'Report Waste' || tab === 'My Reports')) {
        tab = 'Dashboard';
      }
      setActiveTab(tab);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    window.addEventListener('popstate', handlePopState);
    window.addEventListener('hashchange', handlePopState);
    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('hashchange', handlePopState);
    };
  }, [currentRole]);

  const handleLoginSuccess = (user, role) => {
    setCurrentUser(user);
    setCurrentRole(role);
    if (role === 'admin') {
      handleNavigation('Dashboard');
      setToastMessage(`Welcome back, Administrator ${user?.name || ''}!`);
    } else {
      handleNavigation('Home');
      setToastMessage(`Welcome back, ${user?.name || 'Citizen'}!`);
    }
    setTimeout(() => setToastMessage(null), 4000);
  };

  const handleLogout = () => {
    authStorage.clear();
    setCurrentRole(null);
    setCurrentUser(null);
    window.location.hash = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setToastMessage("Logged out successfully.");
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleNavigation = (tabName) => {
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Protect administrator from citizen-only pages
    if (currentRole === 'admin') {
      const citizenOnlyTabs = [
        'Scan Waste', 'Waste Scanner', 'Scan', 'Scan Your Waste', 'Get Started',
        'Report Waste', 'Report a Location', 'Report',
        'My Reports', 'View My Reports',
        'Home', '/'
      ];
      if (citizenOnlyTabs.includes(tabName)) {
        setActiveTab('Dashboard');
        if (window.location.hash !== '#dashboard') {
          window.history.pushState(null, '', '#dashboard');
        }
        return;
      }
    }

    let resolvedTab = 'Home';

    // Canonical Navigation Router
    if (
      tabName === 'Scan Waste' || 
      tabName === 'Waste Scanner' || 
      tabName === 'Scan' || 
      tabName === 'Scan Your Waste' ||
      tabName === 'Get Started'
    ) {
      resolvedTab = 'Waste Scanner';
    } else if (
      tabName === 'Report Waste' || 
      tabName === 'Report a Location' || 
      tabName === 'Report'
    ) {
      resolvedTab = 'Report Waste';
    } else if (
      tabName === 'My Reports' || 
      tabName === 'View My Reports'
    ) {
      resolvedTab = 'My Reports';
    } else if (
      tabName === 'Waste Map' || 
      tabName === 'Hotspot Map' || 
      tabName === 'View Map'
    ) {
      resolvedTab = 'Waste Map';
    } else if (
      tabName === 'Dashboard' || 
      tabName === 'Community Dashboard' ||
      tabName === 'View Live Dashboard' || 
      tabName === 'Track'
    ) {
      resolvedTab = 'Dashboard';
    } else if (
      tabName === 'All Reports' ||
      tabName === 'AllReports' ||
      tabName === 'Reports Management'
    ) {
      resolvedTab = 'All Reports';
    } else if (
      tabName === 'Analytics' ||
      tabName === 'Waste Analytics'
    ) {
      resolvedTab = 'Analytics';
    } else if (
      tabName === 'Environmental Impact' ||
      tabName === 'Impact' ||
      tabName === 'Impact Report'
    ) {
      resolvedTab = 'Environmental Impact';
    } else if (
      tabName === 'Learn & Recycle' || 
      tabName === 'Recycling Guide' || 
      tabName === 'Recycling Guidelines' ||
      tabName === 'Learn'
    ) {
      resolvedTab = 'Learn & Recycle';
    } else if (
      tabName === 'Home' || 
      tabName === '/'
    ) {
      resolvedTab = 'Home';
    } else if (tabName === 'Support') {
      setToastMessage("EcoCycle Community Support: Reach municipal dispatch at support@ecocycle.org.");
      setTimeout(() => setToastMessage(null), 4000);
      return;
    } else {
      resolvedTab = tabName;
      setToastMessage(`"${tabName}" information will be displayed soon.`);
      setTimeout(() => {
        setToastMessage((prev) => (prev && prev.includes(tabName) ? null : prev));
      }, 4000);
    }

    setActiveTab(resolvedTab);
    const targetHash = TAB_HASHES[resolvedTab] || '#home';
    if (window.location.hash !== targetHash) {
      window.history.pushState(null, '', targetHash);
    }
  };

  const handleAddReport = (newReport) => {
    setReports((prev) => [newReport, ...prev]);
  };

  const handleUpdateReportStatus = (reportId, newStatus) => {
    const stageMap = { 'Pending': 1, 'In Progress': 3, 'Resolved': 4 };
    setReports((prev) =>
      prev.map((r) =>
        r.id === reportId
          ? { ...r, status: newStatus, currentStage: stageMap[newStatus] || r.currentStage }
          : r
      )
    );
  };

  const handleResetDefaultReports = () => {
    setReports(DEFAULT_REPORTS);
    setToastMessage('Reset demo reports to initial state.');
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleClearAllReports = () => {
    setReports([]);
    setToastMessage('Cleared all reports to demonstrate empty state.');
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleNavigateToReportFromScanner = (scannerData) => {
    setPrefilledReport(scannerData);
    handleNavigation('Report Waste');
  };

  const handleViewMyReports = (reportId) => {
    handleNavigation('My Reports');
    setToastMessage(`Showing your reported issue (${reportId}) in My Reports tracking portal.`);
    setTimeout(() => {
      setToastMessage(null);
    }, 4500);
  };

  const resolvedCount = reports.filter((r) => r.status === 'Resolved').length;
  const activeHotspotsCount = reports.filter((r) => r.status === 'Pending' || r.status === 'In Progress').length;

  // Check if current user is restricted from administrator-only sections
  const isAdminOnlyPage = 
    activeTab === 'Dashboard' || 
    activeTab === 'Waste Map' || 
    activeTab === 'All Reports' || 
    activeTab === 'Analytics' || 
    activeTab === 'Environmental Impact';
  const isAccessRestricted = currentRole === 'user' && isAdminOnlyPage;

  // If no role is selected yet, render the Welcome / Role Selection page
  if (!currentRole) {
    return (
      <div className="app-root">
        <LoginRoleSelect 
          onLoginSuccess={handleLoginSuccess}
        />
        <ToastNotice 
          message={toastMessage} 
          onClose={() => setToastMessage(null)} 
        />
      </div>
    );
  }

  return (
    <div className="app-root">
      <Navbar 
        activeTab={activeTab} 
        onNavigate={handleNavigation} 
        currentRole={currentRole}
        currentUser={currentUser}
        onLogout={handleLogout}
      />
      
      <main>
        {isAccessRestricted ? (
          <AdminAccessGuard 
            onNavigate={handleNavigation}
            attemptedTab={activeTab}
          />
        ) : activeTab === 'Waste Scanner' ? (
          <WasteScanner onNavigateToReport={handleNavigateToReportFromScanner} />
        ) : activeTab === 'Report Waste' ? (
          <ReportWaste 
            initialData={prefilledReport}
            onViewMyReports={handleViewMyReports} 
            onAddReport={handleAddReport}
          />
        ) : activeTab === 'My Reports' ? (
          <MyReports 
            reports={reports} 
            onNavigate={handleNavigation} 
            onUpdateStatus={handleUpdateReportStatus}
            onResetDemoReports={handleResetDefaultReports}
            onClearReports={handleClearAllReports}
            currentRole={currentRole}
          />
        ) : activeTab === 'Waste Map' ? (
          <WasteMap onNavigate={handleNavigation} />
        ) : activeTab === 'Dashboard' ? (
          <Dashboard reports={reports} onNavigate={handleNavigation} />
        ) : activeTab === 'All Reports' ? (
          <AllReports 
            reports={reports} 
            onNavigate={handleNavigation} 
            onUpdateStatus={handleUpdateReportStatus}
          />
        ) : activeTab === 'Analytics' ? (
          <Analytics reports={reports} onNavigate={handleNavigation} />
        ) : activeTab === 'Environmental Impact' ? (
          <EnvironmentalImpact onNavigate={handleNavigation} />
        ) : activeTab === 'Learn & Recycle' ? (
          <LearnRecycle onNavigate={handleNavigation} currentRole={currentRole} />
        ) : (
          <>
            <Hero 
              onAction={handleNavigation} 
            />
            <Stats 
              wasteCollected={0}
              recycled={0}
              resolvedCount={resolvedCount}
              activeCount={activeHotspotsCount}
            />
            <HowItWorks 
              onAction={handleNavigation} 
              currentRole={currentRole}
            />
          </>
        )}
      </main>

      <Footer 
        onNavigate={handleNavigation} 
        currentRole={currentRole}
      />

      <ToastNotice 
        message={toastMessage} 
        onClose={() => setToastMessage(null)} 
      />
    </div>
  );
}

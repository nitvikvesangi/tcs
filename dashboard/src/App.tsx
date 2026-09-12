import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { AIChatbot } from './components/AIChatbot';
import { ToastContainer } from './components/Toast';

import { Dashboard } from './pages/Dashboard';
import { Recommendations } from './pages/Recommendations';
import { Inventory } from './pages/Inventory';
import { Promotions } from './pages/Promotions';
import { Analytics } from './pages/Analytics';

const AppLayout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const location = useLocation();

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/': return 'Dashboard';
      case '/recommendations': return 'AI Recommendations';
      case '/inventory': return 'Inventory Intelligence';
      case '/promotions': return 'Promotion Planner';
      case '/analytics': return 'Analytics';
      default: return 'QuickAI';
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      <Sidebar isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />
      
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header title={getPageTitle()} toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />
        
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <div className="max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/recommendations" element={<Recommendations />} />
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/promotions" element={<Promotions />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </div>
        </main>
      </div>

      <AIChatbot />
      <ToastContainer />
    </div>
  );
};

function App() {
  return (
    <AppProvider>
      <Router>
        <AppLayout />
      </Router>
    </AppProvider>
  );
}

export default App;

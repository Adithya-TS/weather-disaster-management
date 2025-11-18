import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './context/ThemeContext';
import { LoadingProvider } from './context/LoadingContext';
import { SessionProvider } from './context/SessionContext';
import NavBar from './components/layout/NavBar';
import SideBar from './components/layout/SideBar';
import Loader from './components/ui/Loader';
import { useLoading } from './context/LoadingContext';

// Pages
import Home from './pages/Home';
import Weather from './pages/Weather';
import SocialMedia from './pages/SocialMedia';
import Analysis from './pages/Analysis';
import ResponsePlan from './pages/ResponsePlan';
import Sessions from './pages/Sessions';

const AppContent = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { loading, loadingMessage } = useLoading();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <NavBar onMenuClick={() => setSidebarOpen(true)} />
      <div className="flex">
        <SideBar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 lg:ml-64">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/weather" element={<Weather />} />
            <Route path="/social-media" element={<SocialMedia />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/response-plan" element={<ResponsePlan />} />
            <Route path="/sessions" element={<Sessions />} />
          </Routes>
        </main>
      </div>
      {loading && <Loader fullScreen message={loadingMessage} />}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'var(--toast-bg, #fff)',
            color: 'var(--toast-color, #333)',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <LoadingProvider>
        <SessionProvider>
          <Router>
            <AppContent />
          </Router>
        </SessionProvider>
      </LoadingProvider>
    </ThemeProvider>
  );
}

export default App;


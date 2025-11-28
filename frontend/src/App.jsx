import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './context/ThemeContext';
import { LoadingProvider } from './context/LoadingContext';
import { SessionProvider } from './context/SessionContext';
import { AuthProvider } from './context/AuthContext';
import NavBar from './components/layout/NavBar';
import SideBar from './components/layout/SideBar';
import Loader from './components/ui/Loader';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { useLoading } from './context/LoadingContext';
import { useAuth } from './context/AuthContext';

// Pages
import Home from './pages/Home';
import Weather from './pages/Weather';
import Alerts from './pages/Alerts';
import SocialMedia from './pages/SocialMedia';
import Analysis from './pages/Analysis';
import ResponsePlan from './pages/ResponsePlan';
import Sessions from './pages/Sessions';
import Login from './pages/Login';
import ChatHistory from './pages/ChatHistory';
import RoutePlanning from './pages/RoutePlanning';
import SeismicMonitor from './pages/SeismicMonitor';

const AppContent = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { loading, loadingMessage } = useLoading();
  const { isAuthenticated, loading: authLoading } = useAuth();

  // Show loading while checking authentication
  if (authLoading) {
    return <Loader fullScreen message="Loading..." />;
  }

  // Show login page if not authenticated (except for login route)
  const showLayout = isAuthenticated();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {showLayout && <NavBar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />}
      <div className="flex">
        {showLayout && <SideBar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />}
        <main className={showLayout ? "flex-1 lg:ml-64 pt-16" : "flex-1"}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Home />
                </ProtectedRoute>
              }
            />
            <Route
              path="/weather"
              element={
                <ProtectedRoute>
                  <Weather />
                </ProtectedRoute>
              }
            />
            <Route
              path="/alerts"
              element={
                <ProtectedRoute>
                  <Alerts />
                </ProtectedRoute>
              }
            />
            <Route
              path="/route-planning"
              element={
                <ProtectedRoute>
                  <RoutePlanning />
                </ProtectedRoute>
              }
            />
            <Route
              path="/seismic-monitor"
              element={
                <ProtectedRoute>
                  <SeismicMonitor />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analysis"
              element={
                <ProtectedRoute>
                  <Analysis />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analysis"
              element={
                <ProtectedRoute>
                  <Analysis />
                </ProtectedRoute>
              }
            />
            <Route
              path="/response-plan"
              element={
                <ProtectedRoute>
                  <ResponsePlan />
                </ProtectedRoute>
              }
            />
            <Route
              path="/sessions"
              element={
                <ProtectedRoute>
                  <Sessions />
                </ProtectedRoute>
              }
            />
            <Route
              path="/chat-history"
              element={
                <ProtectedRoute>
                  <ChatHistory />
                </ProtectedRoute>
              }
            />
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
        <AuthProvider>
          <SessionProvider>
            <Router>
              <AppContent />
            </Router>
          </SessionProvider>
        </AuthProvider>
      </LoadingProvider>
    </ThemeProvider>
  );
}

export default App;


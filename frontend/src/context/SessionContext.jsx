import { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';

const SessionContext = createContext();

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within SessionProvider');
  }
  return context;
};

export const SessionProvider = ({ children }) => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchSessions = async (limit = 10) => {
    setLoading(true);
    try {
      const response = await apiService.getSessions(limit);
      // Handle API response - ensure we always get an array
      const sessionsData = response.data;
      if (Array.isArray(sessionsData)) {
        setSessions(sessionsData);
      } else if (sessionsData?.sessions && Array.isArray(sessionsData.sessions)) {
        setSessions(sessionsData.sessions);
      } else {
        // If API returns object with message (current implementation), return empty array
        setSessions([]);
      }
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
      setSessions([]); // Ensure sessions is always an array
    } finally {
      setLoading(false);
    }
  };

  const fetchSession = async (sessionId) => {
    setLoading(true);
    try {
      const response = await apiService.getSession(sessionId);
      setCurrentSession(response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch session:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const addSession = (session) => {
    setSessions((prev) => {
      // Ensure prev is always an array
      const prevArray = Array.isArray(prev) ? prev : [];
      return [session, ...prevArray];
    });
    setCurrentSession(session);
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  return (
    <SessionContext.Provider
      value={{
        sessions,
        currentSession,
        loading,
        fetchSessions,
        fetchSession,
        addSession,
        setCurrentSession,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
};


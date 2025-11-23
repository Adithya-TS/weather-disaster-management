import { useEffect, useState } from 'react';
import { useSession } from '../context/SessionContext';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import Modal from '../components/ui/Modal';
import { History, Eye, RefreshCw } from 'lucide-react';
import { formatDate, formatDuration, truncate } from '../utils/helpers';
import { useNavigate } from 'react-router-dom';

const Sessions = () => {
  const { sessions, loading, fetchSessions, fetchSession } = useSession();
  const [selectedSession, setSelectedSession] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSessions(20);
  }, [fetchSessions]);

  const handleViewSession = async (sessionId) => {
    try {
      const session = await fetchSession(sessionId);
      setSelectedSession(session);
      setModalOpen(true);
    } catch (error) {
      // Error handled by context
    }
  };

  const handleViewResponsePlan = (session) => {
    navigate('/response-plan', { state: { workflowData: session } });
  };

  return (
    <PageContainer
      title="Session History"
      description="View past disaster response workflow sessions"
      actions={
        <Button
          variant="outline"
          onClick={() => fetchSessions(20)}
          loading={loading}
        >
          <RefreshCw size={18} className="mr-2" />
          Refresh
        </Button>
      }
    >
      {loading && <Loader message="Loading sessions..." />}

      {!loading && sessions.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <History size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400">
              No sessions found. Execute a workflow to create a session.
            </p>
          </CardContent>
        </Card>
      )}

      {!loading && sessions.length > 0 && (
        <div className="space-y-4">
          {sessions.map((session) => (
            <Card key={session.session_id || session.id}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {session.display_location || session.full_location || session.city || session.location || 'Unknown Location'}
                      </h3>
                      {session.session_id && (
                        <span className="text-xs font-mono text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                          {session.session_id}
                        </span>
                      )}
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Date</span>
                        <p className="text-gray-900 dark:text-gray-100">
                          {formatDate(session.timestamp || session.created_at)}
                        </p>
                      </div>
                      {session.disaster_type && (
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Disaster Type</span>
                          <p className="text-gray-900 dark:text-gray-100 font-medium">
                            {session.disaster_type}
                          </p>
                        </div>
                      )}
                      {session.severity && (
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Severity</span>
                          <p className={`font-medium ${
                            session.severity === 'Critical' ? 'text-red-600 dark:text-red-400' :
                            session.severity === 'High' ? 'text-orange-600 dark:text-orange-400' :
                            session.severity === 'Medium' ? 'text-yellow-600 dark:text-yellow-400' :
                            'text-green-600 dark:text-green-400'
                          }`}>
                            {session.severity}
                          </p>
                        </div>
                      )}
                      {session.model && (
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Model</span>
                          <p className="text-gray-900 dark:text-gray-100 text-xs">
                            {session.model}
                          </p>
                        </div>
                      )}
                    </div>
                    {session.response_plan && (
                      <div className="mt-3">
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {truncate(session.response_plan, 150)}
                        </p>
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col space-y-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewSession(session.session_id || `session_${session.id}` || session.id)}
                    >
                      <Eye size={16} className="mr-1" />
                      View
                    </Button>
                    {session.response_plan && (
                      <Button
                        size="sm"
                        onClick={() => handleViewResponsePlan(session)}
                      >
                        Plan
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Session Detail Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Session Details"
        size="lg"
      >
        {selectedSession && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Location</span>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {selectedSession.display_location || selectedSession.full_location || selectedSession.city || selectedSession.location || 'N/A'}
                </p>
              </div>
              <div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Session ID</span>
                <p className="text-lg font-mono text-sm text-gray-900 dark:text-gray-100">
                  {selectedSession.session_id || selectedSession.id || 'N/A'}
                </p>
              </div>
              <div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Timestamp</span>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {formatDate(selectedSession.timestamp || selectedSession.created_at)}
                </p>
              </div>
              {selectedSession.model && (
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Model</span>
                  <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {selectedSession.model}
                  </p>
                </div>
              )}
              {selectedSession.disaster_type && (
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Disaster Type</span>
                  <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {selectedSession.disaster_type}
                  </p>
                </div>
              )}
              {selectedSession.severity && (
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Severity</span>
                  <p className={`text-lg font-semibold ${
                    selectedSession.severity === 'Critical' ? 'text-red-600 dark:text-red-400' :
                    selectedSession.severity === 'High' ? 'text-orange-600 dark:text-orange-400' :
                    selectedSession.severity === 'Medium' ? 'text-yellow-600 dark:text-yellow-400' :
                    'text-green-600 dark:text-green-400'
                  }`}>
                    {selectedSession.severity}
                  </p>
                </div>
              )}
            </div>
            
            {selectedSession.input_text && (
              <div>
                <span className="text-sm text-gray-600 dark:text-gray-400 block mb-2 font-medium">
                  Input Request
                </span>
                <div className="text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                  {selectedSession.input_text}
                </div>
              </div>
            )}
            
            {selectedSession.response_plan && (
              <div>
                <span className="text-sm text-gray-600 dark:text-gray-400 block mb-2 font-medium">
                  Response Plan
                </span>
                <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg max-h-96 overflow-y-auto">
                  {selectedSession.response_plan || selectedSession.output_text}
                </pre>
              </div>
            )}
            
            <div className="flex justify-end">
              <Button onClick={() => setModalOpen(false)}>Close</Button>
            </div>
          </div>
        )}
      </Modal>
    </PageContainer>
  );
};

export default Sessions;


import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useWorkflow } from '../hooks/useWorkflow';
import { useToastNotifications } from '../hooks/useToastNotifications';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import Modal from '../components/ui/Modal';
import { FileText, CheckCircle, Send, AlertCircle } from 'lucide-react';
import { formatDate, formatDuration } from '../utils/helpers';

const ResponsePlan = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { verifyPlan, sendAlerts, loading } = useWorkflow();
  const { showSuccess } = useToastNotifications();
  const [workflowData, setWorkflowData] = useState(null);
  const [verificationModalOpen, setVerificationModalOpen] = useState(false);
  const [alertModalOpen, setAlertModalOpen] = useState(false);
  const [alertChannels, setAlertChannels] = useState(['email', 'sms', 'push']);

  useEffect(() => {
    if (location.state?.workflowData) {
      setWorkflowData(location.state.workflowData);
    }
  }, [location.state]);

  const handleVerify = async () => {
    console.log('🔍 Verify Plan button clicked!');
    console.log('📋 Workflow data:', workflowData);
    
    // Check if we have the weather analysis response
    if (!workflowData?.response) {
      console.error('❌ No response data in workflow!');
      showSuccess('⚠️ No weather analysis available. Please run disaster analysis first.');
      return;
    }
    
    try {
      console.log('📤 Sending verify request...');
      const result = await verifyPlan({ response_plan: workflowData.response });  // ← FIXED: Use 'response' field
      
      console.log('✅ Verify response:', result);
      setVerificationModalOpen(false);
      showSuccess('✅ Plan verified successfully!');
    } catch (error) {
      console.error('❌ Verify plan error:', error);
      // Error handled by hook
    }
  };

  const handleSendAlerts = async () => {
    console.log('🚀 Send Alerts button clicked!');
    console.log('📋 Workflow data:', workflowData);
    
    // Check if we have the weather analysis response
    if (!workflowData?.response) {
      console.error('❌ No response data in workflow!');
      showSuccess('⚠️ No weather analysis available. Please run disaster analysis first.');
      return;
    }
    
    try {
      // Get user email from localStorage auth_user
      let userEmail = null;
      try {
        const authUser = localStorage.getItem('auth_user');
        if (authUser) {
          const user = JSON.parse(authUser);
          userEmail = user.email;
          console.log('📧 User email:', userEmail);
        }
      } catch (e) {
        console.error('❌ Failed to get user email:', e);
      }
      
      const location = workflowData.display_location || workflowData.full_location || workflowData.city || workflowData.location || 'Unknown Location';
      
      console.log('📍 Location:', location);
      console.log('📢 Alert channels:', alertChannels);
      
      // Use 'response' field (the weather analysis) as the response_plan
      const payload = {
        response_plan: workflowData.response,  // ← FIXED: Use 'response' field
        channels: alertChannels,
        location: location,
        send_to_email: userEmail || undefined
      };
      
      console.log('📤 Sending alert payload (truncated):', {
        ...payload,
        response_plan: payload.response_plan.substring(0, 100) + '...'
      });
      
      const result = await sendAlerts(payload);
      
      console.log('✅ Alert response:', result);
      
      setAlertModalOpen(false);
      
      // Show appropriate success message based on result
      // Check if result has data property (axios response) or is direct data
      const responseData = result?.data || result;
      
      if (responseData?.email_notifications_sent) {
        if (responseData.emails_sent && responseData.emails_sent > 0) {
          showSuccess(`✅ Email alert sent to ${responseData.recipient || 'your email'}! Check your inbox.`);
        } else if (responseData.subscribers_notified > 0) {
          showSuccess(`✅ Email alerts sent to ${responseData.subscribers_notified} subscriber(s)!`);
        } else {
          showSuccess('✅ Alert sent successfully!');
        }
      } else if (responseData?.success) {
        showSuccess(responseData.message || '✅ Alerts sent successfully!');
      } else {
        showSuccess('✅ Alert broadcast initiated!');
      }
    } catch (error) {
      console.error('❌ Send alerts error:', error);
      // Error handled by hook
    }
  };

  if (!workflowData) {
    return (
      <PageContainer title="Response Plan">
        <Card>
          <CardContent className="p-12 text-center">
            <FileText size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              No response plan data available
            </p>
            <Button onClick={() => navigate('/')}>Go to Home</Button>
          </CardContent>
        </Card>
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title="Response Plan"
      description="View and manage disaster response plan"
      actions={
        <>
          <Button
            variant="outline"
            onClick={() => setVerificationModalOpen(true)}
            disabled={loading}
          >
            <CheckCircle size={18} className="mr-2" />
            Verify Plan
          </Button>
          <Button
            onClick={() => setAlertModalOpen(true)}
            disabled={loading}
          >
            <Send size={18} className="mr-2" />
            Send Alerts
          </Button>
        </>
      }
    >
      <div className="space-y-6">
        {/* Summary Card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">Location</span>
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {workflowData.display_location || workflowData.full_location || workflowData.city || workflowData.location || 'N/A'}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">Session ID</span>
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100 font-mono text-sm">
                {workflowData.session_id || 'N/A'}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">Duration</span>
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {formatDuration(workflowData.duration)}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Response Plan Card */}
        <Card>
          <CardHeader>
            <CardTitle>Response Plan</CardTitle>
            <CardDescription>
              Generated on {formatDate(workflowData.timestamp)}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose dark:prose-invert max-w-none">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                {workflowData.response_plan || workflowData.response || 'No plan available'}
              </pre>
            </div>
          </CardContent>
        </Card>

        {/* Additional Data */}
        {workflowData.disaster_type && (
          <Card>
            <CardHeader>
              <CardTitle>Disaster Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Disaster Type</span>
                  <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {workflowData.disaster_type}
                  </p>
                </div>
                {workflowData.severity && (
                  <div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Severity</span>
                    <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      {workflowData.severity}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Verification Modal */}
        <Modal
          isOpen={verificationModalOpen}
          onClose={() => setVerificationModalOpen(false)}
          title="Verify Response Plan"
        >
          <div className="space-y-4">
            <p className="text-gray-700 dark:text-gray-300">
              Are you sure you want to verify this response plan? This action will mark the plan
              as reviewed and approved.
            </p>
            <div className="flex justify-end space-x-2">
              <Button
                variant="secondary"
                onClick={() => setVerificationModalOpen(false)}
              >
                Cancel
              </Button>
              <Button onClick={handleVerify} loading={loading}>
                Verify
              </Button>
            </div>
          </div>
        </Modal>

        {/* Alert Modal */}
        <Modal
          isOpen={alertModalOpen}
          onClose={() => setAlertModalOpen(false)}
          title="Send Emergency Alerts"
        >
          <div className="space-y-4">
            <p className="text-gray-700 dark:text-gray-300">
              Select channels to send emergency alerts:
            </p>
            <div className="space-y-2">
              {['email', 'sms', 'push', 'broadcast'].map((channel) => (
                <label
                  key={channel}
                  className="flex items-center space-x-2 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={alertChannels.includes(channel)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setAlertChannels([...alertChannels, channel]);
                      } else {
                        setAlertChannels(alertChannels.filter((c) => c !== channel));
                      }
                    }}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-gray-700 dark:text-gray-300 capitalize">
                    {channel}
                  </span>
                </label>
              ))}
            </div>
            <div className="flex justify-end space-x-2">
              <Button
                variant="secondary"
                onClick={() => setAlertModalOpen(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSendAlerts}
                loading={loading}
                disabled={alertChannels.length === 0}
              >
                Send Alerts
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </PageContainer>
  );
};

export default ResponsePlan;


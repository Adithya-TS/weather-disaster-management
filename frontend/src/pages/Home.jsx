import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkflow } from '../hooks/useWorkflow';
import { useToastNotifications } from '../hooks/useToastNotifications';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { AlertTriangle, Cloud, TrendingUp } from 'lucide-react';

const Home = () => {
  const [location, setLocation] = useState('');
  const navigate = useNavigate();
  const { executeWorkflow, loading } = useWorkflow();
  const { showSuccess, showError } = useToastNotifications();

  const handleExecuteWorkflow = async () => {
    if (!location.trim()) {
      showError('Please enter a location');
      return;
    }

    try {
      const result = await executeWorkflow(location.trim(), {
        onSuccess: (data) => {
          showSuccess(`Workflow completed for ${location}`);
          // Navigate to response plan page with data
          navigate('/response-plan', { state: { workflowData: data } });
        },
        onError: (error) => {
          showError('Failed to execute workflow');
        },
      });
    } catch (error) {
      // Error already handled by hook
    }
  };

  const quickActions = [
    {
      title: 'View Weather',
      description: 'Check current weather conditions',
      icon: Cloud,
      onClick: () => navigate('/weather'),
      color: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300',
    },
    {
      title: 'Social Media Reports',
      description: 'View citizen reports and updates',
      icon: TrendingUp,
      onClick: () => navigate('/social-media'),
      color: 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-300',
    },
    {
      title: 'Disaster Analysis',
      description: 'Analyze disaster type and severity',
      icon: AlertTriangle,
      onClick: () => navigate('/analysis'),
      color: 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300',
    },
  ];

  return (
    <PageContainer
      title="Weather Disaster Management"
      description="Monitor, analyze, and respond to weather-related disasters"
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Workflow Card */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Execute Disaster Response Workflow</CardTitle>
              <CardDescription>
                Enter a location (area, city, or village) to trigger the complete disaster response workflow
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Input
                  label="Location"
                  placeholder="e.g., Ashok Nagar, Chennai or Seruvamani, Thiruvarur"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleExecuteWorkflow();
                    }
                  }}
                  disabled={loading}
                />
                <Button
                  onClick={handleExecuteWorkflow}
                  loading={loading}
                  fullWidth
                  size="lg"
                >
                  Execute Workflow
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Quick Actions
          </h2>
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Card
                key={index}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={action.onClick}
              >
                <CardContent className="p-4">
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${action.color}`}>
                      <Icon size={24} />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                        {action.title}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Info Section */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>How It Works</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-primary-600 dark:text-primary-300 font-bold">1</span>
                </div>
                <h3 className="font-semibold text-sm">Data Collection</h3>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Gather weather and social media data
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-primary-600 dark:text-primary-300 font-bold">2</span>
                </div>
                <h3 className="font-semibold text-sm">Analysis</h3>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Analyze disaster type and severity
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-primary-600 dark:text-primary-300 font-bold">3</span>
                </div>
                <h3 className="font-semibold text-sm">Planning</h3>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Generate response plan
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-primary-600 dark:text-primary-300 font-bold">4</span>
                </div>
                <h3 className="font-semibold text-sm">Execution</h3>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Verify and send alerts
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
};

export default Home;


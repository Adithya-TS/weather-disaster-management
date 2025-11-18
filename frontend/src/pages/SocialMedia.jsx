import { useState } from 'react';
import { useWorkflow } from '../hooks/useWorkflow';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { MessageSquare, User, Clock } from 'lucide-react';
import { formatDate } from '../utils/helpers';

const SocialMedia = () => {
  const [city, setCity] = useState('');
  const [reports, setReports] = useState(null);
  const { getSocialMedia, loading } = useWorkflow();

  const handleFetchReports = async () => {
    if (!city.trim()) return;
    try {
      const data = await getSocialMedia(city.trim());
      setReports(data);
    } catch (error) {
      // Error handled by hook
    }
  };

  return (
    <PageContainer
      title="Social Media Reports"
      description="View citizen reports and social media updates"
    >
      <div className="space-y-6">
        {/* Search Card */}
        <Card>
          <CardHeader>
            <CardTitle>Search Social Media Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Input
                placeholder="Enter city name"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleFetchReports();
                  }
                }}
                disabled={loading}
                className="flex-1"
              />
              <Button onClick={handleFetchReports} loading={loading}>
                Search
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Loading */}
        {loading && <Loader message="Fetching social media reports..." />}

        {/* Reports List */}
        {reports && (
          <div className="space-y-4">
            {Array.isArray(reports.reports) && reports.reports.length > 0 ? (
              reports.reports.map((report, index) => (
                <Card key={index}>
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                          <User size={20} className="text-primary-600 dark:text-primary-300" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <span className="font-semibold text-gray-900 dark:text-gray-100">
                              {report.author || 'Anonymous'}
                            </span>
                            {report.platform && (
                              <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                                {report.platform}
                              </span>
                            )}
                          </div>
                          {report.timestamp && (
                            <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                              <Clock size={14} className="mr-1" />
                              {formatDate(report.timestamp)}
                            </div>
                          )}
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 mb-2">
                          {report.content || report.text || 'No content'}
                        </p>
                        {report.location && (
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            📍 {report.location}
                          </p>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <MessageSquare size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    No reports found for {city}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {!reports && !loading && (
          <Card>
            <CardContent className="p-12 text-center">
              <MessageSquare size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                Enter a city name to view social media reports
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </PageContainer>
  );
};

export default SocialMedia;


import { useState } from 'react';
import { useWorkflow } from '../hooks/useWorkflow';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { MessageSquare, User, Clock, Calendar } from 'lucide-react';
import { formatDate } from '../utils/helpers';

const SocialMedia = () => {
  const [location, setLocation] = useState('');
  const [date, setDate] = useState('');
  const [reports, setReports] = useState(null);
  const [parsedReports, setParsedReports] = useState([]);
  const { getSocialMedia, loading } = useWorkflow();

  // Calculate min date (3 days ago) and max date (today)
  const getMinDate = () => {
    const date = new Date();
    date.setDate(date.getDate() - 3);
    return date.toISOString().split('T')[0];
  };

  const getMaxDate = () => {
    return new Date().toISOString().split('T')[0];
  };

  const minDate = getMinDate();
  const maxDate = getMaxDate();

  const parseReports = (reportsString) => {
    if (!reportsString || typeof reportsString !== 'string') return [];
    
    // Split by newlines and filter out the header
    const lines = reportsString.split('\n').filter(line => line.trim());
    const reportLines = lines.slice(1); // Skip the "Social Media Reports for..." header
    
    return reportLines.map((line, index) => {
      // Extract emoji, text, and username
      const match = line.match(/(.*?)\s+-\s+@(\w+)$/);
      if (match) {
        return {
          id: index,
          content: match[1].trim(),
          author: match[2],
          timestamp: new Date().toISOString()
        };
      }
      return {
        id: index,
        content: line.trim(),
        author: 'citizen',
        timestamp: new Date().toISOString()
      };
    });
  };

  const handleFetchReports = async () => {
    if (!location.trim()) return;
    try {
      const data = await getSocialMedia(location.trim(), date || null);
      console.log('Social Media API Response:', data);
      setReports(data);
      
      // Parse the reports string into array
      // Check multiple possible paths for the reports string
      let reportsString = null;
      if (data?.data?.reports) {
        reportsString = data.data.reports;
      } else if (data?.reports) {
        reportsString = data.reports;
      }
      
      console.log('Reports String:', reportsString);
      
      if (reportsString) {
        const parsed = parseReports(reportsString);
        console.log('Parsed Reports:', parsed);
        setParsedReports(parsed);
      } else {
        console.log('No reports found in response');
        setParsedReports([]);
      }
    } catch (error) {
      console.error('Error fetching reports:', error);
      setParsedReports([]);
    }
  };

  const handleClearDate = () => {
    setDate('');
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
            <div className="space-y-4">
              <div className="flex gap-4">
                <Input
                  placeholder="Enter location (e.g., Ashok Nagar, Chennai or Miami)"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
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
              <div className="flex gap-4 items-center">
                <Calendar size={18} className="text-gray-500" />
                <Input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  disabled={loading}
                  min={minDate}
                  max={maxDate}
                  className="flex-1"
                  placeholder="Optional: Select date for reports"
                />
                {date && (
                  <Button variant="outline" size="sm" onClick={handleClearDate}>
                    Clear Date
                  </Button>
                )}
               
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Loading */}
        {loading && <Loader message="Fetching social media reports..." />}

        {/* Reports List */}
        {reports && (
          <div className="space-y-4">
            {parsedReports && parsedReports.length > 0 ? (
              parsedReports.map((report) => (
                <Card key={report.id}>
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
                    No reports found for {location}
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
                Enter a location to view social media reports
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </PageContainer>
  );
};

export default SocialMedia;


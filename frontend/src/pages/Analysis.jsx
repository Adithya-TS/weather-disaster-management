import { useState } from 'react';
import { useWorkflow } from '../hooks/useWorkflow';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { AlertTriangle } from 'lucide-react';
import { getSeverityColor, getDisasterIcon } from '../utils/helpers';

const Analysis = () => {
  const [location, setLocation] = useState('');
  const [weatherData, setWeatherData] = useState('');
  const [socialReports, setSocialReports] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const { analyzeDisaster, loading } = useWorkflow();

  const handleAnalyze = async () => {
    if (!location.trim()) return;

    try {
      const data = await analyzeDisaster({
        location: location.trim(),
        weather_data: weatherData || undefined,
        social_reports: socialReports || undefined,
      });
      setAnalysisResult(data);
    } catch (error) {
      // Error handled by hook
    }
  };

  return (
    <PageContainer
      title="Disaster Analysis"
      description="Analyze disaster type and severity based on weather and social media data"
    >
      <div className="space-y-6">
        {/* Input Card */}
        <Card>
          <CardHeader>
            <CardTitle>Analyze Disaster</CardTitle>
            <CardDescription>
              Enter location (area, city, or village) and optionally provide weather data or social media reports
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Input
                label="Location"
                placeholder="e.g., Ashok Nagar, Chennai or Seruvamani, Thiruvarur"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                required
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Weather Data (Optional)
                </label>
                <textarea
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows="3"
                  placeholder="Paste weather data JSON or leave empty to fetch automatically"
                  value={weatherData}
                  onChange={(e) => setWeatherData(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Social Media Reports (Optional)
                </label>
                <textarea
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows="3"
                  placeholder="Paste social media reports JSON or leave empty to fetch automatically"
                  value={socialReports}
                  onChange={(e) => setSocialReports(e.target.value)}
                />
              </div>
              <Button onClick={handleAnalyze} loading={loading} fullWidth>
                Analyze Disaster
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Loading */}
        {loading && <Loader message="Analyzing disaster..." />}

        {/* Analysis Result */}
        {analysisResult && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Analysis Result</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Location</span>
                    <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      {analysisResult.location || location}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Disaster Type
                    </span>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-2xl">{getDisasterIcon(analysisResult.disaster_type)}</span>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {analysisResult.disaster_type || 'None'}
                      </p>
                    </div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Severity</span>
                    <div className="mt-1">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getSeverityColor(
                          analysisResult.severity
                        )}`}
                      >
                        {analysisResult.severity || 'Unknown'}
                      </span>
                    </div>
                  </div>
                  {analysisResult.confidence && (
                    <div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Confidence
                      </span>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {(analysisResult.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Details</CardTitle>
              </CardHeader>
              <CardContent>
                {analysisResult.analysis && (
                  <div className="space-y-4">
                    <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                        {analysisResult.analysis}
                      </p>
                    </div>
                  </div>
                )}
                {analysisResult.recommendations && (
                  <div className="mt-4">
                    <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                      Recommendations
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                      {Array.isArray(analysisResult.recommendations)
                        ? analysisResult.recommendations.map((rec, idx) => (
                            <li key={idx}>{rec}</li>
                          ))
                        : (
                          <li>{analysisResult.recommendations}</li>
                        )}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {!analysisResult && !loading && (
          <Card>
            <CardContent className="p-12 text-center">
              <AlertTriangle size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                Enter a location to analyze disaster situation
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </PageContainer>
  );
};

export default Analysis;


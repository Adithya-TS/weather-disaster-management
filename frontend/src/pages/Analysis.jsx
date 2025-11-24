import { useState } from 'react';
import { useWorkflow } from '../hooks/useWorkflow';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { Shield, CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react';

const Analysis = () => {
  const [location, setLocation] = useState('');
  const [userClaim, setUserClaim] = useState('');
  const [factCheckResult, setFactCheckResult] = useState(null);
  const { analyzeDisaster, loading } = useWorkflow();

  const handleFactCheck = async () => {
    if (!location.trim() || !userClaim.trim()) return;

    try {
      const data = await analyzeDisaster({
        location: location.trim(),
        weather_data: userClaim.trim(),
      });
      setFactCheckResult(data);
    } catch (error) {
      // Error handled by hook
    }
  };

  const getVerdictColor = (verdict) => {
    if (verdict === 'VERIFIED') return 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300 border-green-300';
    if (verdict === 'FALSE') return 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300 border-red-300';
    if (verdict === 'PARTIALLY TRUE' || verdict === 'PARTIALLY FALSE') return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300 border-yellow-300';
    return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-300';
  };

  const getVerdictIcon = (verdict) => {
    if (verdict === 'VERIFIED') return <CheckCircle className="w-6 h-6 text-green-600" />;
    if (verdict === 'FALSE') return <XCircle className="w-6 h-6 text-red-600" />;
    if (verdict === 'PARTIALLY TRUE' || verdict === 'PARTIALLY FALSE') return <AlertTriangle className="w-6 h-6 text-yellow-600" />;
    return <Info className="w-6 h-6 text-gray-600" />;
  };

  return (
    <PageContainer
      title="Disaster Fact Check"
      description="Verify weather, earthquake, and tsunami claims against official data from reliable sources"
    >
      <div className="space-y-6">
        {/* Input Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Fact Check Disaster Claim
            </CardTitle>
            <CardDescription>
              Verify weather, earthquake, or tsunami claims against official data sources (OpenWeatherMap, USGS, NOAA)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Input
                label="Location"
                placeholder="e.g., Chennai, Mumbai, Delhi"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                required
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Disaster Claim to Verify <span className="text-red-500">*</span>
                </label>
                <textarea
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows="4"
                  placeholder="e.g., 'Heavy rain with thunderstorms', 'Earthquake of magnitude 5.2', 'Tsunami warning issued', 'Hot and sunny weather'"
                  value={userClaim}
                  onChange={(e) => setUserClaim(e.target.value)}
                  required
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Enter weather, earthquake, or tsunami reports you want to verify
                </p>
              </div>
              <Button onClick={handleFactCheck} loading={loading} fullWidth disabled={!location.trim() || !userClaim.trim()}>
                <Shield className="w-4 h-4 mr-2" />
                Verify Claim
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Loading */}
        {loading && <Loader message="Verifying claim against official weather data..." />}

        {/* Fact Check Result */}
        {factCheckResult && factCheckResult.verification && (
          <div className="space-y-6">
            {/* Verdict Card */}
            <Card className={`border-2 ${getVerdictColor(factCheckResult.verification.verdict)}`}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getVerdictIcon(factCheckResult.verification.verdict)}
                    <div>
                      <CardTitle className="text-xl">{factCheckResult.verification.verdict}</CardTitle>
                      <p className="text-sm mt-1">Confidence: {factCheckResult.verification.confidence}%</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Location</p>
                    <p className="font-semibold">{factCheckResult.location}</p>
                  </div>
                </div>
              </CardHeader>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* User Claim */}
              <Card>
                <CardHeader>
                  <CardTitle>Your Claim</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <p className="text-gray-800 dark:text-gray-200">
                      "{factCheckResult.user_claim}"
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Official Weather */}
              <Card>
                <CardHeader>
                  <CardTitle>Official Weather Data</CardTitle>
                  <CardDescription>From OpenWeatherMap API</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <p className="text-gray-800 dark:text-gray-200">
                      {factCheckResult.verification.official_summary}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Verification Details */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Matches */}
              {factCheckResult.verification.matches && factCheckResult.verification.matches.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-green-700 dark:text-green-400">
                      <CheckCircle className="w-5 h-5" />
                      Verified Facts
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {factCheckResult.verification.matches.map((match, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
                          <span className="text-green-600 dark:text-green-400 mt-0.5">✓</span>
                          <span>{match}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Discrepancies */}
              {factCheckResult.verification.discrepancies && factCheckResult.verification.discrepancies.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-red-700 dark:text-red-400">
                      <XCircle className="w-5 h-5" />
                      Discrepancies Found
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {factCheckResult.verification.discrepancies.map((disc, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
                          <span className="text-red-600 dark:text-red-400 mt-0.5">✗</span>
                          <span>{disc}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        )}

        {!factCheckResult && !loading && (
          <Card>
            <CardContent className="p-12 text-center">
              <Shield size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-2">
                Enter a location and weather claim to fact-check
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                Supports weather (OpenWeatherMap), earthquakes (USGS), and tsunamis (NOAA)
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </PageContainer>
  );
};

export default Analysis;


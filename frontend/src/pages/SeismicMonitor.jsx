import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { apiService } from '../services/api';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { Activity, AlertTriangle, CheckCircle, XCircle, Waves, MapPin } from 'lucide-react';

const SeismicMonitor = () => {
  const [location, setLocation] = useState('');
  const [earthquakeData, setEarthquakeData] = useState(null);
  const [tsunamiData, setTsunamiData] = useState(null);
  const [radiusKm, setRadiusKm] = useState(500);
  const [minMagnitude, setMinMagnitude] = useState(2.5);
  const { execute, loading } = useApi();

  const handleFetchSeismicData = async () => {
    if (!location.trim()) return;

    try {
      // Fetch earthquake data
      const eqResponse = await execute(() =>
        apiService.getEarthquakes({
          location: location.trim(),
          radius_km: radiusKm,
          min_magnitude: minMagnitude,
          days: 7
        }),
        { showSuccessToast: false }
      );
      
      setEarthquakeData(eqResponse);

      // Fetch tsunami warnings
      const tsunamiResponse = await execute(() =>
        apiService.getTsunamiWarnings({
          location: location.trim()
        }),
        { showSuccessToast: false }
      );
      
      setTsunamiData(tsunamiResponse);
    } catch (error) {
      console.error('Seismic data fetch error:', error);
    }
  };

  const getMagnitudeColor = (magnitude) => {
    if (magnitude >= 7.0) return 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300 border-red-300';
    if (magnitude >= 6.0) return 'bg-orange-100 dark:bg-orange-900/20 text-orange-800 dark:text-orange-300 border-orange-300';
    if (magnitude >= 5.0) return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300 border-yellow-300';
    if (magnitude >= 4.0) return 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 border-blue-300';
    return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-300';
  };

  const getSeverityIcon = (severity) => {
    if (severity === 'critical') return <AlertTriangle className="w-5 h-5 text-red-600" />;
    if (severity === 'high') return <AlertTriangle className="w-5 h-5 text-orange-600" />;
    if (severity === 'medium') return <Activity className="w-5 h-5 text-yellow-600" />;
    return <Activity className="w-5 h-5 text-gray-600" />;
  };

  return (
    <PageContainer
      title="Seismic & Tsunami Monitor"
      description="Real-time earthquake and tsunami monitoring from USGS and NOAA"
    >
      <div className="space-y-6">
        {/* Search Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Monitor Seismic Activity
            </CardTitle>
            <CardDescription>
              Track earthquakes and tsunami warnings for any location worldwide
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Input
                label="Location"
                placeholder="e.g., Tokyo, San Francisco, Jakarta"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') handleFetchSeismicData();
                }}
                disabled={loading}
                icon={<MapPin className="w-4 h-4 text-gray-400" />}
              />
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Search Radius (km)
                  </label>
                  <input
                    type="number"
                    value={radiusKm}
                    onChange={(e) => setRadiusKm(parseInt(e.target.value))}
                    min="100"
                    max="2000"
                    step="100"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Min Magnitude
                  </label>
                  <input
                    type="number"
                    value={minMagnitude}
                    onChange={(e) => setMinMagnitude(parseFloat(e.target.value))}
                    min="0"
                    max="10"
                    step="0.5"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <Button onClick={handleFetchSeismicData} loading={loading} fullWidth disabled={!location.trim()}>
                <Activity className="w-4 h-4 mr-2" />
                Monitor Seismic Activity
              </Button>
            </div>
          </CardContent>
        </Card>

        {loading && <Loader message="Fetching seismic data from USGS and NOAA..." />}

        {/* Tsunami Warnings */}
        {tsunamiData && (
          <Card className={`border-2 ${tsunamiData.has_warning ? 'border-red-500' : tsunamiData.has_watch ? 'border-orange-500' : 'border-green-500'}`}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Waves className={`w-6 h-6 ${tsunamiData.has_warning ? 'text-red-600' : tsunamiData.has_watch ? 'text-orange-600' : 'text-green-600'}`} />
                  <div>
                    <CardTitle>Tsunami Status</CardTitle>
                    <CardDescription>NOAA/NWS Alerts</CardDescription>
                  </div>
                </div>
                {tsunamiData.has_warning ? (
                  <AlertTriangle className="w-8 h-8 text-red-600" />
                ) : tsunamiData.has_watch ? (
                  <AlertTriangle className="w-8 h-8 text-orange-600" />
                ) : (
                  <CheckCircle className="w-8 h-8 text-green-600" />
                )}
              </div>
            </CardHeader>
            <CardContent>
              {tsunamiData.warnings && tsunamiData.warnings.length > 0 ? (
                <div className="space-y-4">
                  {tsunamiData.warnings.map((warning, idx) => (
                    <div key={idx} className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border-2 border-red-300">
                      <h4 className="font-bold text-red-900 dark:text-red-200 mb-2">
                        🚨 {warning.event}
                      </h4>
                      <p className="text-red-800 dark:text-red-300 mb-2">{warning.headline}</p>
                      {warning.instruction && (
                        <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded">
                          <p className="font-semibold mb-1">Instructions:</p>
                          <p className="text-sm">{warning.instruction}</p>
                        </div>
                      )}
                      <div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
                        <p>Areas: {warning.areas}</p>
                        <p>Severity: {warning.severity} | Urgency: {warning.urgency}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-2" />
                  <p className="text-green-700 dark:text-green-300 font-semibold">
                    No Active Tsunami Warnings
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    No tsunami warnings, watches, or advisories in effect for this region
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Earthquake Data */}
        {earthquakeData && earthquakeData.earthquakes && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Recent Earthquakes ({earthquakeData.count})
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Past 7 days • Min M{minMagnitude} • {radiusKm}km radius
              </p>
            </div>

            {earthquakeData.earthquakes.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <CheckCircle size={48} className="mx-auto text-green-500 mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    No significant earthquakes detected in this region
                  </p>
                </CardContent>
              </Card>
            ) : (
              earthquakeData.earthquakes.map((eq, idx) => (
                <Card key={idx} className={`border-2 ${getMagnitudeColor(eq.magnitude)}`}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {eq.risk_assessment && getSeverityIcon(eq.risk_assessment.severity)}
                        <div>
                          <CardTitle className="text-lg">
                            Magnitude {eq.magnitude.toFixed(1)}
                          </CardTitle>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {eq.location}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        {eq.distance_km !== undefined && (
                          <p className="text-sm font-semibold">{eq.distance_km.toFixed(0)} km away</p>
                        )}
                        <p className="text-xs text-gray-500">
                          {new Date(eq.time).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Depth</p>
                        <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                          {eq.depth_km ? `${eq.depth_km.toFixed(1)} km` : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Tsunami Risk</p>
                        <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                          {eq.tsunami ? '⚠️ Yes' : '✓ No'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Alert Level</p>
                        <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                          {eq.alert ? eq.alert.toUpperCase() : 'None'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Felt Reports</p>
                        <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                          {eq.felt_reports || 'None'}
                        </p>
                      </div>
                    </div>

                    {eq.risk_assessment && (
                      <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <h4 className="font-semibold mb-2">Risk Assessment</h4>
                        <p className="text-sm mb-2"><strong>Impact:</strong> {eq.risk_assessment.impact}</p>
                        <p className="text-sm mb-2"><strong>Depth:</strong> {eq.risk_assessment.depth_note}</p>
                        {eq.distance_km !== undefined && (
                          <p className="text-sm mb-2"><strong>Proximity:</strong> {eq.risk_assessment.proximity_note}</p>
                        )}
                        
                        {eq.risk_assessment.recommendations && eq.risk_assessment.recommendations.length > 0 && (
                          <div className="mt-3">
                            <p className="font-semibold text-sm mb-1">Recommendations:</p>
                            <ul className="text-sm space-y-1">
                              {eq.risk_assessment.recommendations.map((rec, i) => (
                                <li key={i}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {eq.url && (
                      <div className="mt-3">
                        <a 
                          href={eq.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400"
                        >
                          View details on USGS →
                        </a>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        )}

        {!earthquakeData && !loading && (
          <Card>
            <CardContent className="p-12 text-center">
              <Activity size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-2">
                Enter a location to monitor seismic activity
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500">
                Real-time earthquake data from USGS • Tsunami alerts from NOAA
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </PageContainer>
  );
};

export default SeismicMonitor;

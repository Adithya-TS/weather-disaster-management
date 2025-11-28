import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { apiService } from '../services/api';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { MapPin, Navigation, Cloud, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react';

const RoutePlanning = () => {
  const [startCity, setStartCity] = useState('');
  const [endCity, setEndCity] = useState('');
  const [routeData, setRouteData] = useState(null);
  const [selectedDate, setSelectedDate] = useState(''); // Date string for date picker
  const { execute, loading } = useApi();

  // Initialize with today's date
  useState(() => {
    const today = new Date().toISOString().split('T')[0];
    setSelectedDate(today);
  }, []);

  const handleAnalyzeRoute = async () => {
    if (!startCity.trim() || !endCity.trim()) return;
    
    try {
      const response = await execute(() => 
        apiService.getRouteWeather(startCity.trim(), endCity.trim(), selectedDate, 'accurate'), 
        { showSuccessToast: false }
      );
      
      console.log('Route Analysis Response:', response);
      setRouteData(response);
    } catch (error) {
      console.error('Route analysis error:', error);
    }
  };

  const today = new Date().toISOString().split('T')[0];
  const maxDate = new Date();
  maxDate.setDate(maxDate.getDate() + 3); // Allow up to 3 days
  const maxDateStr = maxDate.toISOString().split('T')[0];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20';
      case 'high':
        return 'text-orange-600 bg-orange-50 dark:bg-orange-900/20';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20';
      default:
        return 'text-green-600 bg-green-50 dark:bg-green-900/20';
    }
  };

  const getSeverityIcon = (severity) => {
    if (severity === 'critical' || severity === 'high') {
      return <AlertTriangle className="w-5 h-5" />;
    }
    return <CheckCircle className="w-5 h-5" />;
  };

  return (
    <PageContainer
      title="Route Weather Planning"
      description="Plan your journey with real-time weather using Google Maps • Supports cities and neighborhoods across India"
    >
      <div className="space-y-6">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Navigation className="w-5 h-5" />
              Enter Your Route
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Starting Location"
                  placeholder="e.g., Chennai, Guindy, Bandra"
                  value={startCity}
                  onChange={(e) => setStartCity(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') handleAnalyzeRoute();
                  }}
                  disabled={loading}
                  icon={<MapPin className="w-4 h-4 text-gray-400" />}
                />
                <Input
                  label="Destination Location"
                  placeholder="e.g., Nagapattinam, Ambattur, Andheri"
                  value={endCity}
                  onChange={(e) => setEndCity(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') handleAnalyzeRoute();
                  }}
                  disabled={loading}
                  icon={<MapPin className="w-4 h-4 text-gray-400" />}
                />
              </div>
              
              {/* Date Picker */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  📅 Travel Date
                </label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  min={today}
                  max={maxDateStr}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
               
              </div>
              
              <div className="flex gap-2">
                <Button onClick={handleAnalyzeRoute} loading={loading} className="flex-1">
                  Analyze Route Weather
                </Button>
                {routeData && (
                  <Button
                    onClick={() => {
                      setRouteData(null);
                      setStartCity('');
                      setEndCity('');
                    }}
                    variant="outline"
                  >
                    Clear
                  </Button>
                )}
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                🗺️ Using Google Maps API for real driving routes • Supports neighborhoods: Guindy → Ambattur, Bandra → Andheri
              </p>
            </div>
          </CardContent>
        </Card>

        {loading && <Loader message="Analyzing weather along your route..." />}

        {/* Route Overview */}
        {routeData && routeData.success && (
          <>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Navigation className="w-5 h-5" />
                    Route Overview
                  </span>
                  <span className="text-sm font-normal text-gray-600 dark:text-gray-400">
                    {routeData.route.total_distance_km} km
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Route Info */}
                  <div className="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="flex items-center gap-3">
                      <MapPin className="w-5 h-5 text-blue-600" />
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                          {routeData.route.start}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Start</p>
                      </div>
                    </div>
                    
                    <ArrowRight className="w-6 h-6 text-gray-400" />
                    
                    {routeData.route.cities_count > 2 && (
                      <>
                        <div className="text-center">
                          <p className="font-semibold text-gray-900 dark:text-gray-100">
                            {routeData.route.cities_count - 2}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Cities</p>
                        </div>
                        <ArrowRight className="w-6 h-6 text-gray-400" />
                      </>
                    )}
                    
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                          {routeData.route.end}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Destination</p>
                      </div>
                      <MapPin className="w-5 h-5 text-blue-600" />
                    </div>
                  </div>

                  {/* Recommendation */}
                  <div className={`p-4 rounded-lg border-2 ${
                    routeData.severe_conditions?.length > 0
                      ? 'border-red-200 bg-red-50 dark:bg-red-900/20'
                      : routeData.weather_warnings?.length > 0
                      ? 'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20'
                      : 'border-green-200 bg-green-50 dark:bg-green-900/20'
                  }`}>
                    <p className="font-semibold text-gray-900 dark:text-gray-100 mb-2 whitespace-pre-line">
                      {routeData.recommendation}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Cities Along Route */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <Cloud className="w-5 h-5" />
                Weather Conditions Along Route
              </h3>
              
              {routeData.cities?.map((city, index) => (
                <Card key={index}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${getSeverityColor(city.severity)}`}>
                          {getSeverityIcon(city.severity)}
                        </div>
                        <div>
                          <CardTitle className="text-lg">
                            {city.city}{city.state && `, ${city.state}`}
                          </CardTitle>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {city.distance_km} km from start
                            {city.is_start && " (Starting Point)"}
                            {city.is_end && " (Destination)"}
                          </p>
                        </div>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(city.severity)}`}>
                        {city.severity.toUpperCase()}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {city.weather && city.weather.success && (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Condition</p>
                          <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                            {city.weather.condition || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Temperature</p>
                          <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                            {city.weather.temperature || 'N/A'}°C
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Wind Speed</p>
                          <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                            {city.weather.wind_speed || 'N/A'} km/h
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Humidity</p>
                          <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                            {city.weather.humidity || 'N/A'}%
                          </p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}

        {!routeData && !loading && (
          <Card>
            <CardContent className="p-12 text-center">
              <Navigation size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                Enter start and destination to analyze weather along your route
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                📍 Supports cities & neighborhoods: Chennai, Nagapattinam, Guindy, Ambattur, Bandra, Mumbai
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                🗺️ Powered by Google Maps API for real driving routes
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </PageContainer>
  );
};

export default RoutePlanning;

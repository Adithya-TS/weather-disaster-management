import { useState } from 'react';
import { useWorkflow } from '../hooks/useWorkflow';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { Cloud, Thermometer, Droplets, Wind, Eye, Calendar, MapPin } from 'lucide-react';

const Weather = () => {
  const [location, setLocation] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isForecastMode, setIsForecastMode] = useState(false);
  const [weatherData, setWeatherData] = useState(null);
  const { getWeather, loading } = useWorkflow();

  const handleFetchWeather = async () => {
    if (!location.trim()) return;
    try {
      const start = isForecastMode && startDate ? startDate : null;
      const end = isForecastMode && endDate ? endDate : null;
      const response = await getWeather(location.trim(), start, end);
      const data = response?.data?.weather_data || response?.data || response;
      setWeatherData(data);
    } catch (error) {
      // Error handled by hook
    }
  };

  const handleModeToggle = () => {
    setIsForecastMode(!isForecastMode);
    if (!isForecastMode) {
      const today = new Date();
      const end = new Date(today);
      end.setDate(today.getDate() + 3);
      setStartDate(today.toISOString().split('T')[0]);
      setEndDate(end.toISOString().split('T')[0]);
    } else {
      setStartDate('');
      setEndDate('');
    }
    setWeatherData(null);
  };

  const today = new Date().toISOString().split('T')[0];
  const maxDate = new Date();
  maxDate.setDate(maxDate.getDate() + 30); // Allow up to 30 days (1 month)
  const maxDateStr = maxDate.toISOString().split('T')[0];

  const isForecastData = weatherData?.forecast_type === 'trip_planning' || weatherData?.forecasts;

  const weatherMetrics = weatherData && !isForecastData
    ? [
        {
          label: 'Temperature',
          value: `${weatherData.temperature || 'N/A'}°C`,
          icon: Thermometer,
          color: 'text-red-500',
        },
        {
          label: 'Feels Like',
          value: `${weatherData.feels_like || 'N/A'}°C`,
          icon: Thermometer,
          color: 'text-orange-500',
        },
        {
          label: 'Humidity',
          value: `${weatherData.humidity || 'N/A'}%`,
          icon: Droplets,
          color: 'text-blue-500',
        },
        {
          label: 'Wind Speed',
          value: `${weatherData.wind_speed || 'N/A'} km/h`,
          icon: Wind,
          color: 'text-gray-500',
        },
        {
          label: 'Visibility',
          value: `${weatherData.visibility || 'N/A'} km`,
          icon: Eye,
          color: 'text-purple-500',
        },
      ]
    : [];

  return (
    <PageContainer
      title="Weather Data"
      description="View real-time weather conditions and forecasts for any location"
    >
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Search Weather</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    label="Location"
                    placeholder="e.g., Ashok Nagar, Chennai or Seruvamani, Thiruvarur"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleFetchWeather();
                      }
                    }}
                    disabled={loading}
                  />
                </div>
                <div className="flex items-end">
                  <Button onClick={handleFetchWeather} loading={loading}>
                    Search
                  </Button>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isForecastMode}
                    onChange={handleModeToggle}
                    className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Trip Planning / Forecast Mode
                  </span>
                  <Calendar className="w-4 h-4 text-gray-500" />
                </label>
              </div>

              {isForecastMode && (
                <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Start Date
                    </label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      min={today}
                      max={maxDateStr}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      End Date
                    </label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      min={startDate || today}
                      max={maxDateStr}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <p className="col-span-2 text-xs text-gray-500 dark:text-gray-400">
                    Forecast available for up to 30 days (1 month) in advance. Days 1-5 use actual forecast data, days 6-30 use climatological estimates.
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {loading && <Loader message="Fetching weather data..." />}

        {weatherData && !isForecastData && weatherData.success && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {weatherMetrics.map((metric, index) => {
                const Icon = metric.icon;
                return (
                  <Card key={index}>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {metric.label}
                        </span>
                        <Icon className={metric.color} size={24} />
                      </div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        {metric.value}
                      </p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Weather Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">Location</span>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <MapPin size={18} />
                        {weatherData.full_location || weatherData.location || location}
                      </p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">Condition</span>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {weatherData.condition || weatherData.weather || 'N/A'}
                      </p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">Temperature Range</span>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {weatherData.temp_min || 'N/A'}°C / {weatherData.temp_max || 'N/A'}°C
                      </p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">Pressure</span>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {weatherData.pressure || 'N/A'} hPa
                      </p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">Cloud Cover</span>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {weatherData.cloud_cover || 'N/A'}%
                      </p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">Wind Direction</span>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {weatherData.wind_direction ? `${weatherData.wind_direction}°` : 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {weatherData && isForecastData && weatherData.success && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar size={20} />
                  Weather Forecast for {weatherData.full_location || weatherData.location || location}
                </CardTitle>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {weatherData.start_date} to {weatherData.end_date}
                </p>
              </CardHeader>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {weatherData.forecasts?.map((forecast, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="text-lg">
                      {forecast.day_name}
                    </CardTitle>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {forecast.date}
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                          {forecast.max_temp}°C
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Min: {forecast.min_temp}°C
                        </p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {forecast.description || forecast.condition}
                        </p>
                        {forecast.forecast_type === 'climatological' && (
                          <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                            ⚠️ Estimated forecast
                          </p>
                        )}
                      </div>
                      {forecast.hourly_forecasts && forecast.hourly_forecasts.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                          <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
                            Hourly Forecast:
                          </p>
                          <div className="space-y-1">
                            {forecast.hourly_forecasts.slice(0, 3).map((hourly, hIndex) => (
                              <div key={hIndex} className="flex justify-between text-xs">
                                <span className="text-gray-600 dark:text-gray-400">
                                  {new Date(hourly.time).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
                                </span>
                                <span className="text-gray-900 dark:text-gray-100 font-medium">
                                  {hourly.temperature}°C
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {weatherData && !weatherData.success && (
          <Card>
            <CardContent className="p-6">
              <div className="text-center">
                <Cloud size={48} className="mx-auto text-red-400 mb-4" />
                <p className="text-red-600 dark:text-red-400 font-medium">
                  {weatherData.error || 'Failed to fetch weather data'}
                </p>
                {weatherData.note && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    {weatherData.note}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {!weatherData && !loading && (
          <Card>
            <CardContent className="p-12 text-center">
              <Cloud size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                Enter a location to view weather data
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                Examples: "Ashok Nagar, Chennai" or "Seruvamani, Thiruvarur"
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </PageContainer>
  );
};

export default Weather;


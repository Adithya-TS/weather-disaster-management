import { useState } from 'react';
import { useWorkflow } from '../hooks/useWorkflow';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { Cloud, Thermometer, Droplets, Wind, Eye } from 'lucide-react';

const Weather = () => {
  const [city, setCity] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const { getWeather, loading } = useWorkflow();

  const handleFetchWeather = async () => {
    if (!city.trim()) return;
    try {
      const data = await getWeather(city.trim());
      setWeatherData(data);
    } catch (error) {
      // Error handled by hook
    }
  };

  const weatherMetrics = weatherData
    ? [
        {
          label: 'Temperature',
          value: `${weatherData.temperature || 'N/A'}°C`,
          icon: Thermometer,
          color: 'text-red-500',
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
      description="View real-time weather conditions for any city"
    >
      <div className="space-y-6">
        {/* Search Card */}
        <Card>
          <CardHeader>
            <CardTitle>Search Weather</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Input
                placeholder="Enter city name"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleFetchWeather();
                  }
                }}
                disabled={loading}
                className="flex-1"
              />
              <Button onClick={handleFetchWeather} loading={loading}>
                Search
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Weather Data */}
        {loading && <Loader message="Fetching weather data..." />}

        {weatherData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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
        )}

        {/* Detailed Weather Info */}
        {weatherData && (
          <Card>
            <CardHeader>
              <CardTitle>Weather Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">City</span>
                    <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      {weatherData.city || city}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Condition</span>
                    <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      {weatherData.condition || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Pressure</span>
                    <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      {weatherData.pressure || 'N/A'} hPa
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">UV Index</span>
                    <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      {weatherData.uv_index || 'N/A'}
                    </p>
                  </div>
                </div>
                {weatherData.description && (
                  <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <p className="text-gray-700 dark:text-gray-300">
                      {weatherData.description}
                    </p>
                  </div>
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
                Enter a city name to view weather data
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </PageContainer>
  );
};

export default Weather;


import { useState, useEffect } from 'react';
import { Card } from '../components/ui';
import { AlertTriangle, Bell, BellOff, Plus, Edit2, Trash2, MapPin, Clock, AlertCircle } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

const Alerts = () => {
  const [activeTab, setActiveTab] = useState('alerts'); // 'alerts' or 'subscriptions'
  const [alerts, setAlerts] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [editingSubscription, setEditingSubscription] = useState(null);

  useEffect(() => {
    if (activeTab === 'alerts') {
      fetchAlerts();
    } else {
      fetchSubscriptions();
    }
  }, [activeTab]);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/alerts/');
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      toast.error('Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const fetchSubscriptions = async () => {
    setLoading(true);
    try {
      const response = await api.get('/alerts/subscriptions');
      setSubscriptions(response.data);
    } catch (error) {
      console.error('Error fetching subscriptions:', error);
      toast.error('Failed to load subscriptions');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      low: 'text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-300',
      medium: 'text-orange-600 bg-orange-100 dark:bg-orange-900 dark:text-orange-300',
      high: 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-300',
      critical: 'text-red-800 bg-red-200 dark:bg-red-950 dark:text-red-200'
    };
    return colors[severity] || colors.low;
  };

  const getSeverityIcon = (severity) => {
    if (severity === 'critical' || severity === 'high') {
      return <AlertCircle size={20} className="mr-2" />;
    }
    return <AlertTriangle size={20} className="mr-2" />;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleDeleteSubscription = async (id) => {
    if (!confirm('Are you sure you want to delete this subscription?')) {
      return;
    }

    try {
      await api.delete(`/alerts/subscriptions/${id}`);
      toast.success('Subscription deleted successfully');
      fetchSubscriptions();
    } catch (error) {
      console.error('Error deleting subscription:', error);
      toast.error('Failed to delete subscription');
    }
  };

  const handleEditSubscription = (subscription) => {
    setEditingSubscription(subscription);
    setShowSubscriptionModal(true);
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Alerts & Notifications
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Monitor severe weather alerts and manage your notification preferences
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('alerts')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'alerts'
                ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <AlertTriangle size={18} className="inline mr-2" />
            Active Alerts
          </button>
          <button
            onClick={() => setActiveTab('subscriptions')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'subscriptions'
                ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <Bell size={18} className="inline mr-2" />
            My Subscriptions
          </button>
        </nav>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {activeTab === 'alerts' && (
            <div className="space-y-4">
              {alerts.length === 0 ? (
                <Card>
                  <div className="text-center py-12">
                    <AlertTriangle size={48} className="mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-500 dark:text-gray-400">No active alerts at the moment</p>
                    <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                      You'll see weather alerts here when severe conditions are detected
                    </p>
                  </div>
                </Card>
              ) : (
                alerts.map((alert) => (
                  <Card key={alert.id} className="hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(alert.severity)}`}>
                            {getSeverityIcon(alert.severity)}
                            {alert.severity.toUpperCase()}
                          </span>
                          <span className="ml-3 text-sm text-gray-500 dark:text-gray-400 capitalize">
                            {alert.alert_type.replace('_', ' ')}
                          </span>
                        </div>
                        
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
                          {alert.title}
                        </h3>
                        
                        <p className="text-gray-600 dark:text-gray-400 mb-4">
                          {alert.description}
                        </p>
                        
                        <div className="flex flex-wrap gap-4 text-sm text-gray-500 dark:text-gray-400">
                          <div className="flex items-center">
                            <MapPin size={16} className="mr-1" />
                            {alert.location}
                          </div>
                          <div className="flex items-center">
                            <Clock size={16} className="mr-1" />
                            {formatDate(alert.detected_at)}
                          </div>
                        </div>
                        
                        {(alert.temperature || alert.wind_speed || alert.precipitation) && (
                          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              {alert.temperature && (
                                <div>
                                  <p className="text-xs text-gray-500 dark:text-gray-400">Temperature</p>
                                  <p className="text-sm font-medium">{alert.temperature.toFixed(1)}°C</p>
                                </div>
                              )}
                              {alert.wind_speed && (
                                <div>
                                  <p className="text-xs text-gray-500 dark:text-gray-400">Wind Speed</p>
                                  <p className="text-sm font-medium">{alert.wind_speed.toFixed(1)} km/h</p>
                                </div>
                              )}
                              {alert.precipitation && (
                                <div>
                                  <p className="text-xs text-gray-500 dark:text-gray-400">Precipitation</p>
                                  <p className="text-sm font-medium">{alert.precipitation.toFixed(1)} mm</p>
                                </div>
                              )}
                              {alert.humidity && (
                                <div>
                                  <p className="text-xs text-gray-500 dark:text-gray-400">Humidity</p>
                                  <p className="text-sm font-medium">{alert.humidity.toFixed(1)}%</p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          )}

          {activeTab === 'subscriptions' && (
            <div>
              <div className="mb-6 flex justify-between items-center">
                <p className="text-gray-600 dark:text-gray-400">
                  Subscribe to locations to receive alerts when severe weather is detected
                </p>
                <button
                  onClick={() => {
                    setEditingSubscription(null);
                    setShowSubscriptionModal(true);
                  }}
                  className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <Plus size={18} className="mr-2" />
                  Add Subscription
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {subscriptions.length === 0 ? (
                  <Card className="col-span-full">
                    <div className="text-center py-12">
                      <Bell size={48} className="mx-auto text-gray-400 mb-4" />
                      <p className="text-gray-500 dark:text-gray-400">No subscriptions yet</p>
                      <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                        Add a location to start receiving weather alerts
                      </p>
                    </div>
                  </Card>
                ) : (
                  subscriptions.map((sub) => (
                    <Card key={sub.id} className="hover:shadow-lg transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center">
                          {sub.is_active ? (
                            <Bell size={20} className="text-primary-600 mr-2" />
                          ) : (
                            <BellOff size={20} className="text-gray-400 mr-2" />
                          )}
                          <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                            {sub.location}
                          </h3>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEditSubscription(sub)}
                            className="text-gray-400 hover:text-primary-600"
                          >
                            <Edit2 size={16} />
                          </button>
                          <button
                            onClick={() => handleDeleteSubscription(sub.id)}
                            className="text-gray-400 hover:text-red-600"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </div>
                      
                      <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex items-center">
                          <MapPin size={14} className="mr-2" />
                          Radius: {sub.radius_km} km
                        </div>
                        
                        <div className="flex flex-wrap gap-1 mt-3">
                          {sub.notify_on_critical && (
                            <span className="px-2 py-1 bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300 rounded text-xs">
                              Critical
                            </span>
                          )}
                          {sub.notify_on_high && (
                            <span className="px-2 py-1 bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300 rounded text-xs">
                              High
                            </span>
                          )}
                          {sub.notify_on_medium && (
                            <span className="px-2 py-1 bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300 rounded text-xs">
                              Medium
                            </span>
                          )}
                          {sub.notify_on_low && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded text-xs">
                              Low
                            </span>
                          )}
                        </div>
                        
                        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 flex items-center">
                          {sub.email_enabled && (
                            <span className="text-xs text-gray-500">✉️ Email</span>
                          )}
                        </div>
                      </div>
                    </Card>
                  ))
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* Subscription Modal - Will be implemented in next step */}
      {showSubscriptionModal && (
        <SubscriptionModal
          subscription={editingSubscription}
          onClose={() => {
            setShowSubscriptionModal(false);
            setEditingSubscription(null);
          }}
          onSave={() => {
            setShowSubscriptionModal(false);
            setEditingSubscription(null);
            fetchSubscriptions();
          }}
        />
      )}
    </div>
  );
};

// Subscription Modal Component
const SubscriptionModal = ({ subscription, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    location: subscription?.location || '',
    radius_km: subscription?.radius_km || 50,
    email_enabled: subscription?.email_enabled ?? true,
    phone_number: subscription?.phone_number || '',
    push_enabled: subscription?.push_enabled ?? false,
    notify_on_low: subscription?.notify_on_low ?? false,
    notify_on_medium: subscription?.notify_on_medium ?? true,
    notify_on_high: subscription?.notify_on_high ?? true,
    notify_on_critical: subscription?.notify_on_critical ?? true,
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (subscription) {
        // Update existing
        await api.put(`/alerts/subscriptions/${subscription.id}`, formData);
        toast.success('Subscription updated successfully');
      } else {
        // Create new
        await api.post('/alerts/subscriptions', formData);
        toast.success('Subscription created successfully');
      }
      onSave();
    } catch (error) {
      console.error('Error saving subscription:', error);
      toast.error(error.response?.data?.detail || 'Failed to save subscription');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            {subscription ? 'Edit Subscription' : 'New Subscription'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Location *
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                placeholder="e.g., Chennai, India"
                required
                disabled={!!subscription}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Alert Radius (km)
              </label>
              <input
                type="number"
                value={formData.radius_km}
                onChange={(e) => setFormData({ ...formData, radius_km: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                min="1"
                max="500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Notification Severity Levels
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.notify_on_critical}
                    onChange={(e) => setFormData({ ...formData, notify_on_critical: e.target.checked })}
                    className="mr-3 h-4 w-4 text-primary-600"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Critical</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.notify_on_high}
                    onChange={(e) => setFormData({ ...formData, notify_on_high: e.target.checked })}
                    className="mr-3 h-4 w-4 text-primary-600"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">High</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.notify_on_medium}
                    onChange={(e) => setFormData({ ...formData, notify_on_medium: e.target.checked })}
                    className="mr-3 h-4 w-4 text-primary-600"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Medium</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.notify_on_low}
                    onChange={(e) => setFormData({ ...formData, notify_on_low: e.target.checked })}
                    className="mr-3 h-4 w-4 text-primary-600"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Low</span>
                </label>
              </div>
            </div>

            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.email_enabled}
                  onChange={(e) => setFormData({ ...formData, email_enabled: e.target.checked })}
                  className="mr-3 h-4 w-4 text-primary-600"
                />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Enable Email Notifications
                </span>
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Save Subscription'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Alerts;


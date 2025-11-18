/**
 * Format date to readable string
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString();
};

/**
 * Format duration in milliseconds to readable string
 */
export const formatDuration = (ms) => {
  if (!ms) return 'N/A';
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
};

/**
 * Get severity color class
 */
export const getSeverityColor = (severity) => {
  const colors = {
    Low: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    Moderate: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    High: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    Critical: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  };
  return colors[severity] || colors.Moderate;
};

/**
 * Get disaster type icon
 */
export const getDisasterIcon = (type) => {
  const icons = {
    Hurricane: '🌪️',
    Flood: '🌊',
    Heatwave: '🔥',
    Tornado: '🌪️',
    Wildfire: '🔥',
    Earthquake: '🌍',
    None: '✅',
  };
  return icons[type] || '⚠️';
};

/**
 * Truncate text with ellipsis
 */
export const truncate = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Capitalize first letter
 */
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};


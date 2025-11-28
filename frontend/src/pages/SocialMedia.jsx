import { useState, useEffect } from 'react';
import { useWorkflow } from '../hooks/useWorkflow';
import { apiService } from '../services/api';
import PageContainer from '../components/layout/PageContainer';
import Card, { CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { MessageSquare, Clock, Calendar, Search, X, TrendingUp, AlertCircle, MapPin } from 'lucide-react';
import { formatDate } from '../utils/helpers';
import { useMemo } from 'react';

// Local expandable text component
const ExpandableText = ({ text, url, maxChars = 240 }) => {
  const [expanded, setExpanded] = useState(false);
  const isLong = useMemo(() => (text || '').length > maxChars, [text, maxChars]);
  const display = useMemo(() => {
    if (!text) return '';
    if (expanded || !isLong) return text;
    return text.slice(0, maxChars) + '…';
  }, [text, expanded, isLong, maxChars]);

  return (
    <div className="text-gray-700 dark:text-gray-300 leading-relaxed mb-2">
      <p>{display}</p>
      <div className="flex items-center gap-3 mt-2">
        {isLong && (
          <button
            onClick={() => setExpanded(v => !v)}
            className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400"
          >
            {expanded ? 'Show less' : 'Read more'}
          </button>
        )}
        {url && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
          >
            Open source
          </a>
        )}
      </div>
    </div>
  );
};

const SocialMedia = () => {
  const [location, setLocation] = useState('');
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [reports, setReports] = useState(null);
  const [validation, setValidation] = useState('');
  const [itemValidations, setItemValidations] = useState({}); // id -> summary
  const [validating, setValidating] = useState(false);
  const [parsedReports, setParsedReports] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const { getSocialMedia, loading } = useWorkflow();

  // Load search history from localStorage
  useEffect(() => {
    const history = JSON.parse(localStorage.getItem('socialMediaSearchHistory') || '[]');
    setSearchHistory(history.slice(0, 5));
  }, []);

  // Calculate min date (7 days ago) and max date (today)
  const getMinDate = () => {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date.toISOString().split('T')[0];
  };

  const getMaxDate = () => {
    return new Date().toISOString().split('T')[0];
  };

  const minDate = getMinDate();
  const maxDate = getMaxDate();

  const parseReports = (reportsString) => {
    if (!reportsString || typeof reportsString !== 'string') {
      return [];
    }
    
    const lines = reportsString.split('\n').filter(line => line.trim());
    const reportLines = lines[0] && lines[0].includes('Social Media Reports') 
      ? lines.slice(1) 
      : lines;
    
    return reportLines.map((line, index) => {
      // Format from backend: "📱 [Platform] content - @author | timestamp | url"
      // Split by pipe to get optional timestamp and URL
      const parts = line.split('|').map(p => p.trim());
      const main = parts[0] || line; // Fallback to full line if no pipes
      const timestamp = parts[1] || '';
      const url = parts[2] || '';

      // Extract platform from [Platform] pattern FIRST (before cleaning)
      const platformMatch = main.match(/\[(.*?)\]/);
      const platform = platformMatch ? platformMatch[1] : 'Social Media';

      // Extract author from "- @author" pattern (before any pipe)
      const authorMatch = main.match(/-\s*@([^|]+)$/);
      const author = authorMatch ? authorMatch[1].trim() : 'citizen';
      
      // Clean content: remove emoji, platform tag, and author suffix
      let content = main
        .replace(/^📱\s*/,'')           // Remove emoji
        .replace(/\[.*?\]\s*/,'')        // Remove [Platform]
        .replace(/-\s*@[^|]+$/,'')      // Remove - @author
        .trim();

      // If content is still empty, use original line as fallback
      if (!content) {
        content = line.trim();
      }

      return {
        id: index,
        content,
        author,
        platform,
        timestamp: timestamp || new Date().toISOString(),
        url: url || null,
      };
    }).filter(report => report.content && report.content.length > 0);
  };

  const handleFetchReports = async () => {
    if (!location.trim()) return;
    
    const searchLocation = location.trim();
    
    try {
      const response = await getSocialMedia(searchLocation, date || null);
      const data = response?.data || response;
      setReports(data);
      setValidation('');
      
      const reportsString = data?.reports;
      
      if (reportsString && typeof reportsString === 'string') {
        const parsed = parseReports(reportsString);
        console.log('Parsed reports:', parsed); // Debug log
        setParsedReports(parsed);
        
        if (parsed.length > 0) {
          saveToSearchHistory(searchLocation);
        }
      } else {
        setParsedReports([]);
      }
    } catch (error) {
      console.error('Error fetching reports:', error);
      setParsedReports([]);
      setReports(null);
    }
  };

  const handleValidateReports = async () => {
    if (!location.trim()) return;
    if (!reports?.reports) return;
    try {
      setValidating(true);
      // Call backend validation endpoint
      const res = await apiService.validateSocialMedia(location.trim(), date || null);
      const payload = res?.data || res;
      setValidation(payload?.validation || '');
    } catch (e) {
      console.error('Validation failed', e);
      setValidation('Validation failed. Please try again.');
    } finally {
      setValidating(false);
    }
  };

  const buildReportLine = (report) => {
    // Recompose a single-line string matching backend formatter
    const platform = report.platform ? `[${report.platform}]` : '';
    const author = report.author ? ` - @${report.author}` : '';
    const timestamp = report.timestamp ? ` | ${report.timestamp}` : '';
    const url = report.url ? ` | ${report.url}` : '';
    return `📱 ${platform} ${report.content}${author}${timestamp}${url}`.trim();
  };

  const handleValidateSingle = async (report) => {
    try {
      setItemValidations(prev => ({ ...prev, [report.id]: 'Validating…' }));
      const line = buildReportLine(report);
      // Call the same validate endpoint but with current date; backend validates content lines
      const res = await apiService.validateSocialMediaItem(location.trim(), line, date || null);
      const payload = res?.data || res;
      const summary = payload?.summary || 'Validation unavailable';
      setItemValidations(prev => ({ ...prev, [report.id]: summary }));
    } catch (e) {
      console.error('Validation failed', e);
      setItemValidations(prev => ({ ...prev, [report.id]: 'Validation failed. Please try again.' }));
    }
  };

  const saveToSearchHistory = (searchLocation) => {
    const history = JSON.parse(localStorage.getItem('socialMediaSearchHistory') || '[]');
    const newHistory = [searchLocation, ...history.filter(l => l !== searchLocation)].slice(0, 5);
    localStorage.setItem('socialMediaSearchHistory', JSON.stringify(newHistory));
    setSearchHistory(newHistory);
  };

  const handleQuickSearch = (historyLocation) => {
    setLocation(historyLocation);
    setDate('');
  };

  const clearSearchHistory = () => {
    localStorage.removeItem('socialMediaSearchHistory');
    setSearchHistory([]);
  };

  const handleClearDate = () => {
    setDate('');
  };

  const handleClearSearch = () => {
    setLocation('');
    setDate('');
    setReports(null);
    setParsedReports([]);
  };

  const getPlatformIcon = (platform) => {
    switch (platform?.toLowerCase()) {
      case 'reddit':
        return '🔴';
      case 'news':
        return '📰';
      case 'rss':
        return '📡';
      case 'telegram':
        return '✈️';
      default:
        return '📱';
    }
  };

  const getPlatformColor = (platform) => {
    switch (platform?.toLowerCase()) {
      case 'reddit':
        return 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300';
      case 'news':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300';
      case 'rss':
        return 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300';
      case 'telegram':
        return 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900 dark:text-cyan-300';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <PageContainer
      title="Social Media Reports"
      description="Real-time citizen reports and social media monitoring"
    >
      <div className="space-y-6">
        {/* Search Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search size={20} />
              Search Social Media Reports
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Search Input */}
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <MapPin size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <Input
                    placeholder="Enter location (e.g., Chennai, Miami, New York)"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !loading) {
                        handleFetchReports();
                      }
                    }}
                    disabled={loading}
                    className="pl-10"
                  />
                </div>
                <Button 
                  onClick={handleFetchReports} 
                  loading={loading}
                  disabled={!location.trim() || loading}
                >
                  <Search size={18} className="mr-2" />
                  Search
                </Button>
                {reports && (
                  <Button 
                    variant="outline"
                    onClick={handleValidateReports}
                    loading={validating}
                    disabled={validating}
                  >
                    Validate
                  </Button>
                )}
                {(location || reports) && (
                  <Button 
                    variant="outline" 
                    onClick={handleClearSearch}
                    disabled={loading}
                  >
                    <X size={18} />
                  </Button>
                )}
              </div>

              {/* Date Filter */}
              <div className="flex gap-2 items-center">
                <Calendar size={18} className="text-gray-500 dark:text-gray-400" />
                <Input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  disabled={loading}
                  min={minDate}
                  max={maxDate}
                  className="flex-1"
                  placeholder="Optional: Filter by date"
                />
                {date && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleClearDate}
                    disabled={loading}
                  >
                    Clear
                  </Button>
                )}
              </div>

              {/* Search History */}
              {searchHistory.length > 0 && !reports && (
                <div className="pt-2 border-t dark:border-gray-700">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <TrendingUp size={16} />
                      <span>Recent Searches</span>
                    </div>
                    <button
                      onClick={clearSearchHistory}
                      className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                    >
                      Clear
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {searchHistory.map((loc, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleQuickSearch(loc)}
                        className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-full transition-colors"
                      >
                        {loc}
                      </button>
                    ))}
                  </div>
                </div>
              )}

            
            </div>
          </CardContent>
        </Card>

        {/* Loading */}
        {loading && <Loader message="Fetching social media reports..." />}

        {/* Results Summary */}
        {reports && parsedReports.length > 0 && (
          <div className="flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <MessageSquare size={18} />
              <span>
                Found <strong className="text-gray-900 dark:text-gray-100">{parsedReports.length}</strong> {parsedReports.length === 1 ? 'report' : 'reports'} for{' '}
                <strong className="text-gray-900 dark:text-gray-100">{reports.location || location}</strong>
              </span>
            </div>
            {reports.date && (
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Calendar size={16} />
                {reports.date}
              </div>
            )}
          </div>
        )}

        {/* Validation Summary */}
        {validation && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle size={20} />
                Validation Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">{validation}</pre>
            </CardContent>
          </Card>
        )}

        {/* Reports List */}
        {reports && (
          <div className="space-y-4">
            {parsedReports && parsedReports.length > 0 ? (
              parsedReports.map((report) => (
                <Card key={report.id} className="hover:shadow-lg transition-shadow duration-200">
                  <CardContent className="p-5">
                    <div className="flex items-start gap-4">
                      {/* Avatar */}
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-semibold shadow-md">
                          {report.author ? report.author.charAt(0).toUpperCase() : 'U'}
                        </div>
                      </div>
                      
                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        {/* Header */}
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-semibold text-gray-900 dark:text-gray-100">
                              @{report.author || 'anonymous'}
                            </span>
                            {report.platform && (
                              <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${getPlatformColor(report.platform)}`}>
                                {getPlatformIcon(report.platform)} {report.platform}
                              </span>
                            )}
                          </div>
                          {report.timestamp && (
                            <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                              <Clock size={14} />
                              {formatDate(report.timestamp)}
                            </div>
                          )}
                        </div>
                        
                        {/* Report Content */}
                        <ExpandableText text={report.content} url={report.url} />
                        <div className="mt-2 flex gap-2">
                          <Button variant="outline" size="sm" onClick={() => handleValidateSingle(report)} disabled={validating || loading}>
                            Validate this report
                          </Button>
                        </div>
                        {itemValidations[report.id] && (
                          <div className="mt-3">
                            <pre className="whitespace-pre-wrap text-xs text-gray-800 dark:text-gray-200">{itemValidations[report.id]}</pre>
                          </div>
                        )}
                        
                        {/* Footer */}
                        {report.location && (
                          <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mt-2">
                            <MapPin size={14} />
                            {report.location}
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <div className="max-w-md mx-auto">
                    <MessageSquare size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                      No Reports Found
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      No social media reports found for <strong>{location}</strong>
                      {date && ` on ${date}`}. Try searching for a different location or date.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Empty State */}
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


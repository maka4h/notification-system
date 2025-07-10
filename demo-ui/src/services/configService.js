// Configuration service for fetching backend configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ConfigService {
  constructor() {
    this.cache = new Map();
    this.cacheExpiry = new Map();
    this.CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
  }

  async fetchWithCache(endpoint) {
    const now = Date.now();
    
    // Check if we have valid cached data
    if (this.cache.has(endpoint) && this.cacheExpiry.has(endpoint)) {
      if (now < this.cacheExpiry.get(endpoint)) {
        return this.cache.get(endpoint);
      }
    }

    // Fetch fresh data
    try {
      const response = await fetch(`${API_URL}${endpoint}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch ${endpoint}: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Cache the data
      this.cache.set(endpoint, data);
      this.cacheExpiry.set(endpoint, now + this.CACHE_DURATION);
      
      return data;
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error);
      
      // Return cached data if available, even if expired
      if (this.cache.has(endpoint)) {
        return this.cache.get(endpoint);
      }
      
      throw error;
    }
  }

  async getSeverityLevels() {
    const data = await this.fetchWithCache('/config/severity-levels');
    return data.severity_levels || [];
  }

  async getEventTypes() {
    const data = await this.fetchWithCache('/config/event-types');
    return data.event_types || [];
  }

  async getUIConfig() {
    const data = await this.fetchWithCache('/config/ui');
    return data;
  }

  // Helper method to get severity class for UI components
  getSeverityClass(severity, severityLevels = []) {
    const severityConfig = severityLevels.find(s => s.value === severity);
    return severityConfig?.bootstrap_class || 'secondary';
  }

  // Clear cache (useful for testing or forced refresh)
  clearCache() {
    this.cache.clear();
    this.cacheExpiry.clear();
  }
}

// Export singleton instance
export const configService = new ConfigService();
export default configService;

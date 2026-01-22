// frontend/lib/api-config.ts - UPDATE THIS FILE
/**
 * API Configuration
 * 
 * Uses environment variable for API URL to support different environments:
 * - Development: http://localhost:8000
 * - Production: https://api.yourdomain.com
 * 
 * Set NEXT_PUBLIC_API_URL in your .env file or environment variables
 */
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  // Auth
  auth: {
    register: `${API_URL}/api/v1/auth/register`,
    login: `${API_URL}/api/v1/auth/token`,
    me: `${API_URL}/api/v1/auth/me`,
  },
  // Super Admin - NEW
  superAdmin: {
    hospitals: `${API_URL}/api/v1/super-admin/hospitals`,
    hospitalUsers: (hospitalId: number) => `${API_URL}/api/v1/super-admin/hospitals/${hospitalId}/users`,
    addUser: `${API_URL}/api/v1/super-admin/users`,
    allUsers: `${API_URL}/api/v1/super-admin/all-users`,
  },
  // Hospital Admin - NEW
  hospitalAdmin: {
    users: `${API_URL}/api/v1/hospital-admin/users`,
    thresholds: `${API_URL}/api/v1/hospital-admin/thresholds`,
  },

  // Analytics endpoints
  analytics: {
    roiSummary: `${API_URL}/api/v1/analytics/roi-summary`,
    componentUsage: `${API_URL}/api/v1/analytics/component-usage`,
    bloodProductCosts: `${API_URL}/api/v1/analytics/blood-product-costs`,
  },

  // Recommendations
  recommendations: {
    evaluate: `${API_URL}/api/v1/recommendations/evaluate`,
    getById: (id: number) => `${API_URL}/api/v1/recommendations/${id}`,
    getByEncounter: (encounterId: number) => `${API_URL}/api/v1/recommendations/encounter/${encounterId}`,
    recordOutcome: (id: number) => `${API_URL}/api/v1/recommendations/${id}/outcome`,
  },
  // Rules
  rules: {
    list: `${API_URL}/api/v1/rules`,
    versions: `${API_URL}/api/v1/rules/versions`,
  },
  // PDF
  pdf: {
    encounter: (encounterId: number, language: string = 'en') => 
      `${API_URL}/api/v1/pdf/encounter/${encounterId}/pdf?language=${language}`,
    recommendation: (recommendationId: number, language: string = 'en') => 
      `${API_URL}/api/v1/pdf/${recommendationId}/pdf?language=${language}`,
  },
  // Audit
  audit: {
    override: `${API_URL}/api/v1/audit/override`,
    logs: (encounterId: number) => `${API_URL}/api/v1/audit/logs/${encounterId}`,
  },
  // CardioIQ
  cardioiq: {
    evaluate: `${API_URL}/api/v1/cardioiq/evaluate`,
  },
  // Admin
  admin: {
    thresholds: `${API_URL}/api/v1/admin/thresholds`,
    aiEvidenceSummary: `${API_URL}/api/v1/admin/ai/evidence-summary`,
  },
}

// Legacy export for backward compatibility
export const API_CONFIG = {
  BASE_URL: API_URL,
  ...API_ENDPOINTS
};
/**
 * API client for Water Leakage Detection backend.
 * All endpoints hit Flask at /api/* (use Vite proxy or full URL).
 */

const BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '') + '/api';

async function request(path, options = {}) {
  const url = path.startsWith('http') ? path : `${BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || res.statusText);
  }
  return res.json();
}

export const api = {
  /** Latest events for dashboard table */
  getRecentEvents(limit = 50) {
    return request(`/recent-events?limit=${limit}`);
  },

  /** Historical events for charts */
  getEventHistory(limit = 500) {
    return request(`/event-history?limit=${limit}`);
  },

  /** Leak vs No Leak counts */
  getSummary() {
    return request('/summary');
  },

  /** Sensor health (Active/Inactive, last_seen) */
  getSensorHealth() {
    return request('/sensor-health');
  },
};

export default api;

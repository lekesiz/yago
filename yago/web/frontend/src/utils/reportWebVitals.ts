/**
 * YAGO v8.0 - Web Vitals Reporter
 * Tracks Core Web Vitals for performance monitoring
 */

import { onCLS, onFCP, onINP, onLCP, onTTFB, Metric } from 'web-vitals';

/**
 * Performance thresholds (Google's recommended values)
 */
const THRESHOLDS = {
  // Largest Contentful Paint (LCP) - Loading performance
  LCP: { good: 2500, needsImprovement: 4000 },

  // First Input Delay (FID) - Interactivity
  FID: { good: 100, needsImprovement: 300 },

  // Interaction to Next Paint (INP) - Responsiveness
  INP: { good: 200, needsImprovement: 500 },

  // Cumulative Layout Shift (CLS) - Visual Stability
  CLS: { good: 0.1, needsImprovement: 0.25 },

  // First Contentful Paint (FCP) - Loading
  FCP: { good: 1800, needsImprovement: 3000 },

  // Time to First Byte (TTFB) - Server Response
  TTFB: { good: 800, needsImprovement: 1800 },
};

/**
 * Rating based on thresholds
 */
function getRating(name: string, value: number): 'good' | 'needs-improvement' | 'poor' {
  const threshold = THRESHOLDS[name as keyof typeof THRESHOLDS];
  if (!threshold) return 'good';

  if (value <= threshold.good) return 'good';
  if (value <= threshold.needsImprovement) return 'needs-improvement';
  return 'poor';
}

/**
 * Send metric to analytics
 */
function sendToAnalytics(metric: Metric) {
  const { name, value, rating, delta, id } = metric;

  const enrichedMetric = {
    name,
    value,
    rating: getRating(name, value),
    delta,
    id,
    timestamp: Date.now(),
    url: window.location.pathname,
    userAgent: navigator.userAgent,
  };

  // Log to console in development
  if (import.meta.env.DEV) {
    console.log('📊 Web Vital:', enrichedMetric);
  }

  // Send to Google Analytics if available
  if (typeof window.gtag !== 'undefined') {
    window.gtag('event', name, {
      value: Math.round(name === 'CLS' ? value * 1000 : value),
      metric_id: id,
      metric_value: value,
      metric_delta: delta,
      metric_rating: enrichedMetric.rating,
    });
  }

  // Send to custom analytics endpoint
  if (import.meta.env.VITE_ANALYTICS_ENDPOINT) {
    fetch(import.meta.env.VITE_ANALYTICS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(enrichedMetric),
      keepalive: true,
    }).catch(err => console.error('Failed to send metric:', err));
  }

  // Store in localStorage for debugging
  if (import.meta.env.DEV) {
    const metrics = JSON.parse(localStorage.getItem('web-vitals') || '[]');
    metrics.push(enrichedMetric);
    // Keep only last 50 metrics
    localStorage.setItem('web-vitals', JSON.stringify(metrics.slice(-50)));
  }
}

/**
 * Report all Web Vitals
 */
export function reportWebVitals() {
  // Core Web Vitals
  onCLS(sendToAnalytics);
  onINP(sendToAnalytics); // Replaced FID with INP (new standard)
  onLCP(sendToAnalytics);

  // Additional metrics
  onFCP(sendToAnalytics);
  onTTFB(sendToAnalytics);
}

/**
 * Get stored metrics (for debugging)
 */
export function getStoredMetrics(): Metric[] {
  try {
    return JSON.parse(localStorage.getItem('web-vitals') || '[]');
  } catch {
    return [];
  }
}

/**
 * Clear stored metrics
 */
export function clearStoredMetrics() {
  localStorage.removeItem('web-vitals');
}

/**
 * Get performance summary
 */
export function getPerformanceSummary() {
  const metrics = getStoredMetrics();

  if (metrics.length === 0) {
    return null;
  }

  const summary: Record<string, { avg: number; min: number; max: number; count: number }> = {};

  metrics.forEach((metric: any) => {
    if (!summary[metric.name]) {
      summary[metric.name] = { avg: 0, min: Infinity, max: -Infinity, count: 0 };
    }

    const stat = summary[metric.name];
    stat.count++;
    stat.avg = ((stat.avg * (stat.count - 1)) + metric.value) / stat.count;
    stat.min = Math.min(stat.min, metric.value);
    stat.max = Math.max(stat.max, metric.value);
  });

  return summary;
}

// Type augmentation for gtag
declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
  }
}

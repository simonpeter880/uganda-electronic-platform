/**
 * Sentry configuration for Next.js frontend
 */
import * as Sentry from '@sentry/nextjs';

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;
const SENTRY_ENVIRONMENT = process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || 'development';
const SENTRY_RELEASE = process.env.NEXT_PUBLIC_SENTRY_RELEASE;

export function initSentry() {
  if (!SENTRY_DSN) {
    console.warn('⚠️  Sentry DSN not configured. Error tracking disabled.');
    return;
  }

  Sentry.init({
    dsn: SENTRY_DSN,
    environment: SENTRY_ENVIRONMENT,
    release: SENTRY_RELEASE,

    // Performance Monitoring
    tracesSampleRate: parseFloat(process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE || '0.1'),

    // Session Replay
    replaysSessionSampleRate: parseFloat(
      process.env.NEXT_PUBLIC_SENTRY_REPLAY_SESSION_SAMPLE_RATE || '0.1'
    ),
    replaysOnErrorSampleRate: parseFloat(
      process.env.NEXT_PUBLIC_SENTRY_REPLAY_ERROR_SAMPLE_RATE || '1.0'
    ),

    // Don't send PII
    sendDefaultPii: false,

    // Integrations
    integrations: [
      new Sentry.BrowserTracing({
        tracePropagationTargets: [
          'localhost',
          /^\//,
          process.env.NEXT_PUBLIC_SALEOR_API_URL || '',
        ],
      }),
      new Sentry.Replay({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],

    // Error filtering
    beforeSend(event, hint) {
      // Filter out development errors
      if (SENTRY_ENVIRONMENT === 'development') {
        return null;
      }

      // Remove sensitive data
      if (event.request) {
        // Remove auth headers
        if (event.request.headers) {
          delete event.request.headers['Authorization'];
          delete event.request.headers['Cookie'];
        }

        // Remove sensitive query params
        if (event.request.query_string) {
          const sensitiveParams = ['token', 'key', 'secret'];
          let queryString = event.request.query_string;
          sensitiveParams.forEach((param) => {
            queryString = queryString.replace(
              new RegExp(`${param}=[^&]*`, 'gi'),
              `${param}=[Filtered]`
            );
          });
          event.request.query_string = queryString;
        }
      }

      // Add custom tags
      event.tags = {
        ...event.tags,
        platform: 'uganda-electronics-storefront',
      };

      return event;
    },

    // Breadcrumb filtering
    beforeBreadcrumb(breadcrumb, hint) {
      // Don't log console breadcrumbs in production
      if (breadcrumb.category === 'console' && SENTRY_ENVIRONMENT === 'production') {
        return null;
      }

      // Remove sensitive data from XHR breadcrumbs
      if (breadcrumb.category === 'xhr') {
        if (breadcrumb.data?.url) {
          breadcrumb.data.url = breadcrumb.data.url.replace(/token=[^&]*/gi, 'token=[Filtered]');
        }
      }

      return breadcrumb;
    },

    // Ignore specific errors
    ignoreErrors: [
      // Browser extensions
      'top.GLOBALS',
      'chrome-extension://',
      'moz-extension://',
      // Network errors
      'Network request failed',
      'NetworkError',
      // Random plugins/extensions
      'Can\'t find variable: ZiteReader',
      'jigsaw is not defined',
      'ComboSearch is not defined',
      // Common bot errors
      'fb_xd_fragment',
      'ResizeObserver loop limit exceeded',
      'ResizeObserver loop completed with undelivered notifications',
    ],
  });

  console.log(`✅ Sentry initialized (env: ${SENTRY_ENVIRONMENT})`);
}

/**
 * Capture checkout errors with context
 */
export function captureCheckoutError(error: Error, context?: Record<string, any>) {
  Sentry.withScope((scope) => {
    scope.setTag('error_type', 'checkout');
    scope.setContext('checkout', context || {});
    Sentry.captureException(error);
  });
}

/**
 * Capture payment errors with context
 */
export function capturePaymentError(
  provider: string,
  error: Error,
  context?: Record<string, any>
) {
  Sentry.withScope((scope) => {
    scope.setTag('error_type', 'payment');
    scope.setTag('payment_provider', provider);
    scope.setContext('payment', {
      provider,
      ...context,
    });
    Sentry.captureException(error);
  });
}

/**
 * Capture GraphQL errors
 */
export function captureGraphQLError(operation: string, error: any) {
  Sentry.withScope((scope) => {
    scope.setTag('error_type', 'graphql');
    scope.setContext('graphql', {
      operation,
      error: error.message,
    });
    Sentry.captureException(error);
  });
}

/**
 * Set user context (without PII)
 */
export function setUserContext(userId?: string) {
  if (userId) {
    // Hash the user ID for privacy
    const hashedId = hashString(userId);
    Sentry.setUser({ id: hashedId });
  } else {
    Sentry.setUser(null);
  }
}

/**
 * Simple hash function for user IDs
 */
function hashString(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(16);
}

/**
 * Track page performance
 */
export function trackPagePerformance(pageName: string) {
  const transaction = Sentry.startTransaction({
    op: 'pageload',
    name: pageName,
  });

  return {
    finish: () => transaction.finish(),
  };
}

/**
 * Track API call performance
 */
export function trackAPICall(operation: string) {
  const span = Sentry.startSpan({
    op: 'api.call',
    name: operation,
  });

  return {
    finish: () => span?.end(),
  };
}

/**
 * API client for backend communication.
 */

import type { IntentRequest, StructuredSpec, ErrorResponse } from '../types/spec';

// Get API URL from environment or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 5000;

/**
 * Custom error class for API errors.
 */
export class APIError extends Error {
  constructor(
    message: string,
    public code: string,
    public details: string,
    public suggestions?: string[]
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Fetch wrapper with timeout and error handling.
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeout: number = API_TIMEOUT
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new APIError(
        'Request timeout',
        'TIMEOUT_ERROR',
        `Request took longer than ${timeout}ms`
      );
    }
    throw error;
  }
}

/**
 * Generate structured specification from user intent.
 *
 * @param intent - User intent text
 * @returns Structured specification
 * @throws APIError for validation errors or server errors
 */
export async function generateSpec(intent: string): Promise<StructuredSpec> {
  const request: IntentRequest = { text: intent };

  try {
    const response = await fetchWithTimeout(`${API_URL}/api/v1/spec`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      // Parse error response
      const errorData: ErrorResponse = await response.json();
      throw new APIError(
        errorData.error,
        errorData.code,
        errorData.details,
        errorData.suggestions
      );
    }

    const spec: StructuredSpec = await response.json();
    return spec;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    // Network or other errors
    if (error instanceof TypeError) {
      throw new APIError(
        'Network error',
        'NETWORK_ERROR',
        'Could not connect to the API server. Please ensure the backend is running.'
      );
    }

    // Unknown error
    throw new APIError(
      'Unknown error',
      'UNKNOWN_ERROR',
      error instanceof Error ? error.message : 'An unknown error occurred'
    );
  }
}

/**
 * Check API health status.
 *
 * @returns Health status object
 */
export async function checkHealth(): Promise<{
  status: string;
  version: string;
  timestamp: string;
}> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/api/v1/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return await response.json();
  } catch (error) {
    throw new APIError(
      'Health check failed',
      'HEALTH_CHECK_FAILED',
      error instanceof Error ? error.message : 'Could not check API health'
    );
  }
}

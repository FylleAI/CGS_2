import { v4 as uuidv4 } from 'uuid';

export type ApiResult = "OK" | "KO" | "WARN" | "PARTIAL";

export interface ApiHeader {
  result: ApiResult;
  message: string;
  transaction_id: string;
  warning?: string[];
  error?: string[];
}

export interface ApiEnvelope<T = any> {
  header: ApiHeader;
  response: T;
}

export class ApiEnvelopeParser {
  /**
   * Creates a standardized API envelope with the given data
   */
  static createEnvelope<T>(
    data: T,
    result: ApiResult = "OK",
    message: string = "Success",
    warnings?: string[],
    errors?: string[]
  ): ApiEnvelope<T> {
    return {
      header: {
        result,
        message,
        transaction_id: uuidv4(),
        warning: warnings,
        error: errors
      },
      response: data
    };
  }

  /**
   * Parses API response and extracts the response data
   * Handles error cases and validates envelope structure
   */
  static parseResponse<T>(apiResponse: any): T {
    if (!apiResponse) {
      throw new Error('API response is null or undefined');
    }

    // If response is already unwrapped (legacy format), return as is
    if (!apiResponse.header || !apiResponse.response) {
      return apiResponse as T;
    }

    const envelope = apiResponse as ApiEnvelope<T>;
    
    // Log transaction ID for debugging
    if (envelope.header.transaction_id) {
      console.debug(`API Transaction ID: ${envelope.header.transaction_id}`);
    }

    // Handle warnings
    if (envelope.header.warning && envelope.header.warning.length > 0) {
      console.warn('API Warnings:', envelope.header.warning);
    }

    // Handle errors - preserve original envelope structure for error analysis
    if (envelope.header.result === "KO") {
      const errorMessage = envelope.header.error?.join(', ') || envelope.header.message;
      const error = new Error(`API Error: ${errorMessage}`);
      // Attach original envelope to error for detailed analysis
      (error as any).envelope = envelope;
      (error as any).header = envelope.header;
      (error as any).error = envelope.header.error;
      (error as any).message = envelope.header.message;
      throw error;
    }

    // Handle partial success with warnings
    if (envelope.header.result === "WARN" || envelope.header.result === "PARTIAL") {
      console.warn(`API Warning - ${envelope.header.message}:`, envelope.header.warning);
    }

    return envelope.response;
  }

  /**
   * Creates an error envelope
   */
  static createErrorEnvelope(
    message: string,
    errors: string[],
    transactionId?: string
  ): ApiEnvelope<null> {
    return {
      header: {
        result: "KO",
        message,
        transaction_id: transactionId || uuidv4(),
        error: errors
      },
      response: null
    };
  }

  /**
   * Creates a warning envelope
   */
  static createWarningEnvelope<T>(
    data: T,
    message: string,
    warnings: string[],
    transactionId?: string
  ): ApiEnvelope<T> {
    return {
      header: {
        result: "WARN",
        message,
        transaction_id: transactionId || uuidv4(),
        warning: warnings
      },
      response: data
    };
  }

  /**
   * Creates a partial success envelope
   */
  static createPartialEnvelope<T>(
    data: T,
    message: string,
    warnings?: string[],
    transactionId?: string
  ): ApiEnvelope<T> {
    return {
      header: {
        result: "PARTIAL",
        message,
        transaction_id: transactionId || uuidv4(),
        warning: warnings
      },
      response: data
    };
  }
}

// Utility function for common success envelope creation
export function createSuccessEnvelope<T>(data: T, message: string = "Operation completed successfully"): ApiEnvelope<T> {
  return ApiEnvelopeParser.createEnvelope(data, "OK", message);
}

// Utility function for API calls with envelope parsing
// Enhanced error class to preserve HTTP status information
export class ApiError extends Error {
  public envelope?: ApiEnvelope<any>;
  public header?: ApiHeader;
  public error?: string[];

  constructor(
    message: string,
    public status?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
    
    // If response contains envelope structure, preserve it
    if (response?.header) {
      this.envelope = response;
      this.header = response.header;
      this.error = response.header.error;
    }
  }
}

export async function fetchWithEnvelope<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      let responseData;
      try {
        responseData = await response.json();
      } catch {
        responseData = null;
      }
      
      // Create enhanced error with status and response data
      const errorMessage = responseData?.header?.message || `HTTP ${response.status}: ${response.statusText}`;
      const apiError = new ApiError(errorMessage, response.status, responseData);
      
      // Preserve original error structure for tenant resolution detection
      if (responseData?.header) {
        (apiError as any).originalEnvelope = responseData;
        (apiError as any).originalHeader = responseData.header;
        (apiError as any).originalError = responseData.header.error;
      }
      
      throw apiError;
    }
    
    const data = await response.json();
    return ApiEnvelopeParser.parseResponse<T>(data);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof Error) {
      throw new ApiError(error.message);
    }
    throw new ApiError('Unknown error occurred during API call');
  }
}
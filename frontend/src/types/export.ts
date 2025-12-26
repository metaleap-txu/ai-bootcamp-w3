/**
 * TypeScript types for data export functionality.
 * Mirrors backend Pydantic schemas for type safety.
 */

/**
 * Export file format options
 */
export type ExportFormat = 'csv' | 'json';

/**
 * Export operation status
 */
export type ExportStatus = 'pending' | 'processing' | 'completed' | 'failed';

/**
 * Query result data structure for export
 */
export interface QueryResultData {
  columns: string[];
  rows: Record<string, any>[];
  total_rows: number;
}

/**
 * Export customization options
 */
export interface ExportOptions {
  pretty?: boolean;
  include_bom?: boolean;
  include_metadata?: boolean;
}

/**
 * Export request payload
 */
export interface ExportRequest {
  query_history_id?: number;
  query_result?: QueryResultData;
  format: ExportFormat;
  options?: ExportOptions;
  filename?: string;
}

/**
 * Streaming export response (for SSE)
 */
export interface ExportResponseStreaming {
  status: ExportStatus;
  progress?: number;
  current_row?: number;
  total_rows?: number;
  download_url?: string;
  error?: string;
}

/**
 * Export preferences creation payload
 */
export interface ExportPreferencesCreate {
  user_id: string;
  default_format?: ExportFormat;
  include_headers?: boolean;
  pretty_print?: boolean;
  auto_download?: boolean;
}

/**
 * Export preferences update payload
 */
export interface ExportPreferencesUpdate {
  default_format?: ExportFormat;
  include_headers?: boolean;
  pretty_print?: boolean;
  auto_download?: boolean;
}

/**
 * Export preferences response
 */
export interface ExportPreferencesResponse {
  user_id: string;
  default_format: ExportFormat;
  include_headers: boolean;
  pretty_print: boolean;
  auto_download: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Export history entry creation payload (internal)
 */
export interface ExportHistoryCreate {
  user_id: string;
  query_history_id?: number;
  format: ExportFormat;
  filename: string;
  row_count: number;
  file_size_bytes?: number;
  status?: ExportStatus;
  error_message?: string;
}

/**
 * Export history entry response
 */
export interface ExportHistoryResponse {
  id: number;
  user_id: string;
  query_history_id?: number;
  format: ExportFormat;
  filename: string;
  row_count: number;
  file_size_bytes?: number;
  exported_at: string;
  status: ExportStatus;
  error_message?: string;
}

/**
 * Export history list response
 */
export interface ExportHistoryListResponse {
  items: ExportHistoryResponse[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Error response structure
 */
export interface ErrorResponse {
  detail: string;
  error_code?: string;
  timestamp: string;
}

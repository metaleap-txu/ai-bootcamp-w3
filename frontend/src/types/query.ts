/**
 * TypeScript types for query execution and validation.
 */

export interface ColumnMetadata {
  name: string;
  type: string;
}

export interface QueryExecuteRequest {
  connection_id: number;
  sql: string;
}

export interface QueryResult {
  columns: ColumnMetadata[];
  rows: any[][];
  row_count: number;
  execution_time_ms: number;
  transformed_sql?: string;
  message?: string;
}

export interface QueryValidateRequest {
  sql: string;
}

export interface ValidationResult {
  valid: boolean;
  error?: string;
  transformed_sql?: string;
  message?: string;
}

export interface QueryHistoryItem {
  id: number;
  connection_id: number;
  query_text: string;
  executed_at: string;
  execution_time_ms: number;
  row_count?: number;
  success: boolean;
  error_message?: string;
}

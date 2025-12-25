/**
 * TypeScript types for Natural Language to SQL.
 */

export interface NL2SQLRequest {
  connection_id: number;
  natural_language: string;
}

export interface NL2SQLResponse {
  sql: string;
  explanation: string;
  confidence: 'high' | 'medium' | 'low';
  warnings?: string;
}

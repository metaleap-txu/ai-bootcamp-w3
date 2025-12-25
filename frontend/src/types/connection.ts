/**
 * TypeScript types for database connections.
 */

export interface Connection {
  id: number;
  name: string;
  host: string;
  port: number;
  database: string;
  username: string;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConnectionCreate {
  name: string;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  description?: string;
}

export interface ConnectionUpdate {
  name?: string;
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  description?: string;
}

export interface ConnectionTestRequest {
  connection_id?: number;
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
}

export interface ConnectionTestResponse {
  success: boolean;
  message: string;
  error?: string;
}

/**
 * Service for query execution and validation API calls.
 */
import { apiClient } from '../utils/api';
import type {
  QueryExecuteRequest,
  QueryResult,
  QueryValidateRequest,
  ValidationResult,
  QueryHistoryItem,
} from '../types/query';

const BASE_URL = '/queries';

export const queryService = {
  /**
   * Execute a SQL query.
   */
  async execute(request: QueryExecuteRequest): Promise<QueryResult> {
    const response = await apiClient.post<QueryResult>(
      `${BASE_URL}/execute`,
      request
    );
    return response.data;
  },

  /**
   * Validate SQL syntax.
   */
  async validate(request: QueryValidateRequest): Promise<ValidationResult> {
    const response = await apiClient.post<ValidationResult>(
      `${BASE_URL}/validate`,
      request
    );
    return response.data;
  },

  /**
   * Get query history for a connection.
   */
  async getHistory(
    connectionId: number,
    limit: number = 50
  ): Promise<QueryHistoryItem[]> {
    const response = await apiClient.get<QueryHistoryItem[]>(
      `${BASE_URL}/history/${connectionId}`,
      { params: { limit } }
    );
    return response.data;
  },
};

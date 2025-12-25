/**
 * Service for Natural Language to SQL API calls.
 */
import { apiClient } from '../utils/api';
import type { NL2SQLRequest, NL2SQLResponse } from '../types/nl2sql';

const BASE_URL = '/nl2sql';

export const nl2sqlService = {
  /**
   * Generate SQL from natural language description.
   */
  async generateSQL(request: NL2SQLRequest): Promise<NL2SQLResponse> {
    const response = await apiClient.post<NL2SQLResponse>(
      `${BASE_URL}/generate`,
      request
    );
    return response.data;
  },
};

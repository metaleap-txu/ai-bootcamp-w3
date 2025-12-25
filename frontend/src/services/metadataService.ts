/**
 * Service for metadata API calls.
 */
import { apiClient } from '../utils/api';
import type {
  Schema,
  Table,
  TableDetails,
  MetadataRefreshResponse,
} from '../types/metadata';

const BASE_URL = '/metadata';

export const metadataService = {
  /**
   * Get list of schemas for a connection.
   */
  async listSchemas(
    connectionId: number,
    useCache: boolean = true
  ): Promise<Schema[]> {
    const response = await apiClient.get<Schema[]>(
      `${BASE_URL}/${connectionId}/schemas`,
      { params: { use_cache: useCache } }
    );
    return response.data;
  },

  /**
   * Get list of tables for a schema.
   */
  async listTables(
    connectionId: number,
    schemaName: string,
    useCache: boolean = true
  ): Promise<Table[]> {
    const response = await apiClient.get<Table[]>(
      `${BASE_URL}/${connectionId}/schemas/${encodeURIComponent(schemaName)}/tables`,
      { params: { use_cache: useCache } }
    );
    return response.data;
  },

  /**
   * Get detailed information about a table.
   */
  async getTableDetails(
    connectionId: number,
    schemaName: string,
    tableName: string,
    useCache: boolean = true
  ): Promise<TableDetails> {
    const response = await apiClient.get<TableDetails>(
      `${BASE_URL}/${connectionId}/schemas/${encodeURIComponent(
        schemaName
      )}/tables/${encodeURIComponent(tableName)}`,
      { params: { use_cache: useCache } }
    );
    return response.data;
  },

  /**
   * Refresh metadata cache for a connection.
   */
  async refresh(connectionId: number): Promise<MetadataRefreshResponse> {
    const response = await apiClient.post<MetadataRefreshResponse>(
      `${BASE_URL}/${connectionId}/refresh`
    );
    return response.data;
  },
};

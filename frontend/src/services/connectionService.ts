/**
 * Service for database connection management API calls.
 */
import { apiClient } from '../utils/api';
import type {
  Connection,
  ConnectionCreate,
  ConnectionUpdate,
  ConnectionTestRequest,
  ConnectionTestResponse,
} from '../types/connection';

const BASE_URL = '/connections';

export const connectionService = {
  /**
   * Get all connections.
   */
  async getAll(): Promise<Connection[]> {
    const response = await apiClient.get<Connection[]>(BASE_URL);
    return response.data;
  },

  /**
   * Get a connection by ID.
   */
  async getById(id: number): Promise<Connection> {
    const response = await apiClient.get<Connection>(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Create a new connection.
   */
  async create(data: ConnectionCreate): Promise<Connection> {
    const response = await apiClient.post<Connection>(BASE_URL, data);
    return response.data;
  },

  /**
   * Update an existing connection.
   */
  async update(id: number, data: ConnectionUpdate): Promise<Connection> {
    const response = await apiClient.put<Connection>(`${BASE_URL}/${id}`, data);
    return response.data;
  },

  /**
   * Delete a connection.
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`${BASE_URL}/${id}`);
  },

  /**
   * Test a database connection.
   */
  async test(request: ConnectionTestRequest): Promise<ConnectionTestResponse> {
    const response = await apiClient.post<ConnectionTestResponse>(
      `${BASE_URL}/test`,
      request
    );
    return response.data;
  },
};

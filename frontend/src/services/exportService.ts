/**
 * Service for exporting query results with CSV and JSON formats.
 */
import { apiClient } from '../utils/api';
import type {
  ExportRequest,
  ExportFormat,
  ExportOptions,
  QueryResultData,
} from '../types/export';

const BASE_URL = '/exports';

export const exportService = {
  /**
   * Export query results in specified format.
   */
  async exportData(
    queryResult: QueryResultData,
    format: ExportFormat,
    filename?: string,
    options?: ExportOptions
  ): Promise<void> {
    const request: ExportRequest = {
      query_result: queryResult,
      format,
      filename,
      options,
    };

    const endpoint = format === 'csv' ? `${BASE_URL}/csv` : `${BASE_URL}/json`;

    try {
      const response = await apiClient.post(endpoint, request, {
        responseType: 'blob',
      });

      // Extract filename from Content-Disposition header
      const contentDisposition = response.headers['content-disposition'];
      let filename = `export_${Date.now()}.${format}`;
      
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="([^"]+)"/);
        if (match) {
          filename = match[1];
        }
      }

      // Trigger download
      downloadFile(response.data, filename);
    } catch (error) {
      console.error(`Export to ${format.toUpperCase()} failed:`, error);
      throw new Error(`Failed to export data as ${format.toUpperCase()}`);
    }
  },

  /**
   * Export results to CSV format.
   */
  async exportCSV(
    queryResult: QueryResultData,
    filename?: string,
    options?: ExportOptions
  ): Promise<void> {
    return this.exportData(queryResult, 'csv', filename, options);
  },

  /**
   * Export results to JSON format.
   */
  async exportJSON(
    queryResult: QueryResultData,
    filename?: string,
    options?: ExportOptions
  ): Promise<void> {
    return this.exportData(queryResult, 'json', filename, options);
  },
};

/**
 * Trigger file download in browser.
 */
function downloadFile(blob: Blob, filename: string): void {
  // Create a temporary download link
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;

  // Trigger download
  document.body.appendChild(link);
  link.click();

  // Cleanup
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * Service for exporting query results.
 */
import { apiClient } from '../utils/api';

const BASE_URL = '/exports';

export interface ExportRequest {
  columns: string[];
  rows: any[][];
  filename: string;
}

export const exportService = {
  /**
   * Export results to CSV format.
   */
  async exportCSV(request: ExportRequest): Promise<void> {
    const response = await apiClient.post(`${BASE_URL}/csv`, request, {
      responseType: 'blob',
    });
    
    downloadFile(response.data, `${request.filename}.csv`, 'text/csv');
  },

  /**
   * Export results to JSON format.
   */
  async exportJSON(request: ExportRequest): Promise<void> {
    const response = await apiClient.post(`${BASE_URL}/json`, request, {
      responseType: 'blob',
    });
    
    downloadFile(
      response.data,
      `${request.filename}.json`,
      'application/json'
    );
  },

  /**
   * Export results to Excel format.
   */
  async exportExcel(request: ExportRequest): Promise<void> {
    const response = await apiClient.post(`${BASE_URL}/excel`, request, {
      responseType: 'blob',
    });
    
    downloadFile(
      response.data,
      `${request.filename}.xlsx`,
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
  },
};

/**
 * Trigger file download in browser.
 */
function downloadFile(blob: Blob, filename: string, mimeType: string): void {
  // Create a blob with the correct mime type
  const file = new Blob([blob], { type: mimeType });
  
  // Create a temporary download link
  const url = window.URL.createObjectURL(file);
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

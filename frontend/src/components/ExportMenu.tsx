/**
 * Component for exporting query results to CSV and JSON formats.
 * 
 * Supported formats:
 * - CSV: RFC 4180 compliant comma-separated values
 * - JSON: Standard JSON array of objects
 * 
 * Features:
 * - Dropdown menu with CSV and JSON export options
 * - Loading state during export (button disabled with spinner)
 * - Success/error toast notifications
 * - Browser download triggered automatically with timestamped filename
 * - Exports all rows (not just current page visible in table)
 * - Support for custom filename prefix
 * - Optional headers and pretty printing
 * 
 * Props:
 * - result: Query result with columns and rows
 * - filename: Base filename prefix (default: "query_results")
 */
import React, { useState } from 'react';
import { Dropdown, Button, message } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { exportService } from '../services/exportService';
import type { QueryResult } from '../types/query';
import type { QueryResultData, ExportFormat, ExportOptions } from '../types/export';

interface ExportMenuProps {
  result: QueryResult;
  filename?: string;
}

export const ExportMenu: React.FC<ExportMenuProps> = ({
  result,
  filename = 'query_results',
}) => {
  const [exporting, setExporting] = useState(false);

  const handleExport = async (format: ExportFormat) => {
    setExporting(true);
    
    try {
      // Extract column names from result
      const columns = result.columns.map((col) => col.name);
      
      // Convert rows to dict format
      const rows = result.rows.map(row => {
        const rowDict: Record<string, any> = {};
        columns.forEach((col, idx) => {
          rowDict[col] = row[idx];
        });
        return rowDict;
      });
      
      // Prepare query result data
      const queryResult: QueryResultData = {
        columns,
        rows,
        total_rows: result.rows.length,
      };
      
      // Export options
      const options: ExportOptions = {
        pretty: format === 'json', // Pretty print for JSON
      };
      
      // Call appropriate export method
      if (format === 'csv') {
        await exportService.exportCSV(queryResult, filename, options);
        message.success('CSV file downloaded successfully');
      } else {
        await exportService.exportJSON(queryResult, filename, options);
        message.success('JSON file downloaded successfully');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
      message.error(`Export failed: ${errorMessage}`);
      console.error('Export error:', error);
    } finally {
      setExporting(false);
    }
  };

  const menuItems: MenuProps['items'] = [
    {
      key: 'csv',
      label: 'Export as CSV',
      onClick: () => handleExport('csv'),
    },
    {
      key: 'json',
      label: 'Export as JSON',
      onClick: () => handleExport('json'),
    },
  ];

  return (
    <Dropdown menu={{ items: menuItems }} disabled={exporting}>
      <Button icon={<DownloadOutlined />} loading={exporting}>
        Export Results
      </Button>
    </Dropdown>
  );
};

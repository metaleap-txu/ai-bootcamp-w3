/**
 * Component for exporting query results to various formats.
 * 
 * Supported formats:
 * - CSV: Comma-separated values for Excel/Google Sheets
 * - JSON: Array of objects for programmatic consumption
 * - Excel: XLSX format with formatted headers
 * 
 * Features:
 * - Dropdown menu with 3 export options
 * - Loading state during export (button disabled with spinner)
 * - Success/error toast notifications
 * - Browser download triggered automatically with generated filename
 * - Exports all rows (not just current page visible in table)
 * 
 * Props:
 * - result: Query result with columns and rows
 * - filename: Base filename without extension (default: "query_results")
 */
import React, { useState } from 'react';
import { Dropdown, Button, message } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { exportService } from '../services/exportService';
import type { QueryResult } from '../types/query';

interface ExportMenuProps {
  result: QueryResult;
  filename?: string;
}

export const ExportMenu: React.FC<ExportMenuProps> = ({
  result,
  filename = 'query_results',
}) => {
  const [exporting, setExporting] = useState(false);

  const handleExport = async (format: 'csv' | 'json' | 'excel') => {
    setExporting(true);
    
    try {
      // Extract column names from result
      const columns = result.columns.map((col) => col.name);
      
      // Prepare export request
      const exportRequest = {
        columns,
        rows: result.rows,
        filename,
      };
      
      // Call appropriate export method
      switch (format) {
        case 'csv':
          await exportService.exportCSV(exportRequest);
          message.success('CSV file downloaded successfully');
          break;
        case 'json':
          await exportService.exportJSON(exportRequest);
          message.success('JSON file downloaded successfully');
          break;
        case 'excel':
          await exportService.exportExcel(exportRequest);
          message.success('Excel file downloaded successfully');
          break;
      }
    } catch (error: any) {
      message.error(`Export failed: ${error.response?.data?.detail || error.message}`);
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
    {
      key: 'excel',
      label: 'Export as Excel',
      onClick: () => handleExport('excel'),
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

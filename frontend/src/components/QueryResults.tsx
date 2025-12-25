/**
 * Component for displaying query results in a table.
 * 
 * Features:
 * - Column headers with data type badges
 * - Data type-aware formatting:
 *   - Booleans as green/red tags (TRUE/FALSE)
 *   - Dates/timestamps formatted with toLocaleString()
 *   - Numbers with thousands separators (1,000,000)
 *   - NULL values displayed as italic gray text
 *   - JSON objects with pretty-printed formatting
 * - Export menu (CSV/JSON/Excel)
 * - Pagination with configurable page sizes (50/100/500/1000)
 * - Execution metadata (row count, time, warnings)
 * - Horizontal and vertical scrolling for large result sets
 * 
 * Props:
 * - result: Query result with columns, rows, and metadata
 * - loading: Show loading spinner (default: false)
 */
import React from 'react';
import { Table, Typography, Tag, Space } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { QueryResult } from '../types/query';
import { ExportMenu } from './ExportMenu';

const { Text } = Typography;

interface QueryResultsProps {
  result: QueryResult | null;
  loading?: boolean;
}

export const QueryResults: React.FC<QueryResultsProps> = ({
  result,
  loading = false,
}) => {
  if (!result && !loading) {
    return (
      <div style={{ textAlign: 'center', padding: '48px', color: '#999' }}>
        <Text type="secondary">
          Execute a query to see results here
        </Text>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  // Build columns from result metadata
  const columns: ColumnsType<any> = result.columns.map((col) => ({
    title: (
      <Space direction="vertical" size={0}>
        <strong>{col.name}</strong>
        <Tag color="blue" style={{ fontSize: '10px' }}>
          {col.type}
        </Tag>
      </Space>
    ),
    dataIndex: col.name,
    key: col.name,
    render: (value: any) => {
      if (value === null || value === undefined) {
        return <Text type="secondary" italic>NULL</Text>;
      }
      // Boolean formatting
      if (typeof value === 'boolean') {
        return <Tag color={value ? 'green' : 'red'}>{value ? 'TRUE' : 'FALSE'}</Tag>;
      }
      // Date/timestamp formatting
      if (col.type.toLowerCase().includes('date') || col.type.toLowerCase().includes('time')) {
        try {
          const date = new Date(value);
          if (!isNaN(date.getTime())) {
            return date.toLocaleString();
          }
        } catch (e) {
          // Fall through to default
        }
      }
      // Number formatting with thousands separators
      if (typeof value === 'number') {
        return value.toLocaleString();
      }
      // Object/JSON formatting
      if (typeof value === 'object') {
        return <pre style={{ margin: 0 }}>{JSON.stringify(value, null, 2)}</pre>;
      }
      return String(value);
    },
    ellipsis: true,
  }));

  // Convert rows to objects with column names as keys
  const dataSource = result.rows.map((row, index) => {
    const rowData: any = { key: index };
    result.columns.forEach((col, colIndex) => {
      rowData[col.name] = row[colIndex];
    });
    return rowData;
  });

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Text strong>
            {result.row_count} {result.row_count === 1 ? 'row' : 'rows'}
          </Text>
          <Text type="secondary">•</Text>
          <Text type="secondary">{result.execution_time_ms}ms</Text>
          {result.message && (
            <>
              <Text type="secondary">•</Text>
              <Tag color="orange">{result.message}</Tag>
            </>
          )}
        </Space>
        <ExportMenu result={result} filename="query_results" />
      </div>
      <Table
        columns={columns}
        dataSource={dataSource}
        loading={loading}
        pagination={{
          pageSize: 100,
          showSizeChanger: true,
          pageSizeOptions: ['50', '100', '500', '1000'],
          showTotal: (total, range) =>
            `${range[0]}-${range[1]} of ${total} rows`,
        }}
        scroll={{ x: 'max-content', y: 500 }}
        size="small"
        bordered
      />
    </div>
  );
};

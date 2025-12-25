/**
 * Interactive tree component for browsing database metadata.
 * 
 * Features:
 * - Three-level hierarchy: Schemas → Tables → Columns
 * - Lazy loading: Children fetched only when parent expanded
 * - Click-to-insert: Click any item to insert into SQL editor
 * - Visual indicators:
 *   - DatabaseOutlined icon for schemas
 *   - TableOutlined icon for tables
 *   - FieldStringOutlined icon for columns
 *   - VIEW tag for views
 *   - NOT NULL badge for non-nullable columns
 *   - KeyOutlined icon for primary keys
 *   - LinkOutlined icon for foreign keys (with target table tooltip)
 * - Row count display: Shows "~X rows" from pg_class estimates
 * - Refresh button: Clears metadata cache and reloads tree
 * - State management: Tracks loaded schemas/tables to prevent duplicate fetches
 * 
 * Props:
 * - connectionId: Database connection ID for metadata fetch
 * - onInsertText: Callback to insert selected text into editor
 */
import React, { useState, useEffect } from 'react';
import { Tree, Button, Space, message, Spin, Typography, Tag, Tooltip } from 'antd';
import {
  ReloadOutlined,
  DatabaseOutlined,
  TableOutlined,
  FieldStringOutlined,
  KeyOutlined,
  LinkOutlined,
} from '@ant-design/icons';
import type { DataNode } from 'antd/es/tree';
import { metadataService } from '../services/metadataService';
import type { Schema, Table, TableDetails } from '../types/metadata';

const { Text } = Typography;

interface MetadataTreeProps {
  connectionId: number | null;
  onInsertText?: (text: string) => void;
}

export const MetadataTree: React.FC<MetadataTreeProps> = ({
  connectionId,
  onInsertText,
}) => {
  const [treeData, setTreeData] = useState<DataNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);
  const [loadedSchemas, setLoadedSchemas] = useState<Set<string>>(new Set());
  const [loadedTables, setLoadedTables] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (connectionId) {
      loadSchemas();
    } else {
      setTreeData([]);
      setLoadedSchemas(new Set());
      setLoadedTables(new Set());
    }
  }, [connectionId]);

  const loadSchemas = async () => {
    if (!connectionId) return;

    setLoading(true);
    try {
      const schemas = await metadataService.listSchemas(connectionId);
      
      const nodes: DataNode[] = schemas.map((schema) => ({
        key: `schema-${schema.name}`,
        title: (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <DatabaseOutlined />
            <Text strong>{schema.name}</Text>
          </span>
        ),
        isLeaf: false,
        children: [],
      }));

      setTreeData(nodes);
    } catch (error) {
      message.error('Failed to load schemas');
    } finally {
      setLoading(false);
    }
  };

  const loadTables = async (schemaName: string): Promise<DataNode[]> => {
    if (!connectionId) return [];

    try {
      const tables = await metadataService.listTables(connectionId, schemaName);
      
      return tables.map((table) => ({
        key: `table-${schemaName}-${table.name}`,
        title: (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <TableOutlined />
            <Text>{table.name}</Text>
            {table.table_type === 'VIEW' && <Tag color="blue">VIEW</Tag>}
          </span>
        ),
        isLeaf: false,
        children: [],
      }));
    } catch (error) {
      message.error(`Failed to load tables for schema ${schemaName}`);
      return [];
    }
  };

  const loadColumns = async (
    schemaName: string,
    tableName: string
  ): Promise<DataNode[]> => {
    if (!connectionId) return [];

    try {
      const details = await metadataService.getTableDetails(
        connectionId,
        schemaName,
        tableName
      );

      const columnNodes: DataNode[] = details.columns.map((column) => {
        const isPrimaryKey = column.name === 'id'; // Simplified - could check constraints
        const foreignKey = details.foreign_keys.find(
          (fk) => fk.column_name === column.name
        );

        return {
          key: `column-${schemaName}-${tableName}-${column.name}`,
          title: (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', flexWrap: 'wrap' }}>
              <FieldStringOutlined />
              <Text strong style={{ whiteSpace: 'nowrap' }}>{column.name}</Text>
              <Tag color="geekblue" style={{ fontSize: '10px', margin: 0 }}>
                {column.data_type}
              </Tag>
              {!column.is_nullable && (
                <Tag color="red" style={{ fontSize: '10px', margin: 0 }}>
                  NOT NULL
                </Tag>
              )}
              {isPrimaryKey && (
                <Tooltip title="Primary Key">
                  <KeyOutlined style={{ color: '#faad14' }} />
                </Tooltip>
              )}
              {foreignKey && (
                <Tooltip
                  title={`FK → ${foreignKey.referenced_table}.${foreignKey.referenced_column}`}
                >
                  <LinkOutlined style={{ color: '#1890ff' }} />
                </Tooltip>
              )}
            </span>
          ),
          isLeaf: true,
        };
      });

      // Add row count info node if available
      if (details.row_count !== null && details.row_count !== undefined) {
        columnNodes.unshift({
          key: `info-${schemaName}-${tableName}`,
          title: (
            <Text type="secondary" italic>
              ~{details.row_count.toLocaleString()} rows
            </Text>
          ),
          isLeaf: true,
          selectable: false,
        });
      }

      return columnNodes;
    } catch (error) {
      message.error(`Failed to load columns for table ${tableName}`);
      return [];
    }
  };

  const handleLoadData = async (node: DataNode): Promise<void> => {
    const key = node.key as string;

    if (key.startsWith('schema-')) {
      const schemaName = key.replace('schema-', '');
      if (loadedSchemas.has(schemaName)) return;

      const tables = await loadTables(schemaName);
      
      setTreeData((prevData) =>
        updateTreeData(prevData, key, tables)
      );
      setLoadedSchemas((prev) => new Set([...prev, schemaName]));
    } else if (key.startsWith('table-')) {
      const [, schemaName, tableName] = key.split('-');
      const tableKey = `${schemaName}-${tableName}`;
      if (loadedTables.has(tableKey)) return;

      const columns = await loadColumns(schemaName, tableName);
      
      setTreeData((prevData) =>
        updateTreeData(prevData, key, columns)
      );
      setLoadedTables((prev) => new Set([...prev, tableKey]));
    }
  };

  const updateTreeData = (
    list: DataNode[],
    key: React.Key,
    children: DataNode[]
  ): DataNode[] => {
    return list.map((node) => {
      if (node.key === key) {
        return { ...node, children };
      }
      if (node.children) {
        return {
          ...node,
          children: updateTreeData(node.children, key, children),
        };
      }
      return node;
    });
  };

  const handleRefresh = async () => {
    if (!connectionId) return;

    setRefreshing(true);
    try {
      await metadataService.refresh(connectionId);
      message.success('Metadata cache refreshed');
      
      // Clear loaded state and reload
      setLoadedSchemas(new Set());
      setLoadedTables(new Set());
      setExpandedKeys([]);
      await loadSchemas();
    } catch (error) {
      message.error('Failed to refresh metadata');
    } finally {
      setRefreshing(false);
    }
  };

  const handleSelect = (selectedKeys: React.Key[], info: any) => {
    if (!onInsertText) return;

    const key = selectedKeys[0] as string;
    if (!key) return;

    if (key.startsWith('table-')) {
      const [, schemaName, tableName] = key.split('-');
      onInsertText(`${schemaName}.${tableName}`);
    } else if (key.startsWith('column-')) {
      const parts = key.split('-');
      const columnName = parts[parts.length - 1];
      onInsertText(columnName);
    }
  };

  if (!connectionId) {
    return (
      <div style={{ textAlign: 'center', padding: '48px', color: '#999' }}>
        <Text type="secondary">Select a connection to browse metadata</Text>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          icon={<ReloadOutlined />}
          onClick={handleRefresh}
          loading={refreshing}
          disabled={loading}
          block
        >
          Refresh Metadata
        </Button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px' }}>
          <Spin tip="Loading schemas..." />
        </div>
      ) : (
        <Tree
          showIcon
          treeData={treeData}
          loadData={handleLoadData}
          onExpand={(keys) => setExpandedKeys(keys)}
          expandedKeys={expandedKeys}
          onSelect={handleSelect}
        />
      )}
    </div>
  );
};

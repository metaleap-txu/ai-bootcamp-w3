/**
 * List component for displaying database connections.
 */
import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Popconfirm, message, Tag, Badge, Tooltip } from 'antd';
import { EditOutlined, DeleteOutlined, ThunderboltOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Connection } from '../types/connection';
import { connectionService } from '../services/connectionService';

interface ConnectionListProps {
  onEdit?: (connection: Connection) => void;
  onRefresh?: () => void;
  refreshTrigger?: number;
}

export const ConnectionList: React.FC<ConnectionListProps> = ({
  onEdit,
  onRefresh,
  refreshTrigger,
}) => {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(false);
  const [testingId, setTestingId] = useState<number | null>(null);

  const fetchConnections = async () => {
    setLoading(true);
    try {
      const data = await connectionService.getAll();
      setConnections(data);
    } catch (error) {
      message.error('Failed to load connections');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConnections();
  }, [refreshTrigger]);

  const handleDelete = async (id: number) => {
    try {
      await connectionService.delete(id);
      message.success('Connection deleted successfully');
      fetchConnections();
      onRefresh?.();
    } catch (error) {
      message.error('Failed to delete connection');
    }
  };

  const handleTest = async (id: number) => {
    setTestingId(id);
    try {
      const result = await connectionService.test({ connection_id: id });
      if (result.success) {
        message.success(result.message);
        fetchConnections(); // Refresh to show updated last_tested_at
      } else {
        message.error(`${result.message}: ${result.error || 'Unknown error'}`);
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to test connection';
      message.error(errorMsg);
      console.error('Connection test error:', error);
    } finally {
      setTestingId(null);
    }
  };

  const formatLastTested = (lastTested: string | null) => {
    if (!lastTested) return 'Never tested';
    const date = new Date(lastTested);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hr ago`;
    return `${diffDays} days ago`;
  };

  const columns: ColumnsType<Connection> = [
    {
      title: 'Status',
      key: 'status',
      width: 120,
      render: (_, record) => (
        <Tooltip title={`Last tested: ${formatLastTested(record.last_tested_at)}`}>
          {record.last_tested_at ? (
            <Badge status="success" text="Tested" />
          ) : (
            <Badge status="default" text="Untested" />
          )}
        </Tooltip>
      ),
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <strong>{text}</strong>,
    },
    {
      title: 'Host',
      dataIndex: 'host',
      key: 'host',
    },
    {
      title: 'Port',
      dataIndex: 'port',
      key: 'port',
    },
    {
      title: 'Database',
      dataIndex: 'database',
      key: 'database',
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (text: string | null) => text || '-',
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => new Date(text).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Connection) => (
        <Space size="small">
          <Button
            size="small"
            icon={<ThunderboltOutlined />}
            onClick={() => handleTest(record.id)}
            loading={testingId === record.id}
          >
            Test
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => onEdit?.(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Are you sure you want to delete this connection?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={connections}
      rowKey="id"
      loading={loading}
      pagination={{
        pageSize: 10,
        showTotal: (total) => `Total ${total} connections`,
      }}
    />
  );
};

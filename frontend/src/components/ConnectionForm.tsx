/**
 * Form component for creating/editing database connections.
 */
import React, { useState } from 'react';
import { Form, Input, InputNumber, Button, message, Space, Card, Alert } from 'antd';
import { SaveOutlined, ThunderboltOutlined, DatabaseOutlined } from '@ant-design/icons';
import type { ConnectionCreate, ConnectionUpdate } from '../types/connection';
import { connectionService } from '../services/connectionService';

interface ConnectionFormProps {
  initialValues?: Partial<ConnectionCreate>;
  onSuccess?: () => void;
  onCancel?: () => void;
  isEdit?: boolean;
  connectionId?: number;
}

export const ConnectionForm: React.FC<ConnectionFormProps> = ({
  initialValues,
  onSuccess,
  onCancel,
  isEdit = false,
  connectionId,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);

  const handleSubmit = async (values: ConnectionCreate | ConnectionUpdate) => {
    setLoading(true);
    try {
      if (isEdit && connectionId) {
        await connectionService.update(connectionId, values as ConnectionUpdate);
        message.success('Connection updated successfully');
      } else {
        await connectionService.create(values as ConnectionCreate);
        message.success('Connection created successfully');
      }
      form.resetFields();
      onSuccess?.();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to save connection');
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    try {
      await form.validateFields();
      const values = form.getFieldsValue();
      
      setTesting(true);
      const result = await connectionService.test({
        host: values.host,
        port: values.port,
        database: values.database,
        username: values.username,
        password: values.password,
      });

      if (result.success) {
        message.success(result.message);
      } else {
        message.error(`${result.message}: ${result.error || 'Unknown error'}`);
      }
    } catch (error: any) {
      if (error.errorFields) {
        message.warning('Please fill in all required fields before testing');
      } else {
        message.error('Failed to test connection');
      }
    } finally {
      setTesting(false);
    }
  };

  return (
    <Card title={isEdit ? 'Edit Connection' : 'Create Connection'}>
      <Alert
        message="Supported Database"
        description={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <DatabaseOutlined />
            <span>PostgreSQL</span>
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      <Form
        form={form}
        layout="vertical"
        initialValues={initialValues}
        onFinish={handleSubmit}
      >
        <Form.Item
          name="name"
          label="Connection Name"
          rules={[{ required: true, message: 'Please enter a connection name' }]}
        >
          <Input placeholder="e.g., Production DB" />
        </Form.Item>

        <Form.Item
          name="host"
          label="Host"
          rules={[{ required: true, message: 'Please enter the host' }]}
        >
          <Input placeholder="localhost" />
        </Form.Item>

        <Form.Item
          name="port"
          label="Port"
          rules={[{ required: true, message: 'Please enter the port' }]}
        >
          <InputNumber
            min={1}
            max={65535}
            placeholder="5432"
            style={{ width: '100%' }}
          />
        </Form.Item>

        <Form.Item
          name="database"
          label="Database"
          rules={[{ required: true, message: 'Please enter the database name' }]}
        >
          <Input placeholder="myapp" />
        </Form.Item>

        <Form.Item
          name="username"
          label="Username"
          rules={[{ required: true, message: 'Please enter the username' }]}
        >
          <Input placeholder="postgres" />
        </Form.Item>

        <Form.Item
          name="password"
          label="Password"
          rules={[
            { required: !isEdit, message: 'Please enter the password' },
          ]}
        >
          <Input.Password
            placeholder={isEdit ? 'Leave blank to keep current password' : 'Enter password'}
          />
        </Form.Item>

        <Form.Item name="description" label="Description">
          <Input.TextArea
            rows={3}
            placeholder="Optional description"
          />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              icon={<SaveOutlined />}
            >
              {isEdit ? 'Update' : 'Create'}
            </Button>
            <Button
              onClick={handleTest}
              loading={testing}
              icon={<ThunderboltOutlined />}
            >
              Test Connection
            </Button>
            {onCancel && (
              <Button onClick={onCancel}>
                Cancel
              </Button>
            )}
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

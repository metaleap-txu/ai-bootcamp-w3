/**
 * Page for managing database connections.
 */
import React, { useState } from 'react';
import { Layout, Typography, Row, Col, Modal, Button, Space } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { ConnectionForm } from '../components/ConnectionForm';
import { ConnectionList } from '../components/ConnectionList';
import type { Connection } from '../types/connection';

const { Content } = Layout;
const { Title } = Typography;

export const ConnectionsPage: React.FC = () => {
  const navigate = useNavigate();
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [editingConnection, setEditingConnection] = useState<Connection | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);

  const handleFormSuccess = () => {
    setRefreshTrigger((prev) => prev + 1);
    setIsModalVisible(false);
    setEditingConnection(null);
  };

  const handleEdit = (connection: Connection) => {
    setEditingConnection(connection);
    setIsModalVisible(true);
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    setEditingConnection(null);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Content style={{ padding: '24px' }}>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Title level={2} style={{ margin: 0 }}>Database Connections</Title>
            <Button 
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/queries')}
            >
              Back to Dashboard
            </Button>
          </div>
          
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={8}>
              <ConnectionForm
                onSuccess={handleFormSuccess}
              />
            </Col>
            
            <Col xs={24} lg={16}>
              <ConnectionList
                onEdit={handleEdit}
                onRefresh={() => setRefreshTrigger((prev) => prev + 1)}
                refreshTrigger={refreshTrigger}
              />
            </Col>
          </Row>
        </Space>

        <Modal
          title="Edit Connection"
          open={isModalVisible}
          onCancel={handleModalCancel}
          footer={null}
          width={600}
        >
          {editingConnection && (
            <ConnectionForm
              isEdit
              connectionId={editingConnection.id}
              initialValues={editingConnection}
              onSuccess={handleFormSuccess}
              onCancel={handleModalCancel}
            />
          )}
        </Modal>
      </Content>
    </Layout>
  );
};

/**
 * Page for executing SQL queries.
 */
import React, { useState, useEffect } from 'react';
import {
  Layout,
  Typography,
  Select,
  Button,
  Space,
  message,
  Card,
  Alert,
  Tabs,
  Input,
  Tag,
} from 'antd';
import {
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  BulbOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { SqlEditor } from '../components/SqlEditor';
import { QueryResults } from '../components/QueryResults';
import { MetadataTree } from '../components/MetadataTree';
import { ExportMenu } from '../components/ExportMenu';
import { connectionService } from '../services/connectionService';
import { queryService } from '../services/queryService';
import { nl2sqlService } from '../services/nl2sqlService';
import type { Connection } from '../types/connection';
import type { QueryResult, ValidationResult } from '../types/query';
import type { NL2SQLResponse } from '../types/nl2sql';

const { Content, Sider } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

export const QueryPage: React.FC = () => {
  const navigate = useNavigate();
  const [connections, setConnections] = useState<Connection[]>([]);
  const [selectedConnectionId, setSelectedConnectionId] = useState<number | null>(null);
  const [sql, setSql] = useState<string>('SELECT * FROM users LIMIT 10;');
  const [executing, setExecuting] = useState(false);
  const [validating, setValidating] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // NL2SQL state
  const [activeTab, setActiveTab] = useState<string>('sql');
  const [naturalLanguage, setNaturalLanguage] = useState<string>('');
  const [generating, setGenerating] = useState(false);
  const [nl2sqlResult, setNl2sqlResult] = useState<NL2SQLResponse | null>(null);

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      const data = await connectionService.getAll();
      setConnections(data);
      if (data.length > 0 && !selectedConnectionId) {
        setSelectedConnectionId(data[0].id);
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to load connections';
      message.error(errorMsg);
      console.error('Connection load error:', error);
    }
  };

  const handleValidate = async () => {
    if (!sql.trim()) {
      message.warning('Please enter a SQL query');
      return;
    }

    setValidating(true);
    setError(null);

    try {
      const result = await queryService.validate({ sql });
      setValidation(result);

      if (result.valid) {
        message.success('SQL is valid');
      } else {
        message.error(result.error || 'SQL validation failed');
      }
    } catch (err: any) {
      message.error('Validation failed');
    } finally {
      setValidating(false);
    }
  };

  const handleExecute = async () => {
    if (!selectedConnectionId || !sql.trim()) {
      message.warning('Please select a connection and enter a SQL query');
      return;
    }

    setExecuting(true);
    setError(null);
    setResult(null);

    try {
      const queryResult = await queryService.execute({
        connection_id: selectedConnectionId,
        sql,
      });
      setResult(queryResult);
      message.success('Query executed successfully');
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail || 'Failed to execute query';
      setError(errorDetail);
      message.error(errorDetail);
      console.error('Query execution error:', err);
    } finally {
      setExecuting(false);
    }
  };

  const handleGenerateSQL = async () => {
    if (!selectedConnectionId) {
      message.warning('Please select a connection');
      return;
    }

    if (!naturalLanguage.trim()) {
      message.warning('Please enter a natural language description');
      return;
    }

    setGenerating(true);
    setNl2sqlResult(null);

    try {
      const response = await nl2sqlService.generateSQL({
        connection_id: selectedConnectionId,
        natural_language: naturalLanguage,
      });

      setNl2sqlResult(response);
      setSql(response.sql);
      setActiveTab('sql');
      message.success('SQL generated successfully');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to generate SQL';
      message.error(errorMessage);
    } finally {
      setGenerating(false);
    }
  };

  const handleInsertText = (text: string) => {
    setSql((prev) => {
      const trimmed = prev.trim();
      if (!trimmed) return text;
      return `${prev} ${text}`;
    });
  };

  const selectedConnection = connections.find((c) => c.id === selectedConnectionId);

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Sider
        width={300}
        style={{ background: '#fff', padding: '16px', overflow: 'auto' }}
      >
        <Title level={4}>Database Metadata</Title>
        <MetadataTree
          connectionId={selectedConnectionId}
          onInsertText={handleInsertText}
        />
      </Sider>

      <Content style={{ padding: '24px' }}>
        <Title level={2}>Execute SQL Query</Title>

        <Card style={{ marginBottom: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <Text strong style={{ marginRight: 8 }}>
                  Connection:
                </Text>
                <Select
                  style={{ width: 300 }}
                  placeholder="Select a connection"
                  value={selectedConnectionId}
                  onChange={setSelectedConnectionId}
                  options={connections.map((conn) => ({
                    label: `${conn.name} (${conn.host}:${conn.port}/${conn.database})`,
                    value: conn.id,
                  }))}
                />
                {selectedConnection && (
                  <Text type="secondary" style={{ marginLeft: 16 }}>
                    User: {selectedConnection.username}
                  </Text>
                )}
              </div>
              <Button 
                type="default" 
                icon={<PlusOutlined />}
                onClick={() => navigate('/connections')}
              >
                Add New Connection
              </Button>
            </div>

            {validation && validation.valid && (
              <Alert
                message="Valid SQL"
                description={
                  validation.message ? (
                    <Text>{validation.message}</Text>
                  ) : (
                    'SQL syntax is valid and ready to execute'
                  )
                }
                type="success"
                icon={<CheckCircleOutlined />}
                showIcon
                closable
                onClose={() => setValidation(null)}
              />
            )}

            {validation && !validation.valid && (
              <Alert
                message="Invalid SQL"
                description={validation.message}
                type="error"
                icon={<CloseCircleOutlined />}
                showIcon
                closable
                onClose={() => setValidation(null)}
              />
            )}

            {error && (
              <Alert
                message="Query Execution Error"
                description={error}
                type="error"
                showIcon
                closable
                onClose={() => setError(null)}
              />
            )}

            <div>
              <Tabs
                activeKey={activeTab}
                onChange={setActiveTab}
                items={[
                  {
                    key: 'sql',
                    label: 'SQL Editor',
                    children: (
                      <div>
                        <div style={{ marginBottom: 8 }}>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            Press Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux) to execute
                          </Text>
                        </div>
                        <SqlEditor
                          value={sql}
                          onChange={setSql}
                          onExecute={handleExecute}
                          height="250px"
                        />
                      </div>
                    ),
                  },
                  {
                    key: 'nl2sql',
                    label: (
                      <Space>
                        <BulbOutlined />
                        Natural Language
                      </Space>
                    ),
                    children: (
                      <div>
                        <div style={{ marginBottom: 8 }}>
                          <Text strong>Describe your query in plain English</Text>
                        </div>
                        <TextArea
                          rows={4}
                          placeholder="e.g., Show me all users who registered in the last 30 days"
                          value={naturalLanguage}
                          onChange={(e) => setNaturalLanguage(e.target.value)}
                          style={{ marginBottom: 16 }}
                        />
                        
                        {nl2sqlResult && (
                          <div style={{ marginBottom: 16 }}>
                            <Alert
                              message={
                                <Space>
                                  <Text strong>Generated SQL</Text>
                                  <Tag
                                    color={
                                      nl2sqlResult.confidence === 'high'
                                        ? 'green'
                                        : nl2sqlResult.confidence === 'medium'
                                        ? 'orange'
                                        : 'red'
                                    }
                                  >
                                    {nl2sqlResult.confidence} confidence
                                  </Tag>
                                </Space>
                              }
                              description={
                                <div>
                                  <Text>{nl2sqlResult.explanation}</Text>
                                  {nl2sqlResult.warnings && (
                                    <div style={{ marginTop: 8 }}>
                                      <Text type="warning">⚠️ {nl2sqlResult.warnings}</Text>
                                    </div>
                                  )}
                                </div>
                              }
                              type={nl2sqlResult.confidence === 'low' ? 'warning' : 'info'}
                              showIcon
                            />
                          </div>
                        )}
                        
                        <Button
                          type="primary"
                          icon={<BulbOutlined />}
                          onClick={handleGenerateSQL}
                          loading={generating}
                          disabled={!selectedConnectionId}
                        >
                          Generate SQL
                        </Button>
                      </div>
                    ),
                  },
                ]}
              />
            </div>

            <Space>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleExecute}
                loading={executing}
                disabled={!selectedConnectionId}
              >
                Execute Query
              </Button>
              <Button onClick={handleValidate} loading={validating}>
                Validate SQL
              </Button>
            </Space>
          </Space>
        </Card>

        <Card title="Query Results">
          {result && result.rows.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <ExportMenu result={result} filename="query_results" />
            </div>
          )}
          <QueryResults result={result} loading={executing} />
        </Card>
      </Content>
    </Layout>
  );
};

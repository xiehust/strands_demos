'use client';

import { useState } from 'react';
import {
  Modal,
  Box,
  SpaceBetween,
  Button,
  FormField,
  Input,
  Alert,
  Container,
  Header,
  ColumnLayout,
  StatusIndicator,
} from '@cloudscape-design/components';
import { apiService } from '@/services/api';

interface AgentPreview {
  name: string;
  description: string;
  skills: Array<{
    name: string;
    description: string;
  }>;
}

interface AddAgentModalProps {
  visible: boolean;
  onDismiss: () => void;
  onAgentAdded: () => void;
}

export default function AddAgentModal({ visible, onDismiss, onAgentAdded }: AddAgentModalProps) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentPreview, setAgentPreview] = useState<AgentPreview | null>(null);

  const handleUrlChange = (value: string) => {
    setUrl(value);
    setAgentPreview(null);
    setError(null);
  };

  const previewAgent = async () => {
    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    try {
      setPreviewLoading(true);
      setError(null);
      
      // Call backend to get agent card information
      const response = await fetch('/api/preview_agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      });

      if (!response.ok) {
        throw new Error(`Failed to preview agent: ${response.statusText}`);
      }

      const preview = await response.json();
      setAgentPreview(preview);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to preview agent');
      // Mock preview for development
      // setAgentPreview({
      //   name: 'Sample Agent',
      //   description: 'This is a sample agent for demonstration purposes',
      //   skills: [
      //     {
      //       name: 'Data Processing',
      //       description: 'Process and analyze data efficiently'
      //     },
      //     {
      //       name: 'Text Analysis',
      //       description: 'Analyze and understand text content'
      //     }
      //   ]
      // });
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      await apiService.addAgent({ url: url.trim() });
      
      // Reset form and close modal
      setUrl('');
      setAgentPreview(null);
      onAgentAdded();
      onDismiss();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add agent');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setUrl('');
    setAgentPreview(null);
    setError(null);
    onDismiss();
  };

  return (
    <Modal
      onDismiss={handleCancel}
      visible={visible}
      closeAriaLabel="Close modal"
      footer={
        <Box float="right">
          <SpaceBetween direction="horizontal" size="xs">
            <Button variant="link" onClick={handleCancel}>
              Cancel
            </Button>
            <Button 
              variant="primary" 
              onClick={handleConfirm}
              loading={loading}
              disabled={!url.trim() || previewLoading}
            >
              Add Agent
            </Button>
          </SpaceBetween>
        </Box>
      }
      header="Add Remote Agent"
    >
      <SpaceBetween direction="vertical" size="l">
        {error && (
          <Alert
            statusIconAriaLabel="Error"
            type="error"
            header="Error"
          >
            {error}
          </Alert>
        )}

        <FormField
          label="Agent URL"
          description="Enter the URL of the remote agent you want to add"
        >
          <SpaceBetween direction="horizontal" size="xs">
            <Input
              value={url}
              onChange={({ detail }) => handleUrlChange(detail.value)}
              placeholder="http://localhost:10000"
              disabled={loading}
            />
            <Button
              onClick={previewAgent}
              loading={previewLoading}
              disabled={!url.trim() || loading}
            >
              Preview
            </Button>
          </SpaceBetween>
        </FormField>

        {agentPreview && (
          <Container
            header={
              <Header variant="h2">
                <SpaceBetween direction="horizontal" size="xs" alignItems="center">
                  <span key="title">Agent Preview</span>
                  <StatusIndicator key="status" type="success">Ready to add</StatusIndicator>
                </SpaceBetween>
              </Header>
            }
          >
            <SpaceBetween direction="vertical" size="m">
              <ColumnLayout columns={2} variant="text-grid">
                <div>
                  <Box variant="awsui-key-label">Name</Box>
                  <div>{agentPreview.name}</div>
                </div>
                <div>
                  <Box variant="awsui-key-label">URL</Box>
                  <div>{url}</div>
                </div>
              </ColumnLayout>

              <div>
                <Box variant="awsui-key-label">Description</Box>
                <div>{agentPreview.description}</div>
              </div>

              {agentPreview.skills && agentPreview.skills.length > 0 && (
                <div>
                  <Box variant="awsui-key-label">Skills</Box>
                  <SpaceBetween direction="vertical" size="xs">
                    {agentPreview.skills.map((skill, index) => (
                      <Box key={`skill-${index}`} padding={{ left: 's' }}>
                        <SpaceBetween direction="vertical" size="xxs">
                          <Box fontWeight="bold">{skill.name}</Box>
                          <Box color="text-body-secondary">{skill.description}</Box>
                        </SpaceBetween>
                      </Box>
                    ))}
                  </SpaceBetween>
                </div>
              )}
            </SpaceBetween>
          </Container>
        )}
      </SpaceBetween>
    </Modal>
  );
}
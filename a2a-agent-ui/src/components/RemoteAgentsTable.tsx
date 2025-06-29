'use client';

import { useState, useEffect } from 'react';
import {
  Table,
  Header,
  SpaceBetween,
  Button,
  Pagination,
  CollectionPreferences,
  TextFilter,
  Box,
  Alert,
  Toggle,
  Modal,
} from '@cloudscape-design/components';
import { RemoteAgent } from '@/types';
import { apiService } from '@/services/api';
import AddAgentModal from './AddAgentModal';

export default function RemoteAgentsTable() {
  const [agents, setAgents] = useState<RemoteAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedItems, setSelectedItems] = useState<RemoteAgent[]>([]);
  const [currentPageIndex, setCurrentPageIndex] = useState(1);
  const [filteringText, setFilteringText] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [preferences, setPreferences] = useState({
    pageSize: 10,
    wrapLines: false,
    visibleContent: ['id', 'name', 'description', 'url', 'skillName', 'skillDescription', 'enabled'],
  });

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getRemoteAgents();
      setAgents(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch remote agents');
      // Mock data for development
      // setAgents([
      //   {
      //     id: '1',
      //     name: 'Agent Alpha',
      //     description: 'Primary processing agent for data analysis',
      //     url: 'http://agent-alpha.example.com',
      //     skill_name: 'Data Analysis',
      //     skill_description: 'Advanced data analysis and processing capabilities',
      //     status: 'active',
      //     enabled: true,
      //   },
      //   {
      //     id: '2',
      //     name: 'Agent Beta',
      //     description: 'Secondary agent for machine learning tasks',
      //     url: 'http://agent-beta.example.com',
      //     skill_name: 'Machine Learning',
      //     skill_description: 'Machine learning model training and inference',
      //     status: 'active',
      //     enabled: false,
      //   },
      //   {
      //     id: '3',
      //     name: 'Agent Gamma',
      //     description: 'Specialized agent for natural language processing',
      //     url: 'http://agent-gamma.example.com',
      //     skill_name: 'NLP Processing',
      //     skill_description: 'Natural language understanding and generation',
      //     status: 'active',
      //     enabled: true,
      //   },
      // ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAgentAdded = () => {
    fetchAgents(); // Refresh the agents list after adding a new agent
  };

  const handleToggleEnabled = async (agentId: string, enabled: boolean) => {
    try {
      // Update local state immediately for better UX
      setAgents(prevAgents =>
        prevAgents.map(agent =>
          agent.id === agentId ? { ...agent, enabled } : agent
        )
      );

      // Call backend API to update agent enabled status
      await apiService.updateAgentEnabled(agentId, enabled);
      
    } catch (error) {
      // Revert the change if API call fails
      setAgents(prevAgents =>
        prevAgents.map(agent =>
          agent.id === agentId ? { ...agent, enabled: !enabled } : agent
        )
      );
      console.error('Failed to update agent enabled status:', error);
      setError(error instanceof Error ? error.message : 'Failed to update agent status');
    }
  };

  const handleDeleteClick = () => {
    if (selectedItems.length === 0) return;
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    if (selectedItems.length === 0) return;

    try {
      setDeleting(true);
      // Delete all selected agents
      for (const agent of selectedItems) {
        await apiService.deleteAgent({ agent_id: agent.id });
      }
      
      // Clear selection and refresh the list
      setSelectedItems([]);
      setShowDeleteModal(false);
      fetchAgents();
    } catch (error) {
      console.error('Failed to delete agents:', error);
      setError(error instanceof Error ? error.message : 'Failed to delete agents');
    } finally {
      setDeleting(false);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
  };

  const filteredAgents = agents.filter((agent) => {
    const searchText = filteringText.toLowerCase();
    return (
      agent.name.toLowerCase().includes(searchText) ||
      agent.description.toLowerCase().includes(searchText) ||
      agent.skill_name.toLowerCase().includes(searchText) ||
      agent.skill_description.toLowerCase().includes(searchText) ||
      (agent.skills && agent.skills.some(skill =>
        skill.name.toLowerCase().includes(searchText) ||
        skill.description.toLowerCase().includes(searchText)
      ))
    );
  });

  const paginatedAgents = filteredAgents.slice(
    (currentPageIndex - 1) * preferences.pageSize,
    currentPageIndex * preferences.pageSize
  );

  const columnDefinitions = [
    {
      id: 'id',
      header: 'ID',
      cell: (item: RemoteAgent) => item.id,
      sortingField: 'id',
    },
    {
      id: 'name',
      header: 'Name',
      cell: (item: RemoteAgent) => item.name,
      sortingField: 'name',
    },
    {
      id: 'description',
      header: 'Description',
      cell: (item: RemoteAgent) => item.description,
      sortingField: 'description',
    },
    {
      id: 'url',
      header: 'URL',
      cell: (item: RemoteAgent) => (
        <a href={item.url} target="_blank" rel="noopener noreferrer">
          {item.url}
        </a>
      ),
      sortingField: 'url',
    },
    {
      id: 'skillName',
      header: 'Skill Name',
      cell: (item: RemoteAgent) => {
        if (item.skills && item.skills.length > 0) {
          const skillNames = item.skills.map(skill => skill.name);
          return `[${skillNames.join(', ')}]`;
        }
        return item.skill_name || 'N/A';
      },
      sortingField: 'skill_name',
    },
    {
      id: 'skillDescription',
      header: 'Skill Description',
      cell: (item: RemoteAgent) => {
        if (item.skills && item.skills.length > 0) {
          const skillDescriptions = item.skills.map(skill => skill.description);
          return `[${skillDescriptions.join(', ')}]`;
        }
        return item.skill_description || 'N/A';
      },
      sortingField: 'skill_description',
    },
    {
      id: 'enabled',
      header: 'Enabled',
      cell: (item: RemoteAgent) => (
        <Toggle
          checked={item.enabled}
          onChange={({ detail }) => handleToggleEnabled(item.id, detail.checked)}
          ariaLabel={`Enable/disable ${item.name}`}
        />
      ),
      sortingField: 'enabled',
    },
  ];

  return (
    <SpaceBetween direction="vertical" size="l">
      {error && (
        <Alert
          statusIconAriaLabel="Error"
          type="error"
          header="Failed to load remote agents"
          action={
            <Button onClick={fetchAgents} variant="primary">
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      )}
      
      <Table
        columnDefinitions={columnDefinitions}
        items={paginatedAgents}
        loadingText="Loading remote agents..."
        loading={loading}
        selectedItems={selectedItems}
        onSelectionChange={({ detail }) => setSelectedItems(detail.selectedItems)}
        selectionType="multi"
        wrapLines={preferences.wrapLines}
        resizableColumns={true}
        ariaLabels={{
          selectionGroupLabel: 'Remote agents selection',
          allItemsSelectionLabel: ({ selectedItems }) =>
            `${selectedItems.length} ${
              selectedItems.length === 1 ? 'item' : 'items'
            } selected`,
          itemSelectionLabel: ({ selectedItems }, item) => {
            const isItemSelected = selectedItems.filter(
              (i) => i.id === item.id
            ).length;
            return `${item.name} is ${
              isItemSelected ? '' : 'not '
            }selected`;
          },
        }}
        header={
          <Header
            counter={`(${filteredAgents.length})`}
            actions={
              <SpaceBetween direction="horizontal" size="xs">
                <Button onClick={fetchAgents}>Refresh</Button>
                <Button onClick={() => setShowAddModal(true)}>Add Agent</Button>
                <Button
                  onClick={handleDeleteClick}
                  disabled={selectedItems.length === 0}
                >
                  Delete ({selectedItems.length})
                </Button>
              </SpaceBetween>
            }
          >
            Remote Agents
          </Header>
        }
        filter={
          <TextFilter
            filteringText={filteringText}
            onChange={({ detail }) =>
              setFilteringText(detail.filteringText)
            }
            countText={`${filteredAgents.length} matches`}
            filteringAriaLabel="Filter remote agents"
            filteringPlaceholder="Search agents..."
          />
        }
        pagination={
          <Pagination
            currentPageIndex={currentPageIndex}
            pagesCount={Math.ceil(filteredAgents.length / preferences.pageSize)}
            onChange={({ detail }) =>
              setCurrentPageIndex(detail.currentPageIndex)
            }
            ariaLabels={{
              nextPageLabel: 'Next page',
              previousPageLabel: 'Previous page',
              pageLabel: (pageNumber) => `Page ${pageNumber} of all pages`,
            }}
          />
        }
        preferences={
          <CollectionPreferences
            title="Preferences"
            confirmLabel="Confirm"
            cancelLabel="Cancel"
            preferences={preferences}
            pageSizePreference={{
              title: 'Page size',
              options: [
                { value: 10, label: '10 items' },
                { value: 20, label: '20 items' },
                { value: 50, label: '50 items' },
              ],
            }}
            wrapLinesPreference={{
              label: 'Wrap lines',
              description: 'Enable text wrapping in table cells',
            }}
            visibleContentPreference={{
              title: 'Select visible columns',
              options: [
                {
                  label: 'Agent properties',
                  options: columnDefinitions.map(({ id, header }) => ({
                    id,
                    label: header,
                  })),
                },
              ],
            }}
            onConfirm={({ detail }) => {
              setPreferences({
                pageSize: detail.pageSize || preferences.pageSize,
                wrapLines: detail.wrapLines || false,
                visibleContent: detail.visibleContent ? [...detail.visibleContent] : preferences.visibleContent,
              });
            }}
          />
        }
        empty={
          <Box margin={{ vertical: 'xs' }} textAlign="center" color="inherit">
            <SpaceBetween size="m">
              <b>No remote agents</b>
              <Button onClick={fetchAgents}>Refresh</Button>
            </SpaceBetween>
          </Box>
        }
      />
      
      <AddAgentModal
        visible={showAddModal}
        onDismiss={() => setShowAddModal(false)}
        onAgentAdded={handleAgentAdded}
      />

      <Modal
        onDismiss={handleCancelDelete}
        visible={showDeleteModal}
        closeAriaLabel="Close modal"
        footer={
          <Box float="right">
            <SpaceBetween direction="horizontal" size="xs">
              <Button variant="link" onClick={handleCancelDelete}>
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleConfirmDelete}
                loading={deleting}
              >
                Delete
              </Button>
            </SpaceBetween>
          </Box>
        }
        header="Delete Remote Agents"
      >
        <SpaceBetween direction="vertical" size="m">
          <Box>
            Are you sure you want to delete the following {selectedItems.length} remote agent{selectedItems.length > 1 ? 's' : ''}?
          </Box>
          <Box>
            <ul>
              {selectedItems.map((agent) => (
                <li key={agent.id}><strong>{agent.name}</strong> - {agent.description}</li>
              ))}
            </ul>
          </Box>
          <Alert type="warning">
            This action cannot be undone. The agents will be permanently removed from the system.
          </Alert>
        </SpaceBetween>
      </Modal>
    </SpaceBetween>
  );
}
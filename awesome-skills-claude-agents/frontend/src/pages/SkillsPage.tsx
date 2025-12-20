import { useState } from 'react';
import { SearchBar, Button, Modal, SkeletonTable } from '../components/common';
import type { Skill } from '../types';

// Mock data for demo
const mockSkills: Skill[] = [
  {
    id: '1',
    name: 'QueryDatabase',
    description: 'Executes SQL queries on the customer database.',
    createdBy: 'system',
    createdAt: '2025-01-01',
    updatedAt: '2025-01-01',
    version: '1.0.0',
    isSystem: true,
  },
  {
    id: '2',
    name: 'SendEmail',
    description: 'Sends an email to a specified recipient.',
    createdBy: 'user',
    createdAt: '2025-01-02',
    updatedAt: '2025-01-02',
    version: '1.0.0',
    isSystem: false,
  },
  {
    id: '3',
    name: 'GenerateReport',
    description: 'Creates a PDF report from a data source.',
    createdBy: 'user',
    createdAt: '2025-01-03',
    updatedAt: '2025-01-03',
    version: '1.1.0',
    isSystem: false,
  },
];

export default function SkillsPage() {
  const [skills, setSkills] = useState(mockSkills);
  const [searchQuery, setSearchQuery] = useState('');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [isInitialLoading] = useState(false);

  const filteredSkills = skills.filter((skill) =>
    skill.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDelete = (id: string) => {
    setSkills((prev) => prev.filter((skill) => skill.id !== id));
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Skill Management</h1>
      </div>

      {/* Toolbar */}
      <div className="flex items-center justify-between mb-6">
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Filter by name..."
          className="w-96"
        />

        <div className="flex gap-3">
          <Button variant="secondary" icon="upload" onClick={() => setIsUploadModalOpen(true)}>
            Upload ZIP
          </Button>
          <Button icon="auto_awesome" onClick={() => setIsGenerateModalOpen(true)}>
            Create with Agent
          </Button>
        </div>
      </div>

      {/* Skills Table */}
      <div className="bg-dark-card border border-dark-border rounded-xl overflow-hidden">
        {isInitialLoading ? (
          <SkeletonTable rows={5} columns={3} />
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-border">
                <th className="px-6 py-4 text-left text-sm font-medium text-muted uppercase tracking-wider">
                  Skill Name
                </th>
                <th className="px-6 py-4 text-left text-sm font-medium text-muted uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-4 text-right text-sm font-medium text-muted uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredSkills.map((skill) => (
                <tr
                  key={skill.id}
                  className="border-b border-dark-border hover:bg-dark-hover transition-colors"
                >
                  <td className="px-6 py-4">
                    <span className="text-white font-medium">{skill.name}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-muted">{skill.description}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end gap-2">
                      <button className="p-2 rounded-lg text-muted hover:text-white hover:bg-dark-hover transition-colors">
                        <span className="material-symbols-outlined text-xl">edit</span>
                      </button>
                      <button
                        onClick={() => handleDelete(skill.id)}
                        className="p-2 rounded-lg text-muted hover:text-status-error hover:bg-status-error/10 transition-colors"
                      >
                        <span className="material-symbols-outlined text-xl">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}

              {filteredSkills.length === 0 && (
                <tr>
                  <td colSpan={3} className="px-6 py-12 text-center">
                    <span className="material-symbols-outlined text-4xl text-muted mb-2">
                      construction
                    </span>
                    <p className="text-muted">No skills found</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Skill Package"
        size="md"
      >
        <UploadSkillForm
          onClose={() => setIsUploadModalOpen(false)}
          onUpload={(skill) => {
            setSkills((prev) => [...prev, skill]);
            setIsUploadModalOpen(false);
          }}
        />
      </Modal>

      {/* Generate Modal */}
      <Modal
        isOpen={isGenerateModalOpen}
        onClose={() => setIsGenerateModalOpen(false)}
        title="Create Skill with Agent"
        size="lg"
      >
        <GenerateSkillForm
          onClose={() => setIsGenerateModalOpen(false)}
          onGenerate={(skill) => {
            setSkills((prev) => [...prev, skill]);
            setIsGenerateModalOpen(false);
          }}
        />
      </Modal>
    </div>
  );
}

// Upload Skill Form Component
function UploadSkillForm({
  onClose,
  onUpload,
}: {
  onClose: () => void;
  onUpload: (skill: Skill) => void;
}) {
  const [name, setName] = useState('');
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const newSkill: Skill = {
      id: Date.now().toString(),
      name: name || file.name.replace('.zip', ''),
      description: 'Uploaded skill package',
      createdBy: 'user',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      version: '1.0.0',
      isSystem: false,
    };
    onUpload(newSkill);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-muted mb-2">Skill Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter skill name (optional)"
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder:text-muted focus:outline-none focus:border-primary"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-muted mb-2">ZIP File</label>
        <div className="relative">
          <input
            type="file"
            accept=".zip"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            required
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="px-4 py-8 bg-dark-bg border border-dashed border-dark-border rounded-lg text-center">
            <span className="material-symbols-outlined text-3xl text-muted mb-2">upload_file</span>
            <p className="text-white">
              {file ? file.name : 'Click to select or drag and drop'}
            </p>
            <p className="text-sm text-muted mt-1">ZIP files only</p>
          </div>
        </div>
      </div>

      <div className="flex gap-3 pt-4">
        <Button type="button" variant="secondary" className="flex-1" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" className="flex-1" disabled={!file}>
          Upload
        </Button>
      </div>
    </form>
  );
}

// Generate Skill Form Component
function GenerateSkillForm({
  onClose,
  onGenerate,
}: {
  onClose: () => void;
  onGenerate: (skill: Skill) => void;
}) {
  const [description, setDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);

    // Simulate AI generation
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const skillName = description
      .split(' ')
      .slice(0, 2)
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join('');

    const newSkill: Skill = {
      id: Date.now().toString(),
      name: skillName || 'NewSkill',
      description: description,
      createdBy: 'ai-agent',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      version: '1.0.0',
      isSystem: false,
    };

    setIsGenerating(false);
    onGenerate(newSkill);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-muted mb-2">Skill Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe what this skill should do. The AI agent will generate the implementation based on your description."
          rows={5}
          required
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder:text-muted focus:outline-none focus:border-primary resize-none"
        />
      </div>

      <div className="bg-dark-bg border border-dark-border rounded-lg p-4">
        <div className="flex items-start gap-3">
          <span className="material-symbols-outlined text-primary">info</span>
          <div>
            <p className="text-sm text-white font-medium">How it works</p>
            <p className="text-sm text-muted mt-1">
              The AI agent will analyze your description and generate a complete skill package
              including the SKILL.md file, code templates, and configuration.
            </p>
          </div>
        </div>
      </div>

      <div className="flex gap-3 pt-4">
        <Button type="button" variant="secondary" className="flex-1" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" className="flex-1" isLoading={isGenerating}>
          {isGenerating ? 'Generating...' : 'Generate Skill'}
        </Button>
      </div>
    </form>
  );
}

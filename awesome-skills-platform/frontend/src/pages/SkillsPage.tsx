import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { skillsApi } from '../services/skills';
import { Button } from '../components/common/Button';

export function SkillsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch skills
  const { data: skills = [], isLoading } = useQuery({
    queryKey: ['skills'],
    queryFn: skillsApi.list,
  });

  // Delete skill mutation
  const deleteSkillMutation = useMutation({
    mutationFn: skillsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['skills'] });
    },
  });
  return (
    <div className="p-8 h-full flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Skill Management</h1>
        <p className="text-text-muted">Manage and organize your agent skills.</p>
      </div>

      {/* Toolbar */}
      <div className="mb-6 flex items-center justify-between gap-4">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">
              search
            </span>
            <input
              type="text"
              placeholder="Filter by name..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <div className="flex gap-3">
          <Button variant="secondary" onClick={() => navigate('/skills/upload')}>
            <span className="material-symbols-outlined">upload</span>
            Upload ZIP
          </Button>
          <Button onClick={() => navigate('/skills/create')}>
            <span className="material-symbols-outlined">auto_awesome</span>
            Create with Agent
          </Button>
        </div>
      </div>

      {/* Skills Table */}
      <div className="flex-1 bg-gray-900 rounded-lg border border-gray-800 overflow-hidden flex flex-col">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-text-muted">Loading skills...</div>
          </div>
        ) : skills.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="text-text-muted mb-4">No skills found</div>
            <Button onClick={() => navigate('/skills/create')}>
              <span className="material-symbols-outlined">auto_awesome</span>
              Create Your First Skill
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto flex-1">
            <table className="w-full">
              <thead className="border-b border-gray-800 bg-gray-900 sticky top-0">
                <tr className="text-left">
                  <th className="px-6 py-4 font-medium text-text-muted">Skill Name</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Description</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Actions</th>
                </tr>
              </thead>
              <tbody>
                {skills.map((skill) => (
                  <tr
                    key={skill.id}
                    className="border-b border-gray-800 hover:bg-gray-800 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">extension</span>
                        <span className="font-medium">{skill.name}</span>
                        {skill.isSystem && (
                          <span className="px-2 py-0.5 text-xs bg-blue-500/10 text-blue-400 rounded">
                            System
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-text-muted">{skill.description}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button className="p-1.5 hover:bg-gray-700 rounded transition-colors">
                          <span className="material-symbols-outlined text-lg text-gray-400 hover:text-white">
                            edit
                          </span>
                        </button>
                        <button
                          onClick={() => {
                            if (confirm(`Delete skill "${skill.name}"?`)) {
                              deleteSkillMutation.mutate(skill.id);
                            }
                          }}
                          disabled={deleteSkillMutation.isPending}
                          className="p-1.5 hover:bg-gray-700 rounded transition-colors disabled:opacity-50"
                        >
                          <span className="material-symbols-outlined text-lg text-gray-400 hover:text-red-400">
                            delete
                          </span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

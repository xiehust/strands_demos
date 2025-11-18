import { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';

interface UploadFile {
  id: string;
  name: string;
  status: 'uploading' | 'completed' | 'error';
  progress?: number;
}

export function UploadSkillPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<UploadFile[]>([
    {
      id: '1',
      name: 'my-awesome-skill.zip',
      status: 'uploading',
      progress: 75,
    },
    {
      id: '2',
      name: 'database-query-skill.zip',
      status: 'completed',
    },
  ]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      handleFiles(selectedFiles);
    }
  };

  const handleFiles = (selectedFiles: File[]) => {
    const zipFiles = selectedFiles.filter(file => file.name.endsWith('.zip'));

    const newFiles: UploadFile[] = zipFiles.map((file, index) => ({
      id: `${Date.now()}-${index}`,
      name: file.name,
      status: 'uploading',
      progress: 0,
    }));

    setFiles(prev => [...prev, ...newFiles]);

    // Simulate upload progress
    newFiles.forEach((file) => {
      simulateUpload(file.id);
    });
  };

  const simulateUpload = (fileId: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      if (progress >= 100) {
        clearInterval(interval);
        setFiles(prev =>
          prev.map(f =>
            f.id === fileId ? { ...f, status: 'completed' as const, progress: 100 } : f
          )
        );
      } else {
        setFiles(prev =>
          prev.map(f => (f.id === fileId ? { ...f, progress } : f))
        );
      }
    }, 200);
  };

  const handleRemoveFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = () => {
    // TODO: Phase 3 - API call to upload files
    console.log('Uploading files:', files);
    navigate('/skills');
  };

  const handleCancel = () => {
    navigate('/skills');
  };

  return (
    <div className="min-h-screen bg-bg-dark text-white p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/skills"
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
          >
            <span className="material-symbols-outlined text-xl">arrow_back</span>
            Back to Skill Management
          </Link>
          <h1 className="text-3xl font-semibold mb-2">Upload ZIP Skill Package</h1>
          <p className="text-gray-400">
            Upload a .zip file containing your skill definitions and code.
          </p>
        </div>

        {/* Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-lg p-16 transition-colors ${
            isDragging
              ? 'border-primary bg-primary/5'
              : 'border-gray-600 bg-gray-800/30'
          }`}
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center justify-center">
            {/* Upload Icon */}
            <div className="mb-6">
              <svg
                width="64"
                height="64"
                viewBox="0 0 64 64"
                fill="none"
                className="text-primary"
              >
                <rect x="12" y="8" width="40" height="48" rx="2" stroke="currentColor" strokeWidth="2" fill="none" />
                <path
                  d="M32 20 L32 40 M24 28 L32 20 L40 28"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="none"
                />
              </svg>
            </div>

            {/* Instructions */}
            <p className="text-lg text-white mb-2">
              Drag & Drop your ZIP file here
            </p>
            <p className="text-gray-400 mb-4">or</p>
            <Button
              type="button"
              variant="secondary"
              onClick={handleBrowseClick}
            >
              Browse Files
            </Button>

            {/* Hidden File Input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".zip"
              multiple
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="mt-8 space-y-4">
            {files.map(file => (
              <div
                key={file.id}
                className="bg-gray-800/50 border border-gray-700 rounded-lg p-4"
              >
                <div className="flex items-center gap-4">
                  {/* Icon */}
                  <div className="flex-shrink-0">
                    {file.status === 'uploading' && (
                      <span className="material-symbols-outlined text-primary text-3xl">
                        folder_zip
                      </span>
                    )}
                    {file.status === 'completed' && (
                      <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center">
                        <span className="material-symbols-outlined text-green-400 text-xl">
                          check_circle
                        </span>
                      </div>
                    )}
                  </div>

                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-white font-medium truncate">
                        {file.name}
                      </span>
                      {file.status === 'uploading' && (
                        <span className="text-sm text-gray-400 ml-2">
                          {file.progress}%
                        </span>
                      )}
                      {file.status === 'completed' && (
                        <span className="text-sm text-green-400 ml-2">
                          Upload complete
                        </span>
                      )}
                    </div>

                    {/* Progress Bar */}
                    {file.status === 'uploading' && (
                      <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary transition-all duration-300"
                          style={{ width: `${file.progress}%` }}
                        />
                      </div>
                    )}
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={() => handleRemoveFile(file.id)}
                    className="flex-shrink-0 text-gray-400 hover:text-red-400 transition-colors"
                  >
                    {file.status === 'uploading' ? (
                      <span className="material-symbols-outlined text-2xl">close</span>
                    ) : (
                      <span className="material-symbols-outlined text-2xl">delete</span>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end gap-4 mt-8">
          <Button type="button" variant="secondary" onClick={handleCancel}>
            Cancel
          </Button>
          <Button
            type="button"
            variant="primary"
            onClick={handleUpload}
            icon={<span className="material-symbols-outlined">upload</span>}
          >
            Upload
          </Button>
        </div>
      </div>
    </div>
  );
}

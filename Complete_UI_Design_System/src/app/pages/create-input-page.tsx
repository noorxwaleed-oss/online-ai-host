import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import { useGeneration } from '../providers/generation-provider';
import {
  Link2,
  FileText,
  ScanSearch,
  FileEdit,
  Users,
  Palette,
  Rocket,
  X,
  UploadCloud,
} from 'lucide-react';

type TabType = 'url' | 'pdf';

const MAX_PDF_SIZE = 10 * 1024 * 1024; // 10 MB

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function CreateInputPage() {
  const navigate = useNavigate();
  const { input: draft, setInput: setDraft } = useGeneration();

  const [activeTab, setActiveTab] = useState<TabType>(draft.input_type);
  const [input, setInput] = useState(draft.input_type === 'url' ? draft.content : '');
  const [pdfFile, setPdfFile] = useState<File | null>(draft.pdf_file);
  const [isDragging, setIsDragging] = useState(false);
  const [podcastTitle, setPodcastTitle] = useState(draft.podcast_name);
  const [language, setLanguage] = useState<'EN' | 'AR'>(draft.language);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setDraft({
      input_type: activeTab,
      content: activeTab === 'url' ? input.trim() : pdfFile?.name ?? '',
      pdf_file: activeTab === 'pdf' ? pdfFile : null,
      podcast_name: podcastTitle.trim(),
      language,
    });
  }, [activeTab, input, pdfFile, podcastTitle, language, setDraft]);

  const canProceed =
    podcastTitle.trim().length > 0 &&
    (activeTab === 'url' ? input.trim().length > 0 : pdfFile !== null);

  const handleNext = () => {
    if (!canProceed) {
      toast.warning('Please provide a podcast title and either a URL or PDF.');
      return;
    }
    navigate('/create/personas');
  };

  const agents = [
    {
      name: 'ContentAnalyzer',
      status: 'waiting' as const,
      message: 'Waiting for input',
      icon: ScanSearch,
    },
    {
      name: 'Scriptwriter',
      status: 'waiting' as const,
      message: 'Waiting to write script',
      icon: FileEdit,
    },
    {
      name: 'Persona',
      status: 'waiting' as const,
      message: 'Waiting to configure voices',
      icon: Users,
    },
    {
      name: 'Media',
      status: 'waiting' as const,
      message: 'Waiting to generate media',
      icon: Palette,
    },
    {
      name: 'Publisher',
      status: 'waiting' as const,
      message: 'Waiting to prepare publishing',
      icon: Rocket,
    },
  ];

  const validateAndSetFile = (file: File | undefined | null) => {
    if (!file) return;
    const isPdf =
      file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    if (!isPdf) {
      toast.error('Only PDF files are supported.');
      return;
    }
    if (file.size > MAX_PDF_SIZE) {
      toast.error('File is too large. Maximum size is 10 MB.');
      return;
    }
    setPdfFile(file);
    toast.success(`Uploaded ${file.name}`);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    validateAndSetFile(e.target.files?.[0]);
    // Reset so selecting the same file again still fires onChange
    e.target.value = '';
  };

  const handleDrop = (e: React.DragEvent<HTMLElement>) => {
    e.preventDefault();
    setIsDragging(false);
    validateAndSetFile(e.dataTransfer.files?.[0]);
  };

  const handleDragOver = (e: React.DragEvent<HTMLElement>) => {
    e.preventDefault();
    if (!isDragging) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleClearFile = () => {
    setPdfFile(null);
  };

  const tabs = [
    { id: 'url' as TabType, label: 'FROM URL', icon: Link2 },
    { id: 'pdf' as TabType, label: 'FROM PDF', icon: FileText },
  ];

  return (
    <CreateLayout
      currentStep={1}
      agents={agents}
      onNext={handleNext}
      nextLabel="Next"
    >
      <GlassCard className="p-8">
        {/* Tabs */}
        <div className="flex items-center gap-2 mb-6 border-b border-white/10">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-3 relative transition-colors ${
                  activeTab === tab.id ? 'text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
                {activeTab === tab.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#6366F1]" />
                )}
              </button>
            );
          })}
        </div>

        {/* Input Area */}
        <div className="mb-6">
          {activeTab === 'url' && (
            <div>
              <label className="block text-sm mb-2">Enter URL</label>
              <input
                type="url"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="https://example.com/article"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
              />
            </div>
          )}

          {activeTab === 'pdf' && (
            <div>
              <label className="block text-sm mb-2">Upload PDF</label>

              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf,.pdf"
                onChange={handleFileChange}
                className="sr-only"
                aria-label="Upload PDF file"
              />

              {pdfFile ? (
                <div className="flex items-center gap-4 p-4 bg-white/5 border border-[#10B981]/30 rounded-lg">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#10B981] to-[#06B6D4] rounded-lg flex items-center justify-center flex-shrink-0">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{pdfFile.name}</p>
                    <p className="text-sm text-gray-400">
                      {formatFileSize(pdfFile.size)} · PDF
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="px-3 py-1.5 text-sm bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors"
                  >
                    Replace
                  </button>
                  <button
                    type="button"
                    onClick={handleClearFile}
                    aria-label="Remove file"
                    className="p-2 hover:bg-[#EF4444]/20 rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4 text-[#EF4444]" />
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  className={`w-full border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
                    isDragging
                      ? 'border-[#6366F1] bg-[#6366F1]/10'
                      : 'border-white/10 hover:border-[#6366F1]/50'
                  }`}
                  aria-label="Click to upload or drag and drop a PDF"
                >
                  <UploadCloud
                    className={`w-12 h-12 mx-auto mb-2 transition-colors ${
                      isDragging ? 'text-[#6366F1]' : 'text-gray-400'
                    }`}
                  />
                  <p className="text-sm text-gray-300 mb-1">
                    {isDragging ? 'Drop your PDF here' : 'Click to upload or drag and drop'}
                  </p>
                  <p className="text-xs text-gray-500">PDF files up to 10MB</p>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Settings */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm mb-2" htmlFor="podcast-title">
              Podcast Title
            </label>
            <input
              id="podcast-title"
              type="text"
              value={podcastTitle}
              onChange={(e) => setPodcastTitle(e.target.value)}
              placeholder="e.g. The Future of AI"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[#6366F1] transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm mb-2">Language</label>
            <div className="flex gap-2">
              {(['EN', 'AR'] as const).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setLanguage(lang)}
                  className={`flex-1 py-2 rounded-lg border transition-colors ${
                    language === lang
                      ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                      : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
                  }`}
                >
                  {lang}
                </button>
              ))}
            </div>
          </div>
        </div>

        <p className="text-xs text-gray-500 mt-2">
          Content analysis runs on the next steps. Click <span className="text-white">Next</span> when ready.
        </p>
      </GlassCard>
    </CreateLayout>
  );
}

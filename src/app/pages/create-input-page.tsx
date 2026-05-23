import { useRef, useState } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import {
  Link2,
  FileText,
  CheckCircle2,
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
  const [activeTab, setActiveTab] = useState<TabType>('url');
  const [input, setInput] = useState('');
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [podcastTitle, setPodcastTitle] = useState('');
  const [language, setLanguage] = useState('EN');
  const [analyzed, setAnalyzed] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const agents = [
    {
      name: 'ContentAnalyzer',
      status: analyzed ? ('completed' as const) : ('active' as const),
      message: analyzed ? 'Content analyzed successfully' : 'Analyzing content...',
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

  const canAnalyze =
    activeTab === 'url' ? input.trim().length > 0 : pdfFile !== null;

  const handleAnalyze = () => {
    if (!canAnalyze) {
      toast.warning(
        activeTab === 'url' ? 'Please enter a URL first.' : 'Please upload a PDF first.',
      );
      return;
    }
    setAnalyzed(true);
  };

  const tabs = [
    { id: 'url' as TabType, label: 'FROM URL', icon: Link2 },
    { id: 'pdf' as TabType, label: 'FROM PDF', icon: FileText },
  ];

  return (
    <CreateLayout
      currentStep={1}
      agents={agents}
      onNext={() => navigate('/create/personas')}
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
              {['EN', 'AR'].map((lang) => (
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

        {/* Analyze Button */}
        {!analyzed && (
          <button
            onClick={handleAnalyze}
            disabled={!canAnalyze}
            className="w-full py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Analyze Content
          </button>
        )}

        {/* Analysis Results */}
        {analyzed && (
          <div className="mt-6 space-y-4">
            <div className="flex items-center gap-2 text-[#10B981]">
              <CheckCircle2 className="w-5 h-5" />
              <span className="font-semibold">Analysis Complete</span>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Topic</label>
              <p className="text-lg">{podcastTitle || 'love in moon'}</p>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Key Points</label>
              <ul className="space-y-2 list-disc list-inside text-gray-300">
                <li>Exploration of romantic concepts in space</li>
                <li>Scientific perspective on lunar environments</li>
                <li>Cultural significance of moon symbolism</li>
                <li>Future possibilities for lunar habitation</li>
              </ul>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Keywords</label>
              <div className="flex flex-wrap gap-2">
                {['moon', 'love', 'romance', 'space', 'science', 'culture'].map((keyword) => (
                  <span
                    key={keyword}
                    className="px-3 py-1 bg-[#6366F1]/20 border border-[#6366F1]/30 rounded-full text-sm text-[#6366F1]"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Tone</label>
              <p className="text-gray-300">Conversational yet informative</p>
            </div>
          </div>
        )}
      </GlassCard>
    </CreateLayout>
  );
}

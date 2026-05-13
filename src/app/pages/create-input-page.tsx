import { useState } from 'react';
import { useNavigate } from 'react-router';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import { Link2, FileText, Type, CheckCircle2, ScanSearch, FileEdit, Users, Palette, Rocket } from 'lucide-react';

type TabType = 'url' | 'pdf' | 'text';

export function CreateInputPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('url');
  const [input, setInput] = useState('');
  const [duration, setDuration] = useState('5m');
  const [language, setLanguage] = useState('EN');
  const [analyzed, setAnalyzed] = useState(false);

  const agents = [
    {
      name: 'ContentAnalyzer',
      status: analyzed ? 'completed' as const : 'active' as const,
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

  const handleAnalyze = () => {
    setAnalyzed(true);
  };

  const tabs = [
    { id: 'url' as TabType, label: 'FROM URL', icon: Link2 },
    { id: 'pdf' as TabType, label: 'FROM PDF', icon: FileText },
    { id: 'text' as TabType, label: 'FROM TEXT', icon: Type },
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
              <div className="border-2 border-dashed border-white/10 rounded-lg p-8 text-center hover:border-[#6366F1]/50 transition-colors cursor-pointer">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-400 mb-1">Click to upload or drag and drop</p>
                <p className="text-xs text-gray-500">PDF files up to 10MB</p>
              </div>
            </div>
          )}
          
          {activeTab === 'text' && (
            <div>
              <label className="block text-sm mb-2">Enter Text</label>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Paste your content here..."
                rows={8}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors resize-none"
              />
            </div>
          )}
        </div>

        {/* Settings */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm mb-2">Duration</label>
            <div className="flex gap-2">
              {['3m', '5m', '10m', '15m'].map((dur) => (
                <button
                  key={dur}
                  onClick={() => setDuration(dur)}
                  className={`flex-1 py-2 rounded-lg border transition-colors ${
                    duration === dur
                      ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                      : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
                  }`}
                >
                  {dur}
                </button>
              ))}
            </div>
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
            className="w-full py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity"
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
              <p className="text-lg">love in moon</p>
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
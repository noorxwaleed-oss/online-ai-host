import { useState } from 'react';
import { useNavigate } from 'react-router';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import { RotateCw, FileText, ScanSearch, FileEdit, Users, Palette, Rocket, Copy } from 'lucide-react';

interface ScriptLine {
  speaker: 'HOST' | 'GUEST';
  text: string;
}

export function PersonasPage() {
  const navigate = useNavigate();
  const [script, setScript] = useState<ScriptLine[]>([
    { speaker: 'HOST', text: 'Welcome to today\'s episode where we explore the fascinating topic of love in moon.' },
    { speaker: 'GUEST', text: 'Thanks for having me! This is such an intriguing subject that combines romance, science, and culture.' },
    { speaker: 'HOST', text: 'Let\'s start with the cultural significance. The moon has been a symbol of romance for centuries.' },
    { speaker: 'GUEST', text: 'Absolutely! From ancient poetry to modern songs, the moon represents mystery and longing.' },
    { speaker: 'HOST', text: 'Now, from a scientific perspective, what would love actually look like on the moon?' },
    { speaker: 'GUEST', text: 'Well, the lunar environment is quite harsh. It would require advanced habitats and life support.' },
    { speaker: 'HOST', text: 'That\'s fascinating. Are there any current plans for lunar habitation?' },
    { speaker: 'GUEST', text: 'Several space agencies are working on establishing permanent lunar bases within the next decade.' },
    { speaker: 'HOST', text: 'Imagine celebrating an anniversary on the moon! The view of Earth would be incredible.' },
    { speaker: 'GUEST', text: 'It would be the ultimate romantic gesture, though quite expensive!' },
    { speaker: 'HOST', text: 'Thank you for this enlightening conversation about love and the moon.' },
  ]);

  const agents = [
    {
      name: 'ContentAnalyzer',
      status: 'completed' as const,
      message: 'Content analyzed successfully',
      icon: ScanSearch,
    },
    {
      name: 'Scriptwriter',
      status: 'active' as const,
      message: 'Preparing to write script',
      icon: FileEdit,
    },
    {
      name: 'Persona',
      status: 'active' as const,
      message: 'Configuring voice personas',
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

  const handleRegenerateAll = () => {
    // Mock regeneration
    console.log('Regenerating entire script...');
  };

  const handleCopyScript = () => {
    // Copy script to clipboard using fallback method
    const scriptText = script.map(line => `${line.speaker}: ${line.text}`).join('\n');
    
    try {
      // Try modern Clipboard API first
      navigator.clipboard.writeText(scriptText).then(() => {
        console.log('Script copied to clipboard');
      }).catch(() => {
        // Fallback method
        copyTextFallback(scriptText);
      });
    } catch (error) {
      // Fallback method for browsers that don't support Clipboard API
      copyTextFallback(scriptText);
    }
  };

  const copyTextFallback = (text: string) => {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      console.log('Script copied to clipboard (fallback method)');
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
    document.body.removeChild(textarea);
  };

  return (
    <CreateLayout
      currentStep={2}
      agents={agents}
      onPrevious={() => navigate('/create/input')}
      onNext={() => navigate('/create/script')}
      previousLabel="Back"
      nextLabel="Next"
    >
      <div className="space-y-6">
        {/* Script Editor */}
        <GlassCard className="p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold">Script</h2>
            <div className="flex items-center gap-3">
              <button
                onClick={handleCopyScript}
                className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors"
              >
                <Copy className="w-4 h-4" />
                Copy
              </button>
              <button
                onClick={handleRegenerateAll}
                className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors"
              >
                <RotateCw className="w-4 h-4" />
                Regenerate
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {script.map((line, index) => (
              <div key={index} className={`flex gap-3 ${line.speaker === 'GUEST' ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar Circle */}
                <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-white/15 backdrop-blur-sm border border-white/20 shadow-lg">
                  <span className="text-xs font-medium text-white">
                    {line.speaker === 'HOST' ? 'Host' : 'Guest'}
                  </span>
                </div>

                {/* Chat Bubble */}
                <div className={`flex-1 max-w-[80%] group ${line.speaker === 'GUEST' ? 'flex justify-end' : ''}`}>
                  <div className={`relative px-4 py-3 rounded-2xl ${
                    line.speaker === 'HOST'
                      ? 'bg-white/10 rounded-tl-sm'
                      : 'bg-[#6366F1]/20 rounded-tr-sm'
                  }`}>
                    <p className="text-gray-200 leading-relaxed">{line.text}</p>
                    <div className={`flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity ${
                      line.speaker === 'GUEST' ? 'justify-end' : 'justify-start'
                    }`}>
                      <button
                        className="p-1 hover:bg-white/10 rounded"
                        title="Regenerate this line"
                      >
                        <RotateCw className="w-3 h-3 text-gray-400" />
                      </button>
                      <span className="text-xs text-gray-500">Click to edit</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Script Info */}
        <GlassCard className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-[#6366F1]" />
            <h3 className="text-lg font-semibold">Script Info</h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-400 mb-1">Lines</p>
              <p className="text-xl font-semibold">{script.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">Est. Duration</p>
              <p className="text-xl font-semibold">5 min</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">Language</p>
              <p className="text-xl font-semibold">EN</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">Word Count</p>
              <p className="text-xl font-semibold">
                {script.reduce((acc, line) => acc + line.text.split(' ').length, 0)}
              </p>
            </div>
          </div>
        </GlassCard>
      </div>
    </CreateLayout>
  );
}
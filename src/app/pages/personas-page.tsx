import { useRef, useState } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import {
  RotateCw,
  FileText,
  ScanSearch,
  FileEdit,
  Users,
  Palette,
  Rocket,
  Copy,
  Check,
  X,
  Pencil,
} from 'lucide-react';

interface ScriptLine {
  speaker: 'HOST' | 'GUEST';
  text: string;
}

const INITIAL_SCRIPT: ScriptLine[] = [
  { speaker: 'HOST', text: "Welcome to today's episode where we explore the fascinating topic of love in moon." },
  { speaker: 'GUEST', text: 'Thanks for having me! This is such an intriguing subject that combines romance, science, and culture.' },
  { speaker: 'HOST', text: "Let's start with the cultural significance. The moon has been a symbol of romance for centuries." },
  { speaker: 'GUEST', text: 'Absolutely! From ancient poetry to modern songs, the moon represents mystery and longing.' },
  { speaker: 'HOST', text: 'Now, from a scientific perspective, what would love actually look like on the moon?' },
  { speaker: 'GUEST', text: 'Well, the lunar environment is quite harsh. It would require advanced habitats and life support.' },
  { speaker: 'HOST', text: "That's fascinating. Are there any current plans for lunar habitation?" },
  { speaker: 'GUEST', text: 'Several space agencies are working on establishing permanent lunar bases within the next decade.' },
  { speaker: 'HOST', text: 'Imagine celebrating an anniversary on the moon! The view of Earth would be incredible.' },
  { speaker: 'GUEST', text: 'It would be the ultimate romantic gesture, though quite expensive!' },
  { speaker: 'HOST', text: 'Thank you for this enlightening conversation about love and the moon.' },
];

// Alternative phrasings used when "regenerating" a line — would come from your LLM call.
const REGEN_VARIATIONS: Record<'HOST' | 'GUEST', string[]> = {
  HOST: [
    'Let me rephrase that — what a great point to explore further.',
    'Building on that, I find the angle here genuinely fascinating.',
    'That raises an interesting question worth digging into.',
  ],
  GUEST: [
    'Right, and there are a few more dimensions to consider here.',
    'Exactly — and there are plenty of angles to unpack on this.',
    'That resonates with me, and I would add a bit more nuance.',
  ],
};

export function PersonasPage() {
  const navigate = useNavigate();
  const [script, setScript] = useState<ScriptLine[]>(INITIAL_SCRIPT);
  const [copied, setCopied] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [regenLineIdx, setRegenLineIdx] = useState<number | null>(null);
  const [editingIdx, setEditingIdx] = useState<number | null>(null);
  const [editingValue, setEditingValue] = useState('');
  const copyTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const agents = [
    {
      name: 'ContentAnalyzer',
      status: 'completed' as const,
      message: 'Content analyzed successfully',
      icon: ScanSearch,
    },
    {
      name: 'Scriptwriter',
      status: regenerating ? ('active' as const) : ('completed' as const),
      message: regenerating ? 'Regenerating script...' : 'Script generated successfully',
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

  const copyTextFallback = (text: string): boolean => {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    let ok = false;
    try {
      ok = document.execCommand('copy');
    } catch {
      ok = false;
    }
    document.body.removeChild(textarea);
    return ok;
  };

  const handleCopyScript = async () => {
    const scriptText = script.map((line) => `${line.speaker}: ${line.text}`).join('\n\n');

    const showCopied = () => {
      setCopied(true);
      toast.success('Script copied to clipboard');
      if (copyTimeoutRef.current) clearTimeout(copyTimeoutRef.current);
      copyTimeoutRef.current = setTimeout(() => setCopied(false), 2000);
    };

    try {
      await navigator.clipboard.writeText(scriptText);
      showCopied();
    } catch {
      if (copyTextFallback(scriptText)) {
        showCopied();
      } else {
        toast.error('Could not copy. Please copy manually.');
      }
    }
  };

  const handleRegenerateAll = async () => {
    if (regenerating) return;
    setRegenerating(true);
    try {
      // TODO: call your real script-generation endpoint here.
      await new Promise((r) => setTimeout(r, 1200));
      setScript((current) =>
        current.map((line) => {
          const variants = REGEN_VARIATIONS[line.speaker];
          const next = variants[Math.floor(Math.random() * variants.length)];
          return { ...line, text: next };
        }),
      );
      toast.success('Script regenerated');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not regenerate script';
      toast.error(message);
    } finally {
      setRegenerating(false);
    }
  };

  const handleRegenerateLine = async (idx: number) => {
    if (regenLineIdx !== null) return;
    setRegenLineIdx(idx);
    try {
      await new Promise((r) => setTimeout(r, 700));
      setScript((current) =>
        current.map((line, i) => {
          if (i !== idx) return line;
          const variants = REGEN_VARIATIONS[line.speaker].filter((v) => v !== line.text);
          const next = variants[Math.floor(Math.random() * variants.length)];
          return { ...line, text: next };
        }),
      );
      toast.success('Line regenerated');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not regenerate line';
      toast.error(message);
    } finally {
      setRegenLineIdx(null);
    }
  };

  const startEdit = (idx: number) => {
    setEditingIdx(idx);
    setEditingValue(script[idx].text);
  };

  const saveEdit = () => {
    if (editingIdx === null) return;
    const trimmed = editingValue.trim();
    if (!trimmed) {
      toast.warning('Line cannot be empty');
      return;
    }
    setScript((current) =>
      current.map((line, i) => (i === editingIdx ? { ...line, text: trimmed } : line)),
    );
    setEditingIdx(null);
    setEditingValue('');
    toast.success('Line updated');
  };

  const cancelEdit = () => {
    setEditingIdx(null);
    setEditingValue('');
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
                disabled={regenerating}
                className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4 text-[#10B981]" />
                    <span className="text-[#10B981]">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    Copy
                  </>
                )}
              </button>
              <button
                onClick={handleRegenerateAll}
                disabled={regenerating}
                className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RotateCw
                  className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`}
                />
                {regenerating ? 'Regenerating...' : 'Regenerate'}
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {script.map((line, index) => {
              const isRegenLine = regenLineIdx === index;
              const isEditing = editingIdx === index;
              return (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    line.speaker === 'GUEST' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  {/* Avatar */}
                  <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-white/15 backdrop-blur-sm border border-white/20 shadow-lg">
                    <span className="text-xs font-medium text-white">
                      {line.speaker === 'HOST' ? 'Host' : 'Guest'}
                    </span>
                  </div>

                  {/* Chat Bubble */}
                  <div
                    className={`flex-1 max-w-[80%] group ${
                      line.speaker === 'GUEST' ? 'flex justify-end' : ''
                    }`}
                  >
                    <div
                      className={`relative px-4 py-3 rounded-2xl w-full ${
                        line.speaker === 'HOST'
                          ? 'bg-white/10 rounded-tl-sm'
                          : 'bg-[#6366F1]/20 rounded-tr-sm'
                      } ${isRegenLine ? 'opacity-60 animate-pulse' : ''}`}
                    >
                      {isEditing ? (
                        <>
                          <textarea
                            value={editingValue}
                            onChange={(e) => setEditingValue(e.target.value)}
                            rows={Math.max(2, Math.ceil(editingValue.length / 70))}
                            autoFocus
                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-[#6366F1] resize-none"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                                e.preventDefault();
                                saveEdit();
                              }
                              if (e.key === 'Escape') {
                                e.preventDefault();
                                cancelEdit();
                              }
                            }}
                          />
                          <div className="flex items-center gap-2 mt-2 justify-end">
                            <button
                              onClick={cancelEdit}
                              className="flex items-center gap-1 px-2 py-1 text-xs bg-white/5 border border-white/10 rounded hover:bg-white/10"
                            >
                              <X className="w-3 h-3" />
                              Cancel
                            </button>
                            <button
                              onClick={saveEdit}
                              className="flex items-center gap-1 px-2 py-1 text-xs bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] rounded hover:opacity-90"
                            >
                              <Check className="w-3 h-3" />
                              Save
                            </button>
                          </div>
                        </>
                      ) : (
                        <>
                          <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">
                            {line.text}
                          </p>
                          <div
                            className={`flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity ${
                              line.speaker === 'GUEST' ? 'justify-end' : 'justify-start'
                            }`}
                          >
                            <button
                              onClick={() => startEdit(index)}
                              disabled={regenerating || isRegenLine}
                              className="flex items-center gap-1 px-2 py-1 hover:bg-white/10 rounded text-xs text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              title="Edit this line"
                            >
                              <Pencil className="w-3 h-3" />
                              Edit
                            </button>
                            <button
                              onClick={() => handleRegenerateLine(index)}
                              disabled={regenerating || isRegenLine}
                              className="flex items-center gap-1 px-2 py-1 hover:bg-white/10 rounded text-xs text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              title="Regenerate this line"
                            >
                              <RotateCw
                                className={`w-3 h-3 ${isRegenLine ? 'animate-spin' : ''}`}
                              />
                              {isRegenLine ? 'Regenerating' : 'Regenerate'}
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
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
                {script.reduce((acc, line) => acc + line.text.split(/\s+/).filter(Boolean).length, 0)}
              </p>
            </div>
          </div>
        </GlassCard>
      </div>
    </CreateLayout>
  );
}

import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import {
  ScanSearch,
  FileEdit,
  Users,
  Palette,
  Rocket,
  Loader2,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../providers/auth-provider';
import { useGeneration, type ScriptLine } from '../providers/generation-provider';
import { fetchJsonUrl, generatePodcast, getLatestProject, uploadPdf } from '@/lib/api';

type AgentStatus = 'waiting' | 'active' | 'completed' | 'error';

const PROGRESS_STEPS: { key: string; label: string }[] = [
  { key: 'analyzer', label: 'Analyzing content' },
  { key: 'script', label: 'Writing script' },
  { key: 'audio', label: 'Generating audio' },
  { key: 'cover', label: 'Designing cover art' },
  { key: 'publish', label: 'Publishing to RSS' },
];

// Backend runs steps sequentially inside one POST and gives no progress updates,
// so we estimate timing client-side to give visual feedback. These are conservative.
const ESTIMATED_STEP_MS = [12000, 25000, 90000, 30000, 8000];

function parseScript(content: string): ScriptLine[] {
  const lines: ScriptLine[] = [];
  let currentSpeaker: 'HOST' | 'GUEST' | null = null;
  let buffer = '';

  for (const raw of content.split('\n')) {
    const line = raw.trim();
    if (!line) continue;
    const hostMatch = line.match(/^(host|HOST|Host)\s*:\s*(.*)$/);
    const guestMatch = line.match(/^(guest|GUEST|Guest)\s*:\s*(.*)$/);
    if (hostMatch) {
      if (currentSpeaker && buffer) lines.push({ speaker: currentSpeaker, text: buffer.trim() });
      currentSpeaker = 'HOST';
      buffer = hostMatch[2];
    } else if (guestMatch) {
      if (currentSpeaker && buffer) lines.push({ speaker: currentSpeaker, text: buffer.trim() });
      currentSpeaker = 'GUEST';
      buffer = guestMatch[2];
    } else if (currentSpeaker) {
      buffer += ' ' + line;
    }
  }
  if (currentSpeaker && buffer) lines.push({ speaker: currentSpeaker, text: buffer.trim() });
  return lines;
}

export function ScriptPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    input,
    personas,
    isGenerating,
    setIsGenerating,
    result,
    setResult,
    project,
    setProject,
    scriptLines,
    setScriptLines,
  } = useGeneration();

  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const hasFiredRef = useRef(false);

  // Validate prerequisites
  useEffect(() => {
    const hasInput =
      input.input_type === 'pdf' ? input.pdf_file !== null : input.content.length > 0;
    if (!hasInput || !input.podcast_name) {
      toast.error('Missing input. Please start from the beginning.');
      navigate('/create/input');
    }
  }, [input.content, input.pdf_file, input.input_type, input.podcast_name, navigate]);

  // Fire the single POST on mount if not already done
  useEffect(() => {
    if (hasFiredRef.current) return;
    if (result && project && scriptLines) return; // already done in this session
    if (!user) return;
    if (!input.podcast_name) return;
    if (input.input_type === 'pdf' && !input.pdf_file) {
      setError('No PDF selected. Go back to the Input step and choose a file.');
      return;
    }
    if (input.input_type === 'url' && !input.content) return;

    hasFiredRef.current = true;
    // No AbortController and no `cancelled` flag: the generation POST runs for
    // several minutes and we want to capture its response even if React StrictMode's
    // dev unmount/remount cycle tears the script page down in between. Because
    // result/project/scriptLines live in App-level context, setting them after an
    // unmount still works — the context is alive even when this page is not.
    (async () => {
      setIsGenerating(true);
      setError(null);
      setCurrentStepIdx(0);

      // Client-side step animation. Advances on a timer while the single POST is in flight.
      const stepTimers: ReturnType<typeof setTimeout>[] = [];
      let elapsed = 0;
      for (let i = 0; i < ESTIMATED_STEP_MS.length - 1; i++) {
        elapsed += ESTIMATED_STEP_MS[i];
        stepTimers.push(
          setTimeout(() => setCurrentStepIdx((idx) => Math.max(idx, i + 1)), elapsed),
        );
      }

      try {
        // If the user picked a PDF, upload it first so the backend has a
        // server-local file path it can read with PyPDFLoader.
        let contentForApi = input.content;
        if (input.input_type === 'pdf' && input.pdf_file) {
          const upload = await uploadPdf(input.pdf_file);
          contentForApi = upload.content;
        }

        const apiResult = await generatePodcast({
          host_name: personas.host_name,
          host_gender: personas.host_gender,
          guest_name: personas.guest_name,
          guest_gender: personas.guest_gender,
          podcast_name: input.podcast_name,
          language: input.language === 'AR' ? 'arabic' : 'english',
          content: contentForApi,
          voice_id_host: personas.voice_id_host,
          voice_id_guest: personas.voice_id_guest,
          host_style: personas.host_style,
          guest_style: personas.guest_style,
          user_id: user.id,
        });

        stepTimers.forEach(clearTimeout);

        if (apiResult.error) {
          throw new Error(apiResult.error);
        }
        setResult(apiResult);
        setCurrentStepIdx(PROGRESS_STEPS.length);

        // Hydrate the rest from /latest
        const latest = await getLatestProject(user.id);
        setProject(latest);

        if (latest.script_url) {
          try {
            const scriptJson = await fetchJsonUrl<{ content: string }>(latest.script_url);
            setScriptLines(parseScript(scriptJson.content));
          } catch (err) {
            console.warn('Failed to fetch script JSON', err);
          }
        }

        toast.success('Podcast generated successfully');
      } catch (err) {
        stepTimers.forEach(clearTimeout);
        if ((err as Error).name === 'AbortError') return;
        const msg = err instanceof Error ? err.message : 'Generation failed';
        setError(msg);
        toast.error(msg);
      } finally {
        setIsGenerating(false);
      }
    })();

    // No cleanup: the in-flight POST should keep running and write its result
    // into context regardless of whether this page is still mounted.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // If we've come back to this page after a previous successful run (script
  // already in context), show all steps as completed regardless of the local
  // `currentStepIdx` (which resets on remount).
  const previouslyCompleted = !isGenerating && !error && scriptLines !== null;

  const agentStatus = (idx: number): AgentStatus => {
    if (previouslyCompleted) return 'completed';
    if (error && idx === currentStepIdx) return 'error';
    if (currentStepIdx > idx) return 'completed';
    if (currentStepIdx === idx && isGenerating) return 'active';
    if (!isGenerating && currentStepIdx >= PROGRESS_STEPS.length) return 'completed';
    return 'waiting';
  };

  // CreateLayout's Agent type only accepts the three normal statuses, so map
  // the local 'error' state to 'active' for the right-hand panel.
  const layoutStatus = (idx: number): 'completed' | 'active' | 'waiting' => {
    const s = agentStatus(idx);
    return s === 'error' ? 'active' : s;
  };

  const agents = [
    { name: 'ContentAnalyzer', status: layoutStatus(0), message: PROGRESS_STEPS[0].label, icon: ScanSearch },
    { name: 'Scriptwriter',    status: layoutStatus(1), message: PROGRESS_STEPS[1].label, icon: FileEdit },
    { name: 'Persona',         status: layoutStatus(2), message: PROGRESS_STEPS[2].label, icon: Users },
    { name: 'Media',           status: layoutStatus(3), message: PROGRESS_STEPS[3].label, icon: Palette },
    { name: 'Publisher',       status: layoutStatus(4), message: PROGRESS_STEPS[4].label, icon: Rocket },
  ];

  const allDone = !isGenerating && !error && scriptLines !== null;

  return (
    <CreateLayout
      currentStep={3}
      agents={agents}
      onPrevious={() => navigate('/create/personas')}
      onNext={() => navigate('/create/audio')}
      previousLabel="Back"
      nextLabel={allDone ? 'Next' : 'Generating…'}
    >
      <div className="space-y-6">
        {/* Progress card */}
        <GlassCard className="p-6">
          <h2 className="text-2xl font-semibold mb-4">
            {isGenerating ? 'Generating your podcast…' : error ? 'Generation failed' : 'Script'}
          </h2>

          {error ? (
            <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-red-300">{error}</p>
                <button
                  onClick={() => {
                    hasFiredRef.current = false;
                    setError(null);
                    setResult(null);
                    setProject(null);
                    setScriptLines(null);
                    setCurrentStepIdx(0);
                  }}
                  className="mt-3 px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-sm"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : (
            <ul className="space-y-3">
              {PROGRESS_STEPS.map((step, idx) => {
                const status = agentStatus(idx);
                return (
                  <li key={step.key} className="flex items-center gap-3">
                    {status === 'completed' ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    ) : status === 'active' ? (
                      <Loader2 className="w-5 h-5 text-[#6366F1] animate-spin" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border border-white/20" />
                    )}
                    <span
                      className={
                        status === 'completed'
                          ? 'text-gray-200'
                          : status === 'active'
                          ? 'text-white font-medium'
                          : 'text-gray-500'
                      }
                    >
                      {step.label}
                    </span>
                  </li>
                );
              })}
            </ul>
          )}
        </GlassCard>

        {/* Script display once available */}
        {scriptLines && scriptLines.length > 0 && (
          <GlassCard className="p-8">
            <h3 className="text-xl font-semibold mb-4">Script</h3>
            <div className="space-y-4">
              {scriptLines.map((line, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    line.speaker === 'GUEST' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-white/15 backdrop-blur-sm border border-white/20 shadow-lg">
                    <span className="text-xs font-medium text-white">
                      {line.speaker === 'HOST' ? 'Host' : 'Guest'}
                    </span>
                  </div>
                  <div
                    className={`flex-1 max-w-[80%] ${
                      line.speaker === 'GUEST' ? 'flex justify-end' : ''
                    }`}
                  >
                    <div
                      className={`relative px-4 py-3 rounded-2xl w-full ${
                        line.speaker === 'HOST'
                          ? 'bg-white/10 rounded-tl-sm'
                          : 'bg-[#6366F1]/20 rounded-tr-sm'
                      }`}
                    >
                      <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">
                        {line.text}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        )}
      </div>
    </CreateLayout>
  );
}

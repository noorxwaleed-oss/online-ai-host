import { useNavigate } from 'react-router';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import { ScanSearch, FileEdit, Users, Palette, Rocket, Loader2 } from 'lucide-react';
import { useGeneration } from '../providers/generation-provider';

function formatTime(seconds: number) {
  const safe = Math.max(0, Math.floor(seconds));
  const mins = Math.floor(safe / 60);
  const secs = safe % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function AudioPage() {
  const navigate = useNavigate();
  const { personas, result, project, isGenerating } = useGeneration();

  const audioUrl = result?.audio_url || project?.audio_url || null;
  const duration = result?.duration ?? 0;

  const baseStatus = audioUrl ? 'completed' : isGenerating ? 'active' : 'waiting';

  const agents = [
    { name: 'ContentAnalyzer', status: 'completed' as const, message: 'Content analyzed', icon: ScanSearch },
    { name: 'Scriptwriter',    status: 'completed' as const, message: 'Script generated',  icon: FileEdit },
    { name: 'Persona',         status: 'completed' as const, message: 'Personas configured', icon: Users },
    { name: 'Media',           status: baseStatus as 'waiting' | 'active' | 'completed',
      message: audioUrl ? 'Audio ready' : isGenerating ? 'Generating audio…' : 'Waiting',
      icon: Palette },
    { name: 'Publisher',       status: 'waiting' as const, message: 'Waiting to prepare publishing', icon: Rocket },
  ];

  const initials = (name: string) =>
    (name || '?').split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase();

  return (
    <CreateLayout
      currentStep={4}
      agents={agents}
      onPrevious={() => navigate('/create/script')}
      onNext={() => navigate('/create/cover')}
      previousLabel="Back"
      nextLabel="Next"
    >
      <div className="space-y-6">
        <GlassCard className="p-8">
          <h2 className="text-2xl font-semibold mb-6">Audio</h2>

          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <GlassCard className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-full flex items-center justify-center">
                  <span className="font-semibold">{initials(personas.host_name)}</span>
                </div>
                <div>
                  <p className="font-medium">{personas.host_name || 'Host'}</p>
                  <p className="text-sm text-gray-400">{personas.host_style} voice</p>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-[#8B5CF6] to-[#EC4899] rounded-full flex items-center justify-center">
                  <span className="font-semibold">{initials(personas.guest_name)}</span>
                </div>
                <div>
                  <p className="font-medium">{personas.guest_name || 'Guest'}</p>
                  <p className="text-sm text-gray-400">{personas.guest_style} voice</p>
                </div>
              </div>
            </GlassCard>
          </div>

          {audioUrl ? (
            <>
              <audio controls src={audioUrl} className="w-full" preload="metadata">
                Your browser does not support the audio element.
              </audio>
              {duration > 0 && (
                <p className="text-sm text-gray-400 mt-3">
                  Duration: <span className="font-mono">{formatTime(duration)}</span>
                </p>
              )}
              <a
                href={audioUrl}
                download
                className="mt-4 inline-block px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-sm"
              >
                Download audio
              </a>
            </>
          ) : (
            <div className="flex items-center justify-center gap-3 py-12 text-gray-400">
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating audio…</span>
                </>
              ) : (
                <span>No audio yet. Go back to the Script step to start generation.</span>
              )}
            </div>
          )}
        </GlassCard>
      </div>
    </CreateLayout>
  );
}

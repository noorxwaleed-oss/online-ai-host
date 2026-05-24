import { useNavigate } from 'react-router';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import { Palette, ScanSearch, FileEdit, Users, Rocket, Loader2, Download } from 'lucide-react';
import { useGeneration } from '../providers/generation-provider';

export function CoverArtPage() {
  const navigate = useNavigate();
  const { input, project, isGenerating } = useGeneration();

  const coverUrl = project?.cover_url || null;

  const agents = [
    { name: 'ContentAnalyzer', status: 'completed' as const, message: 'Content analyzed', icon: ScanSearch },
    { name: 'Scriptwriter',    status: 'completed' as const, message: 'Script generated',  icon: FileEdit },
    { name: 'Persona',         status: 'completed' as const, message: 'Personas configured', icon: Users },
    { name: 'Media',
      status: (coverUrl ? 'completed' : isGenerating ? 'active' : 'waiting') as
        | 'completed' | 'active' | 'waiting',
      message: coverUrl ? 'Cover art ready' : isGenerating ? 'Generating cover…' : 'Waiting',
      icon: Palette },
    { name: 'Publisher',       status: 'waiting' as const, message: 'Waiting to prepare publishing', icon: Rocket },
  ];

  return (
    <CreateLayout
      currentStep={5}
      agents={agents}
      onPrevious={() => navigate('/create/audio')}
      onNext={() => navigate('/create/publish')}
      previousLabel="Back"
      nextLabel="Next"
    >
      <div className="space-y-6">
        <GlassCard className="p-8">
          <h2 className="text-2xl font-semibold mb-6">Cover Art</h2>

          <div className="grid md:grid-cols-[1fr_1.5fr] gap-8 items-start">
            <div>
              <div className="aspect-[2/3] w-full rounded-2xl overflow-hidden bg-white/5 border border-white/10 flex items-center justify-center">
                {coverUrl ? (
                  <img src={coverUrl} alt="Generated cover" className="w-full h-full object-cover" />
                ) : isGenerating ? (
                  <div className="flex flex-col items-center gap-2 text-gray-400">
                    <Loader2 className="w-8 h-8 animate-spin" />
                    <span className="text-sm">Generating…</span>
                  </div>
                ) : (
                  <span className="text-sm text-gray-500 px-4 text-center">
                    No cover yet. Go back to the Script step to start generation.
                  </span>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-400 mb-1">Title</p>
                <p className="text-lg font-medium">{input.podcast_name || '—'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-1">Language</p>
                <p className="text-lg font-medium">{input.language}</p>
              </div>

              {coverUrl && (
                <a
                  href={coverUrl}
                  download
                  className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-sm"
                >
                  <Download className="w-4 h-4" />
                  Download cover
                </a>
              )}
            </div>
          </div>
        </GlassCard>
      </div>
    </CreateLayout>
  );
}

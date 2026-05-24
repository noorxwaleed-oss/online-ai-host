import { useState } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import {
  Download,
  FileAudio,
  FileImage,
  FileText,
  CheckCircle2,
  Link2,
  Copy,
  Loader2,
  ScanSearch,
  FileEdit,
  Users,
  Palette,
  Rocket,
  type LucideIcon,
} from 'lucide-react';
import { useGeneration } from '../providers/generation-provider';

interface DownloadOption {
  key: 'audio' | 'cover' | 'script';
  icon: LucideIcon;
  label: string;
  url: string | null;
  filename: string;
}

function triggerBrowserDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function downloadFromUrl(url: string, filename: string) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const blob = await res.blob();
  triggerBrowserDownload(blob, filename);
}

export function PublishPage() {
  const navigate = useNavigate();
  const { input, result, project, reset } = useGeneration();

  const [downloadingKey, setDownloadingKey] = useState<DownloadOption['key'] | null>(null);

  const audioUrl = result?.audio_url || project?.audio_url || null;
  const coverUrl = project?.cover_url || null;
  const scriptUrl = project?.script_url || null;
  const rssUrl = project?.feed_url || null;
  const podcastTitle = input.podcast_name || 'podcast';
  const slug = podcastTitle.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');

  const downloads: DownloadOption[] = [
    { key: 'audio',  icon: FileAudio,  label: 'Audio',  url: audioUrl,  filename: `${slug}.mp3` },
    { key: 'cover',  icon: FileImage,  label: 'Cover',  url: coverUrl,  filename: `${slug}-cover.png` },
    { key: 'script', icon: FileText,   label: 'Script', url: scriptUrl, filename: `${slug}-script.json` },
  ];

  const agents = [
    { name: 'ContentAnalyzer', status: 'completed' as const, message: 'Content analyzed', icon: ScanSearch },
    { name: 'Scriptwriter',    status: 'completed' as const, message: 'Script generated',  icon: FileEdit },
    { name: 'Persona',         status: 'completed' as const, message: 'Personas configured', icon: Users },
    { name: 'Media',           status: 'completed' as const, message: 'Media generated', icon: Palette },
    { name: 'Publisher',
      status: (rssUrl ? 'completed' : 'active') as 'completed' | 'active',
      message: rssUrl ? 'Published' : 'Ready to publish',
      icon: Rocket },
  ];

  const handleCopyRss = async () => {
    if (!rssUrl) return;
    try {
      await navigator.clipboard.writeText(rssUrl);
      toast.success('RSS link copied to clipboard');
    } catch {
      toast.error('Could not copy link. Please copy it manually.');
    }
  };

  const handleDownloadOne = async (opt: DownloadOption) => {
    if (downloadingKey || !opt.url) return;
    setDownloadingKey(opt.key);
    try {
      await downloadFromUrl(opt.url, opt.filename);
      toast.success(`${opt.label} downloaded`);
    } catch (err) {
      const message = err instanceof Error ? err.message : `Could not download ${opt.label}`;
      toast.error(message);
    } finally {
      setDownloadingKey(null);
    }
  };

  return (
    <CreateLayout
      currentStep={6}
      agents={agents}
      onPrevious={() => navigate('/create/cover')}
      previousLabel="Back"
    >
      <div className="space-y-6">
        <GlassCard className="p-6 bg-[#10B981]/10 border-[#10B981]/20">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-6 h-6 text-[#10B981] flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-[#10B981] mb-1">Podcast Ready!</h3>
              <p className="text-sm text-gray-300">
                Your podcast &quot;{podcastTitle}&quot; has been generated. Download the assets or
                copy the RSS link to publish on any podcast platform.
              </p>
            </div>
          </div>
        </GlassCard>

        <div className="grid lg:grid-cols-2 gap-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-6">
              <Download className="w-5 h-5 text-[#6366F1]" />
              <h3 className="text-lg font-semibold">Download Options</h3>
            </div>

            <div className="space-y-3">
              {downloads.map((opt) => {
                const Icon = opt.icon;
                const isLoading = downloadingKey === opt.key;
                const disabled = !opt.url || (downloadingKey !== null && !isLoading);
                return (
                  <button
                    key={opt.key}
                    onClick={() => handleDownloadOne(opt)}
                    disabled={disabled}
                    className="w-full flex items-center gap-4 p-4 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 hover:border-[#6366F1]/30 transition-colors group disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white/5 disabled:hover:border-white/10"
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-lg flex items-center justify-center">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="font-medium">{opt.label}</p>
                      <p className="text-sm text-gray-400">
                        {opt.url ? opt.filename : 'Not available yet'}
                      </p>
                    </div>
                    {isLoading ? (
                      <Loader2 className="w-5 h-5 text-[#6366F1] animate-spin" />
                    ) : (
                      <Download className="w-5 h-5 text-gray-400 group-hover:text-[#6366F1] transition-colors" />
                    )}
                  </button>
                );
              })}
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-6">
              <Link2 className="w-5 h-5 text-[#6366F1]" />
              <h3 className="text-lg font-semibold">Share & Publish</h3>
            </div>

            <p className="text-sm text-gray-400 mb-4">
              Copy the RSS feed link below and submit it to Spotify, Apple Podcasts, or any podcast
              directory to publish your episode.
            </p>

            <label className="block text-sm mb-2" htmlFor="rss-url">
              RSS Feed URL
            </label>
            <div className="flex items-stretch gap-2">
              <input
                id="rss-url"
                type="text"
                value={rssUrl ?? 'No feed URL yet'}
                readOnly
                onFocus={(e) => e.currentTarget.select()}
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm font-mono text-gray-200 focus:outline-none focus:border-[#6366F1] transition-colors disabled:opacity-50"
                disabled={!rssUrl}
              />
              <button
                onClick={handleCopyRss}
                disabled={!rssUrl}
                className="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Copy RSS link"
              >
                <Copy className="w-4 h-4" />
                <span className="text-sm">Copy</span>
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-3">
              Hosted on Cloudinary. The link stays the same for every new episode of this podcast.
            </p>
          </GlassCard>
        </div>

        <GlassCard className="p-6">
          <h3 className="text-lg font-semibold mb-4">What&apos;s Next?</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <button
              onClick={() => {
                reset();
                navigate('/create/input');
              }}
              className="p-4 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-left"
            >
              <p className="font-medium mb-1">Create Another</p>
              <p className="text-sm text-gray-400">Start a new podcast episode</p>
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="p-4 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-left"
            >
              <p className="font-medium mb-1">View Dashboard</p>
              <p className="text-sm text-gray-400">See all your creations</p>
            </button>
            <button
              onClick={() => navigate('/personas')}
              className="p-4 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-left"
            >
              <p className="font-medium mb-1">Manage Personas</p>
              <p className="text-sm text-gray-400">Edit voice settings</p>
            </button>
          </div>
        </GlassCard>
      </div>
    </CreateLayout>
  );
}

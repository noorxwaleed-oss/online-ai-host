import { useEffect, useState } from 'react';
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

type DownloadKey = 'audio' | 'cover' | 'script';

interface DownloadOption {
  key: DownloadKey;
  icon: LucideIcon;
  label: string;
  format: string;
  size: string;
  filename: string;
  mime: string;
  /**
   * Real URL to fetch the asset from when the backend is wired up.
   * Leave undefined to fall back to a generated placeholder blob.
   */
  url?: string;
}

const PODCAST_TITLE = 'love in moon';
const DRAFTS_STORAGE_KEY = 'podcraft.drafts';

const DOWNLOAD_OPTIONS: DownloadOption[] = [
  {
    key: 'audio',
    icon: FileAudio,
    label: 'Audio',
    format: 'MP3',
    size: '12.4 MB',
    filename: 'love-in-moon.mp3',
    mime: 'audio/mpeg',
  },
  {
    key: 'cover',
    icon: FileImage,
    label: 'Cover',
    format: 'PNG',
    size: '2.1 MB',
    filename: 'love-in-moon-cover.png',
    mime: 'image/png',
  },
  {
    key: 'script',
    icon: FileText,
    label: 'Script',
    format: 'PDF',
    size: '156 KB',
    filename: 'love-in-moon-script.pdf',
    mime: 'application/pdf',
  },
];

function triggerBrowserDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  // Defer revoke so the browser has time to start the download
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function downloadAsset(option: DownloadOption) {
  if (option.url) {
    // Real backend path — fetch then trigger a download with the proper filename
    const res = await fetch(option.url);
    if (!res.ok) throw new Error(`Could not fetch ${option.label} (HTTP ${res.status})`);
    const blob = await res.blob();
    triggerBrowserDownload(blob, option.filename);
    return;
  }
  // Dev placeholder — generate a tiny file so the user sees the flow works
  const placeholderContent = `PodCraft AI · ${PODCAST_TITLE}\n\nPlaceholder ${option.format} file for "${option.label}".\nWhen the backend is wired, this will be replaced with the real asset from Cloudinary.\n`;
  const blob = new Blob([placeholderContent], { type: option.mime });
  triggerBrowserDownload(blob, option.filename);
}

export function PublishPage() {
  const navigate = useNavigate();
  const [rssUrl, setRssUrl] = useState<string>('');
  const [loadingRss, setLoadingRss] = useState(true);
  const [downloadingKey, setDownloadingKey] = useState<DownloadKey | null>(null);
  const [downloadingAll, setDownloadingAll] = useState(false);
  const [savingDraft, setSavingDraft] = useState(false);

  const agents = [
    {
      name: 'ContentAnalyzer',
      status: 'completed' as const,
      message: 'Content analyzed successfully',
      icon: ScanSearch,
    },
    {
      name: 'Scriptwriter',
      status: 'completed' as const,
      message: 'Script generated successfully',
      icon: FileEdit,
    },
    {
      name: 'Persona',
      status: 'completed' as const,
      message: 'Personas configured',
      icon: Users,
    },
    {
      name: 'Media',
      status: 'completed' as const,
      message: 'Media generated successfully',
      icon: Palette,
    },
    {
      name: 'Publisher',
      status: 'active' as const,
      message: 'Ready to publish',
      icon: Rocket,
    },
  ];

  useEffect(() => {
    let cancelled = false;

    async function fetchRssUrl() {
      try {
        setLoadingRss(true);
        // TODO: replace with real Cloudinary lookup, e.g.:
        //   const res = await fetch(`/api/episodes/${episodeId}/rss`);
        //   const { url } = await res.json();
        //   setRssUrl(url);
        await new Promise((r) => setTimeout(r, 600));
        const mockUrl =
          'https://res.cloudinary.com/podcraft-ai/raw/upload/v1/feeds/love-in-moon.xml';
        if (!cancelled) setRssUrl(mockUrl);
      } catch (err) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Failed to load RSS feed.';
          toast.error(message);
        }
      } finally {
        if (!cancelled) setLoadingRss(false);
      }
    }

    fetchRssUrl();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleCopyRss = async () => {
    if (!rssUrl) return;
    try {
      await navigator.clipboard.writeText(rssUrl);
      toast.success('RSS link copied to clipboard');
    } catch {
      const textarea = document.createElement('textarea');
      textarea.value = rssUrl;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        toast.success('RSS link copied to clipboard');
      } catch {
        toast.error('Could not copy link. Please copy it manually.');
      } finally {
        document.body.removeChild(textarea);
      }
    }
  };

  const handleDownloadOne = async (option: DownloadOption) => {
    if (downloadingKey || downloadingAll) return;
    setDownloadingKey(option.key);
    try {
      await downloadAsset(option);
      toast.success(`${option.label} downloaded`);
    } catch (err) {
      const message = err instanceof Error ? err.message : `Could not download ${option.label}`;
      toast.error(message);
    } finally {
      setDownloadingKey(null);
    }
  };

  const handleDownloadAll = async () => {
    if (downloadingAll) return;
    setDownloadingAll(true);
    try {
      for (const opt of DOWNLOAD_OPTIONS) {
        // Sequential to avoid browser blocking multiple simultaneous downloads
        await downloadAsset(opt);
        // Tiny pause so browsers don't bunch them together
        await new Promise((r) => setTimeout(r, 250));
      }
      toast.success('All files downloaded');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not download all files';
      toast.error(message);
    } finally {
      setDownloadingAll(false);
    }
  };

  const handleSaveDraft = async () => {
    if (savingDraft) return;
    setSavingDraft(true);
    try {
      // TODO: persist to Supabase `podcasts` table with status='draft'.
      const draft = {
        id: crypto.randomUUID(),
        title: PODCAST_TITLE,
        status: 'Draft',
        rssUrl,
        savedAt: new Date().toISOString(),
      };
      try {
        const existing = JSON.parse(localStorage.getItem(DRAFTS_STORAGE_KEY) ?? '[]') as unknown[];
        localStorage.setItem(DRAFTS_STORAGE_KEY, JSON.stringify([draft, ...existing]));
      } catch {
        localStorage.setItem(DRAFTS_STORAGE_KEY, JSON.stringify([draft]));
      }
      await new Promise((r) => setTimeout(r, 400));
      toast.success('Saved as draft. You can find it in My Library.');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not save draft';
      toast.error(message);
    } finally {
      setSavingDraft(false);
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
        {/* Success Message */}
        <GlassCard className="p-6 bg-[#10B981]/10 border-[#10B981]/20">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-6 h-6 text-[#10B981] flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-[#10B981] mb-1">Podcast Ready!</h3>
              <p className="text-sm text-gray-300">
                Your podcast &quot;{PODCAST_TITLE}&quot; has been generated successfully. Download
                your files or copy the RSS link to publish on any podcast platform.
              </p>
            </div>
          </div>
        </GlassCard>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Download Options */}
          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-6">
              <Download className="w-5 h-5 text-[#6366F1]" />
              <h3 className="text-lg font-semibold">Download Options</h3>
            </div>

            <div className="space-y-3">
              {DOWNLOAD_OPTIONS.map((option) => {
                const Icon = option.icon;
                const isLoading = downloadingKey === option.key;
                const disabled = downloadingAll || (downloadingKey !== null && !isLoading);
                return (
                  <button
                    key={option.key}
                    onClick={() => handleDownloadOne(option)}
                    disabled={disabled || isLoading}
                    className="w-full flex items-center gap-4 p-4 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 hover:border-[#6366F1]/30 transition-colors group disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white/5 disabled:hover:border-white/10"
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-lg flex items-center justify-center">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="font-medium">{option.label}</p>
                      <p className="text-sm text-gray-400">
                        {option.format} • {option.size}
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

            <button
              onClick={handleDownloadAll}
              disabled={downloadingAll || downloadingKey !== null}
              className="w-full mt-4 py-3 flex items-center justify-center gap-2 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {downloadingAll ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Downloading...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  Download All Files
                </>
              )}
            </button>
          </GlassCard>

          {/* Share & Publish — RSS link */}
          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-6">
              <Link2 className="w-5 h-5 text-[#6366F1]" />
              <h3 className="text-lg font-semibold">Share & Publish</h3>
            </div>

            <p className="text-sm text-gray-400 mb-4">
              Copy the RSS feed link below and submit it to Spotify, Apple Podcasts, Google
              Podcasts, or any other podcast directory to publish your episode.
            </p>

            <label className="block text-sm mb-2" htmlFor="rss-url">
              RSS Feed URL
            </label>
            <div className="flex items-stretch gap-2">
              <input
                id="rss-url"
                type="text"
                value={loadingRss ? 'Loading RSS link...' : rssUrl}
                readOnly
                onFocus={(e) => e.currentTarget.select()}
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm font-mono text-gray-200 focus:outline-none focus:border-[#6366F1] transition-colors disabled:opacity-50"
                disabled={loadingRss || !rssUrl}
              />
              <button
                onClick={handleCopyRss}
                disabled={loadingRss || !rssUrl}
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

            {/* Save as Draft */}
            <div className="mt-6 pt-4 border-t border-white/10">
              <button
                onClick={handleSaveDraft}
                disabled={savingDraft}
                className="w-full py-3 flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {savingDraft ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save as Draft'
                )}
              </button>
            </div>
          </GlassCard>
        </div>

        {/* Next Steps */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-semibold mb-4">What&apos;s Next?</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <button
              onClick={() => navigate('/create/input')}
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

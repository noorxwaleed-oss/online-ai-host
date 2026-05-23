import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import {
  RotateCw,
  Upload,
  Palette,
  ScanSearch,
  FileEdit,
  Users,
  Rocket,
  Loader2,
  X,
} from 'lucide-react';

interface Gradient {
  from: string;
  to: string;
  decoration: string; // accent blur color
}

const GRADIENTS: Gradient[] = [
  { from: '#6366F1', to: '#8B5CF6', decoration: '#8B5CF6' },
  { from: '#8B5CF6', to: '#EC4899', decoration: '#EC4899' },
  { from: '#10B981', to: '#06B6D4', decoration: '#06B6D4' },
  { from: '#F59E0B', to: '#EF4444', decoration: '#EF4444' },
  { from: '#0EA5E9', to: '#6366F1', decoration: '#6366F1' },
  { from: '#EC4899', to: '#F59E0B', decoration: '#F59E0B' },
];

const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5 MB

export function CoverArtPage() {
  const navigate = useNavigate();
  const [gradientIdx, setGradientIdx] = useState(0);
  const [regenerating, setRegenerating] = useState(false);
  const [customImage, setCustomImage] = useState<string | null>(null);
  const [customFileName, setCustomFileName] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Revoke object URL when component unmounts or image is replaced
  useEffect(() => {
    return () => {
      if (customImage) URL.revokeObjectURL(customImage);
    };
  }, [customImage]);

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
      status: regenerating ? ('active' as const) : ('completed' as const),
      message: regenerating ? 'Regenerating cover art...' : 'Cover art ready',
      icon: Palette,
    },
    {
      name: 'Publisher',
      status: 'waiting' as const,
      message: 'Waiting to prepare publishing',
      icon: Rocket,
    },
  ];

  const handleRegenerate = async () => {
    if (regenerating) return;
    setRegenerating(true);
    try {
      // TODO: replace with real image-generation call.
      await new Promise((r) => setTimeout(r, 1000));
      setGradientIdx((idx) => {
        let next = idx;
        // Pick a different gradient than the current one
        while (next === idx && GRADIENTS.length > 1) {
          next = Math.floor(Math.random() * GRADIENTS.length);
        }
        return next;
      });
      // Drop custom image if one was set — they likely want the AI cover back
      if (customImage) {
        URL.revokeObjectURL(customImage);
        setCustomImage(null);
        setCustomFileName('');
      }
      toast.success('New cover generated');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not regenerate cover';
      toast.error(message);
    } finally {
      setRegenerating(false);
    }
  };

  const handleUploadClick = () => {
    if (regenerating) return;
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error('Only image files are supported.');
      return;
    }
    if (file.size > MAX_IMAGE_SIZE) {
      toast.error('Image is too large. Maximum size is 5 MB.');
      return;
    }

    // Replace any previous URL
    if (customImage) URL.revokeObjectURL(customImage);

    const url = URL.createObjectURL(file);
    setCustomImage(url);
    setCustomFileName(file.name);
    toast.success(`Uploaded ${file.name}`);
  };

  const handleRemoveCustom = () => {
    if (customImage) URL.revokeObjectURL(customImage);
    setCustomImage(null);
    setCustomFileName('');
    toast.info('Reverted to generated cover');
  };

  const gradient = GRADIENTS[gradientIdx];

  return (
    <CreateLayout
      currentStep={5}
      agents={agents}
      onPrevious={() => navigate('/create/audio')}
      onNext={() => navigate('/create/publish')}
      previousLabel="Back"
      nextLabel="Next"
    >
      <GlassCard className="p-8">
        <h2 className="text-2xl font-semibold mb-6">Cover Art</h2>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="sr-only"
          aria-label="Upload custom cover image"
        />

        {/* Cover Preview */}
        <div className="mb-6">
          <div
            className={`mx-auto rounded-lg overflow-hidden relative aspect-square max-w-md transition-opacity ${
              regenerating ? 'opacity-60' : 'opacity-100'
            }`}
            style={
              customImage
                ? undefined
                : {
                    backgroundImage: `linear-gradient(to bottom right, ${gradient.from}, ${gradient.to})`,
                  }
            }
          >
            {customImage ? (
              <>
                <img
                  src={customImage}
                  alt="Custom cover"
                  className="w-full h-full object-cover"
                />
                <button
                  onClick={handleRemoveCustom}
                  aria-label="Remove custom cover"
                  className="absolute top-3 right-3 w-8 h-8 bg-black/60 backdrop-blur-sm hover:bg-black/80 rounded-full flex items-center justify-center transition-colors"
                >
                  <X className="w-4 h-4 text-white" />
                </button>
              </>
            ) : (
              <>
                <div className="absolute inset-0 flex items-center justify-center p-8">
                  <div className="text-center">
                    <div className="w-20 h-20 mx-auto mb-6 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                      <Palette className="w-10 h-10 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2">love in moon</h1>
                    <p className="text-white/80 text-sm">A PodCraft AI Production</p>
                  </div>
                </div>

                <div className="absolute top-10 right-10 w-32 h-32 bg-white/10 rounded-full blur-3xl" />
                <div
                  className="absolute bottom-10 left-10 w-40 h-40 rounded-full blur-3xl opacity-40"
                  style={{ background: gradient.decoration }}
                />
              </>
            )}

            {regenerating && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/30 backdrop-blur-sm">
                <Loader2 className="w-10 h-10 text-white animate-spin" />
              </div>
            )}
          </div>

          {customImage && (
            <p className="text-center text-xs text-gray-400 mt-3 truncate max-w-md mx-auto">
              Using uploaded file: <span className="text-gray-200">{customFileName}</span>
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="grid md:grid-cols-2 gap-3">
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="flex items-center justify-center gap-2 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {regenerating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Regenerating...
              </>
            ) : (
              <>
                <RotateCw className="w-4 h-4" />
                Regenerate
              </>
            )}
          </button>
          <button
            onClick={handleUploadClick}
            disabled={regenerating}
            className="flex items-center justify-center gap-2 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Upload className="w-4 h-4" />
            Upload Custom
          </button>
        </div>
      </GlassCard>
    </CreateLayout>
  );
}

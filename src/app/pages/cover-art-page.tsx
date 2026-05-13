import { useState } from 'react';
import { useNavigate } from 'react-router';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import { RotateCw, Upload, Palette, ScanSearch, FileEdit, Users, Rocket } from 'lucide-react';

export function CoverArtPage() {
  const navigate = useNavigate();
  const [coverStyle, setCoverStyle] = useState('minimalist');
  const [aspectRatio, setAspectRatio] = useState('9:16');

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
      status: 'active' as const,
      message: 'Generating cover art...',
      icon: Palette,
    },
    {
      name: 'Publisher',
      status: 'waiting' as const,
      message: 'Waiting to prepare publishing',
      icon: Rocket,
    },
  ];

  const styles = ['minimalist', 'professional', 'artistic', 'colorful'];
  const ratios = [
    { value: '9:16', label: '9:16', platform: 'Reels' },
    { value: '16:9', label: '16:9', platform: 'YouTube' },
    { value: '1:1', label: '1:1', platform: 'Instagram' },
    { value: '4:5', label: '4:5', platform: 'Facebook' },
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
      <GlassCard className="p-8">
        <h2 className="text-2xl font-semibold mb-6">Cover Art</h2>

        {/* Cover Preview */}
        <div className="mb-6">
          <div
            className={`mx-auto bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-lg overflow-hidden relative ${
              aspectRatio === '9:16'
                ? 'aspect-[9/16] max-w-sm'
                : aspectRatio === '16:9'
                ? 'aspect-video max-w-2xl'
                : aspectRatio === '1:1'
                ? 'aspect-square max-w-md'
                : 'aspect-[4/5] max-w-md'
            }`}
          >
            {/* Generated Cover Design */}
            <div className="absolute inset-0 flex items-center justify-center p-8">
              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-6 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                  <Palette className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-white mb-2">love in moon</h1>
                <p className="text-white/80 text-sm">A PodCraft AI Production</p>
              </div>
            </div>

            {/* Decorative Elements */}
            <div className="absolute top-10 right-10 w-32 h-32 bg-white/10 rounded-full blur-3xl" />
            <div className="absolute bottom-10 left-10 w-40 h-40 bg-[#8B5CF6]/30 rounded-full blur-3xl" />
          </div>
        </div>

        {/* Cover Style */}
        <div className="mb-6">
          <label className="block text-sm mb-3">Cover Style</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {styles.map((style) => (
              <button
                key={style}
                onClick={() => setCoverStyle(style)}
                className={`py-2.5 px-4 rounded-lg border text-sm capitalize transition-colors ${
                  coverStyle === style
                    ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                    : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
                }`}
              >
                {style}
              </button>
            ))}
          </div>
        </div>

        {/* Aspect Ratio */}
        <div className="mb-6">
          <label className="block text-sm mb-3">Aspect Ratio</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {ratios.map((ratio) => (
              <button
                key={ratio.value}
                onClick={() => setAspectRatio(ratio.value)}
                className={`py-2.5 px-4 rounded-lg border transition-colors ${
                  aspectRatio === ratio.value
                    ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                    : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
                }`}
              >
                <div className="text-sm font-medium">{ratio.label}</div>
                <div className="text-xs text-gray-400">{ratio.platform}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="grid md:grid-cols-2 gap-3">
          <button className="flex items-center justify-center gap-2 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors">
            <RotateCw className="w-4 h-4" />
            Regenerate
          </button>
          <button className="flex items-center justify-center gap-2 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors">
            <Upload className="w-4 h-4" />
            Upload Custom
          </button>
        </div>

        {/* Editing Controls */}
        <div className="mt-6 pt-6 border-t border-white/10">
          <h3 className="text-sm font-semibold mb-3">Quick Adjustments</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-2">Brightness</label>
              <input type="range" min="0" max="100" defaultValue="50" className="w-full" />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-2">Contrast</label>
              <input type="range" min="0" max="100" defaultValue="50" className="w-full" />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-2">Saturation</label>
              <input type="range" min="0" max="100" defaultValue="50" className="w-full" />
            </div>
          </div>
        </div>
      </GlassCard>
    </CreateLayout>
  );
}
import { useState } from 'react';
import { useNavigate } from 'react-router';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import { Download, FileAudio, Video, FileImage, FileText, CheckCircle2, Link2, ScanSearch, FileEdit, Users, Palette, Rocket } from 'lucide-react';

export function PublishPage() {
  const navigate = useNavigate();
  const [youtubeConnected] = useState(true);
  const [spotifyConnected] = useState(false);
  const [appleConnected] = useState(false);

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

  const downloadOptions = [
    { icon: FileAudio, label: 'Audio', format: 'MP3', size: '12.4 MB' },
    { icon: Video, label: 'Video', format: 'MP4', size: '45.2 MB' },
    { icon: FileImage, label: 'Cover', format: 'PNG', size: '2.1 MB' },
    { icon: FileText, label: 'Script', format: 'PDF', size: '156 KB' },
  ];

  const platforms = [
    {
      name: 'YouTube',
      connected: youtubeConnected,
      icon: '📺',
      action: 'Publish Now',
    },
    {
      name: 'Spotify',
      connected: spotifyConnected,
      icon: '🎵',
      action: 'Connect Account',
    },
    {
      name: 'Apple Podcasts',
      connected: appleConnected,
      icon: '🎙️',
      action: 'Connect Account',
    },
  ];

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
                Your podcast "love in moon" has been generated successfully. Download your files or publish directly to your favorite platforms.
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
              {downloadOptions.map((option) => {
                const Icon = option.icon;
                return (
                  <button
                    key={option.label}
                    className="w-full flex items-center gap-4 p-4 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 hover:border-[#6366F1]/30 transition-colors group"
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-lg flex items-center justify-center">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="font-medium">{option.label}</p>
                      <p className="text-sm text-gray-400">{option.format} • {option.size}</p>
                    </div>
                    <Download className="w-5 h-5 text-gray-400 group-hover:text-[#6366F1] transition-colors" />
                  </button>
                );
              })}
            </div>

            <button className="w-full mt-4 py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity">
              Download All Files
            </button>
          </GlassCard>

          {/* Publish/Share */}
          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-6">
              <Link2 className="w-5 h-5 text-[#6366F1]" />
              <h3 className="text-lg font-semibold">Share & Publish</h3>
            </div>
            
            <div className="space-y-3 mb-6">
              {platforms.map((platform) => (
                <div
                  key={platform.name}
                  className="flex items-center gap-4 p-4 bg-white/5 border border-white/10 rounded-lg"
                >
                  <div className="text-3xl">{platform.icon}</div>
                  <div className="flex-1">
                    <p className="font-medium">{platform.name}</p>
                    <p className="text-sm text-gray-400">
                      {platform.connected ? (
                        <span className="text-[#10B981]">Connected ✓</span>
                      ) : (
                        'Not connected'
                      )}
                    </p>
                  </div>
                  <button
                    className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                      platform.connected
                        ? 'bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white hover:opacity-90'
                        : 'bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    {platform.action}
                  </button>
                </div>
              ))}
            </div>

            {/* Save as Draft */}
            <div className="pt-4 border-t border-white/10">
              <button className="w-full py-3 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors">
                Save as Draft
              </button>
            </div>
          </GlassCard>
        </div>

        {/* Next Steps */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-semibold mb-4">What's Next?</h3>
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
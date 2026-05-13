import { useState } from 'react';
import { useNavigate } from 'react-router';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import { Play, Pause, Volume2, Sparkles, ScanSearch, FileEdit, Users, Palette, Rocket } from 'lucide-react';

export function AudioPage() {
  const navigate = useNavigate();
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(70);
  const [backgroundMusic, setBackgroundMusic] = useState(true);

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
      message: 'Generating audio...',
      icon: Palette,
    },
    {
      name: 'Publisher',
      status: 'waiting' as const,
      message: 'Waiting to prepare publishing',
      icon: Rocket,
    },
  ];

  const totalDuration = 300; // 5:00 in seconds

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

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
        {/* Audio Generation */}
        <GlassCard className="p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full">
              <Sparkles className="w-4 h-4 text-[#6366F1]" />
              <span className="text-sm">Powered by ElevenLabs</span>
            </div>
          </div>

          <h2 className="text-2xl font-semibold mb-6">Audio Generation</h2>

          {/* Voice Personas */}
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <GlassCard className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-full flex items-center justify-center">
                  <span className="font-semibold">AR</span>
                </div>
                <div>
                  <p className="font-medium">Alex Rivera</p>
                  <p className="text-sm text-gray-400">Professional voice</p>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-[#8B5CF6] to-[#EC4899] rounded-full flex items-center justify-center">
                  <span className="font-semibold">SC</span>
                </div>
                <div>
                  <p className="font-medium">Sarah Chen</p>
                  <p className="text-sm text-gray-400">Energetic voice</p>
                </div>
              </div>
            </GlassCard>
          </div>

          {/* Generate Button */}
          <button className="w-full py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity mb-6">
            Generate Audio Preview
          </button>

          {/* Waveform Visualization */}
          <div className="mb-6">
            <div className="h-24 bg-white/5 rounded-lg flex items-center justify-center gap-1 px-4">
              {Array.from({ length: 100 }).map((_, i) => (
                <div
                  key={i}
                  className="flex-1 bg-gradient-to-t from-[#6366F1] to-[#8B5CF6] rounded-full transition-all"
                  style={{
                    height: `${Math.random() * 60 + 20}%`,
                    opacity: i < (currentTime / totalDuration) * 100 ? 1 : 0.3,
                  }}
                />
              ))}
            </div>
          </div>

          {/* Audio Controls */}
          <div className="space-y-4">
            {/* Progress Bar */}
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-400 font-mono">{formatTime(currentTime)}</span>
              <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] rounded-full transition-all"
                  style={{ width: `${(currentTime / totalDuration) * 100}%` }}
                />
              </div>
              <span className="text-sm text-gray-400 font-mono">{formatTime(totalDuration)}</span>
            </div>

            {/* Play/Pause Button */}
            <div className="flex items-center justify-center">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="w-14 h-14 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] rounded-full flex items-center justify-center hover:opacity-90 transition-opacity"
              >
                {isPlaying ? (
                  <Pause className="w-6 h-6 text-white" />
                ) : (
                  <Play className="w-6 h-6 text-white ml-1" />
                )}
              </button>
            </div>
          </div>
        </GlassCard>

        {/* Audio Settings */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-semibold mb-4">Audio Settings</h3>
          
          <div className="space-y-4">
            {/* Background Music */}
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Background Music</p>
                <p className="text-sm text-gray-400">Add subtle background music</p>
              </div>
              <button
                onClick={() => setBackgroundMusic(!backgroundMusic)}
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  backgroundMusic ? 'bg-[#6366F1]' : 'bg-white/20'
                }`}
              >
                <div
                  className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                    backgroundMusic ? 'translate-x-7' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Volume */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="font-medium">Music Volume</label>
                <span className="text-sm text-gray-400">{volume}%</span>
              </div>
              <div className="flex items-center gap-3">
                <Volume2 className="w-4 h-4 text-gray-400" />
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={volume}
                  onChange={(e) => setVolume(parseInt(e.target.value))}
                  className="flex-1"
                  disabled={!backgroundMusic}
                />
              </div>
            </div>
          </div>
        </GlassCard>
      </div>
    </CreateLayout>
  );
}
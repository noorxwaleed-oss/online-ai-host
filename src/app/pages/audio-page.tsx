import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import {
  Play,
  Pause,
  RotateCcw,
  Loader2,
  ScanSearch,
  FileEdit,
  Users,
  Palette,
  Rocket,
} from 'lucide-react';

const TOTAL_DURATION = 300; // 5:00 in seconds
const BAR_COUNT = 100;

function formatTime(seconds: number) {
  const safe = Math.max(0, Math.floor(seconds));
  const mins = Math.floor(safe / 60);
  const secs = safe % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function AudioPage() {
  const navigate = useNavigate();
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Stable waveform heights — computed once, not regenerated on every tick
  const waveformHeights = useMemo(
    () => Array.from({ length: BAR_COUNT }, () => Math.random() * 60 + 20),
    [],
  );

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
      status: generating
        ? ('active' as const)
        : generated
          ? ('completed' as const)
          : ('active' as const),
      message: generating
        ? 'Generating audio...'
        : generated
          ? 'Audio generated successfully'
          : 'Ready to generate audio',
      icon: Palette,
    },
    {
      name: 'Publisher',
      status: 'waiting' as const,
      message: 'Waiting to prepare publishing',
      icon: Rocket,
    },
  ];

  // Tick the playback clock while playing
  useEffect(() => {
    if (!isPlaying) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    intervalRef.current = setInterval(() => {
      setCurrentTime((t) => {
        if (t >= TOTAL_DURATION) {
          setIsPlaying(false);
          return TOTAL_DURATION;
        }
        return t + 1;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isPlaying]);

  // Auto-pause at the end
  useEffect(() => {
    if (currentTime >= TOTAL_DURATION) {
      setIsPlaying(false);
    }
  }, [currentTime]);

  const handleGenerate = async () => {
    if (generating) return;
    setGenerating(true);
    setIsPlaying(false);
    setCurrentTime(0);
    try {
      // TODO: replace with real audio generation call (e.g. ElevenLabs proxy / Supabase function).
      await new Promise((r) => setTimeout(r, 1500));
      setGenerated(true);
      toast.success('Audio preview ready');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Audio generation failed';
      toast.error(message);
    } finally {
      setGenerating(false);
    }
  };

  const handlePlayPause = () => {
    if (!generated) {
      toast.warning('Generate the audio preview first.');
      return;
    }
    if (currentTime >= TOTAL_DURATION) {
      setCurrentTime(0);
    }
    setIsPlaying((p) => !p);
  };

  const handleRestart = () => {
    setCurrentTime(0);
    setIsPlaying(false);
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!generated) return;
    const bar = e.currentTarget;
    const rect = bar.getBoundingClientRect();
    const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
    setCurrentTime(Math.floor(ratio * TOTAL_DURATION));
  };

  const progressPct = (currentTime / TOTAL_DURATION) * 100;

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
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity mb-6 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>{generated ? 'Regenerate Audio Preview' : 'Generate Audio Preview'}</>
            )}
          </button>

          {/* Waveform Visualization */}
          <div className="mb-6">
            <div
              className={`h-24 bg-white/5 rounded-lg flex items-center justify-center gap-1 px-4 ${
                generating ? 'animate-pulse' : ''
              }`}
            >
              {waveformHeights.map((height, i) => {
                const filled = generated && i < (currentTime / TOTAL_DURATION) * BAR_COUNT;
                return (
                  <div
                    key={i}
                    className="flex-1 bg-gradient-to-t from-[#6366F1] to-[#8B5CF6] rounded-full transition-all"
                    style={{
                      height: `${height}%`,
                      opacity: filled ? 1 : 0.3,
                    }}
                  />
                );
              })}
            </div>
          </div>

          {/* Audio Controls */}
          <div className="space-y-4">
            {/* Progress Bar */}
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-400 font-mono w-10">
                {formatTime(currentTime)}
              </span>
              <div
                onClick={handleSeek}
                role="slider"
                aria-label="Seek"
                aria-valuemin={0}
                aria-valuemax={TOTAL_DURATION}
                aria-valuenow={currentTime}
                tabIndex={generated ? 0 : -1}
                className={`flex-1 h-2 bg-white/5 rounded-full overflow-hidden ${
                  generated ? 'cursor-pointer' : 'cursor-not-allowed opacity-50'
                }`}
              >
                <div
                  className="h-full bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] rounded-full transition-all"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
              <span className="text-sm text-gray-400 font-mono w-10 text-right">
                {formatTime(TOTAL_DURATION)}
              </span>
            </div>

            {/* Playback Buttons */}
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={handleRestart}
                disabled={!generated || currentTime === 0}
                className="w-10 h-10 bg-white/5 border border-white/10 rounded-full flex items-center justify-center hover:bg-white/10 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                aria-label="Restart"
                title="Restart"
              >
                <RotateCcw className="w-4 h-4 text-white" />
              </button>
              <button
                onClick={handlePlayPause}
                disabled={!generated}
                className="w-14 h-14 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] rounded-full flex items-center justify-center hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label={isPlaying ? 'Pause' : 'Play'}
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
      </div>
    </CreateLayout>
  );
}

import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import { Play, Pause, Loader2, ScanSearch, FileEdit, Users, Palette, Rocket } from 'lucide-react';
import { useGeneration, type PersonaDraft } from '../providers/generation-provider';
import { voicesFor, findVoice, type Gender, type VoiceOption } from '@/lib/voices';
import { previewVoice } from '@/lib/api';

type Role = 'host' | 'guest';

export function PersonasPage() {
  const navigate = useNavigate();
  const { input, personas, setPersonas } = useGeneration();

  const language = input.language;
  const allVoices = voicesFor(language);

  // Clear stale voice selections whenever language changes (catalogues don't overlap)
  useEffect(() => {
    const patch: Partial<PersonaDraft> = {};
    if (!findVoice(language, personas.voice_id_host)) {
      patch.voice_id_host = '';
      patch.host_style = '';
    }
    if (!findVoice(language, personas.voice_id_guest)) {
      patch.voice_id_guest = '';
      patch.guest_style = '';
    }
    if (Object.keys(patch).length > 0) setPersonas(patch);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language]);

  const agents = [
    { name: 'ContentAnalyzer', status: 'waiting' as const, message: 'Waiting to analyze content', icon: ScanSearch },
    { name: 'Scriptwriter',    status: 'waiting' as const, message: 'Waiting to write script',     icon: FileEdit },
    { name: 'Persona',         status: 'active'  as const, message: 'Configuring voice personas',  icon: Users },
    { name: 'Media',           status: 'waiting' as const, message: 'Waiting to generate media',   icon: Palette },
    { name: 'Publisher',       status: 'waiting' as const, message: 'Waiting to prepare publishing', icon: Rocket },
  ];

  const canProceed =
    personas.host_name.trim().length > 0 &&
    personas.guest_name.trim().length > 0 &&
    personas.voice_id_host.trim().length > 0 &&
    personas.voice_id_guest.trim().length > 0 &&
    personas.voice_id_host !== personas.voice_id_guest;

  const handleNext = () => {
    if (personas.voice_id_host && personas.voice_id_host === personas.voice_id_guest) {
      toast.warning('Host and Guest must use different voices.');
      return;
    }
    if (!canProceed) {
      toast.warning('Fill in the name, gender, and voice for both speakers.');
      return;
    }
    navigate('/create/script');
  };

  return (
    <CreateLayout
      currentStep={2}
      agents={agents}
      onPrevious={() => navigate('/create/input')}
      onNext={handleNext}
      previousLabel="Back"
      nextLabel="Generate"
    >
      <GlassCard className="p-8">
        <h2 className="text-2xl font-semibold mb-2">Configure Personas</h2>
        <p className="text-sm text-gray-400 mb-6">
          Set up the Host and Guest voices. Language:{' '}
          <span className="text-white font-medium">
            {language === 'AR' ? 'Arabic (Munsit)' : 'English (ElevenLabs)'}
          </span>
        </p>

        <div className="grid md:grid-cols-2 gap-8">
          <PersonaSection
            role="host"
            label="Host"
            personas={personas}
            setPersonas={setPersonas}
            allVoices={allVoices}
            otherVoiceId={personas.voice_id_guest}
            language={language}
          />
          <PersonaSection
            role="guest"
            label="Guest"
            personas={personas}
            setPersonas={setPersonas}
            allVoices={allVoices}
            otherVoiceId={personas.voice_id_host}
            language={language}
          />
        </div>
      </GlassCard>
    </CreateLayout>
  );
}

interface SectionProps {
  role: Role;
  label: string;
  personas: PersonaDraft;
  setPersonas: (patch: Partial<PersonaDraft>) => void;
  allVoices: VoiceOption[];
  otherVoiceId: string;
  language: 'EN' | 'AR';
}

function PersonaSection({
  role,
  label,
  personas,
  setPersonas,
  allVoices,
  otherVoiceId,
  language,
}: SectionProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const name      = role === 'host' ? personas.host_name      : personas.guest_name;
  const gender    = role === 'host' ? personas.host_gender    : personas.guest_gender;
  const voiceId   = role === 'host' ? personas.voice_id_host  : personas.voice_id_guest;
  const voice     = findVoice(language, voiceId);

  const filteredVoices = allVoices.filter((v) => v.gender === gender);

  // Reset preview when the picked voice changes
  useEffect(() => {
    setPreviewUrl(null);
    setIsPlaying(false);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  }, [voiceId]);

  const setName = (v: string) =>
    setPersonas(role === 'host' ? { host_name: v } : { guest_name: v });

  const setGender = (g: Gender) => {
    // Switching gender invalidates the current voice pick
    if (role === 'host') {
      setPersonas({ host_gender: g, voice_id_host: '', host_style: '' });
    } else {
      setPersonas({ guest_gender: g, voice_id_guest: '', guest_style: '' });
    }
  };

  const selectVoice = (v: VoiceOption) => {
    if (role === 'host') {
      setPersonas({ voice_id_host: v.id, host_style: v.style });
    } else {
      setPersonas({ voice_id_guest: v.id, guest_style: v.style });
    }
  };

  const handlePreview = async () => {
    if (!voice) {
      toast.info('Pick a voice first.');
      return;
    }
    const audio = audioRef.current;
    if (!audio) return;

    // Toggle pause if already playing this voice's preview
    if (previewUrl && isPlaying) {
      audio.pause();
      setIsPlaying(false);
      return;
    }
    // Resume if we already have the URL
    if (previewUrl && !isPlaying) {
      try {
        await audio.play();
        setIsPlaying(true);
      } catch {
        /* ignore */
      }
      return;
    }

    setPreviewLoading(true);
    try {
      const result = await previewVoice({
        voice_id: voice.id,
        language: language === 'AR' ? 'arabic' : 'english',
        gender: voice.gender,
        style: voice.style,
        dialect: voice.dialect,
      });
      setPreviewUrl(result.audio_url);
      audio.src = result.audio_url;
      await audio.play();
      setIsPlaying(true);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Could not generate preview';
      toast.error(msg);
    } finally {
      setPreviewLoading(false);
    }
  };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">{label}</h3>

      {/* 1. Name */}
      <div className="mb-4">
        <label className="block text-sm mb-2">{label} name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder={role === 'host' ? 'e.g. Mariam' : 'e.g. Omar'}
          className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[#6366F1] transition-colors"
        />
      </div>

      {/* 2. Gender */}
      <div className="mb-4">
        <label className="block text-sm mb-2">Gender</label>
        <div className="flex gap-2">
          {(['male', 'female'] as const).map((g) => (
            <button
              key={g}
              onClick={() => setGender(g)}
              className={`flex-1 py-2 rounded-lg border text-sm transition-colors capitalize ${
                gender === g
                  ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                  : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
              }`}
            >
              {g}
            </button>
          ))}
        </div>
      </div>

      {/* 3. Voice (filtered by gender) */}
      <div className="mb-4">
        <label className="block text-sm mb-2">Voice</label>
        {filteredVoices.length === 0 ? (
          <p className="text-sm text-gray-500 italic px-3 py-2 bg-white/5 border border-white/10 rounded-lg">
            No {gender} voices available in this language.
          </p>
        ) : (
          <div className="space-y-2">
            {filteredVoices.map((v) => {
              const selected = voiceId === v.id;
              const takenByOther = otherVoiceId === v.id;
              return (
                <button
                  key={v.id}
                  onClick={() => selectVoice(v)}
                  disabled={takenByOther}
                  className={`w-full flex items-center justify-between gap-3 py-2.5 px-3 rounded-lg border text-sm transition-colors text-left ${
                    selected
                      ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                      : 'border-white/10 bg-white/5 text-gray-300 hover:text-white hover:bg-white/10'
                  } ${takenByOther ? 'opacity-40 cursor-not-allowed' : ''}`}
                  title={takenByOther ? 'Already picked by the other speaker' : undefined}
                >
                  <span className="flex items-center gap-3 min-w-0">
                    <span className="font-medium capitalize truncate">
                      {v.style} voice
                    </span>
                    {v.dialect && (
                      <span className="text-xs text-gray-400 capitalize whitespace-nowrap">
                        {v.dialect} dialect
                      </span>
                    )}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 4. Preview */}
      <button
        onClick={handlePreview}
        disabled={!voice || previewLoading}
        className="w-full flex items-center justify-center gap-2 py-2.5 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {previewLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : isPlaying ? (
          <Pause className="w-4 h-4" />
        ) : (
          <Play className="w-4 h-4" />
        )}
        {previewLoading
          ? 'Generating preview…'
          : isPlaying
            ? 'Pause Preview'
            : `Preview Voice${voice ? ` — ${voice.style}` : ''}`}
      </button>

      <audio
        ref={audioRef}
        className="hidden"
        onEnded={() => setIsPlaying(false)}
        onPause={() => setIsPlaying(false)}
        onPlay={() => setIsPlaying(true)}
      />
    </div>
  );
}

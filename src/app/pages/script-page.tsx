import { useState } from 'react';
import { useNavigate } from 'react-router';
import { CreateLayout } from '../components/create-layout';
import { GlassCard } from '../components/glass-card';
import { Play, Library, ScanSearch, FileEdit, Users, Palette, Rocket } from 'lucide-react';

interface Persona {
  name: string;
  voiceStyle: string;
  gender: 'male' | 'female';
}

export function ScriptPage() {
  const navigate = useNavigate();
  const [host, setHost] = useState<Persona>({
    name: 'Alex Rivera',
    voiceStyle: 'Professional',
    gender: 'male',
  });

  const [guest, setGuest] = useState<Persona>({
    name: 'Sarah Chen',
    voiceStyle: 'Energetic',
    gender: 'female',
  });

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
      status: 'waiting' as const,
      message: 'Waiting to generate media',
      icon: Palette,
    },
    {
      name: 'Publisher',
      status: 'waiting' as const,
      message: 'Waiting to prepare publishing',
      icon: Rocket,
    },
  ];

  const voiceStyles = ['Professional', 'Energetic', 'Calm', 'Warm', 'Authoritative'];

  const PersonaCard = ({
    persona,
    onChange,
    label,
  }: {
    persona: Persona;
    onChange: (persona: Persona) => void;
    label: string;
  }) => (
    <div className="flex-1">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{label}</h3>
        <button
          onClick={() => navigate('/personas')}
          className="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-sm"
        >
          <Library className="w-4 h-4" />
          Use from library
        </button>
      </div>

      {/* Persona Preview */}
      <GlassCard className="p-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-full flex items-center justify-center">
            <span className="text-lg font-semibold">
              {persona.name.split(' ').map(n => n[0]).join('')}
            </span>
          </div>
          <div>
            <p className="font-medium">{persona.name}</p>
            <p className="text-sm text-gray-400">{persona.voiceStyle}</p>
          </div>
        </div>
      </GlassCard>

      {/* Name */}
      <div className="mb-4">
        <label className="block text-sm mb-2">Name</label>
        <input
          type="text"
          value={persona.name}
          onChange={(e) => onChange({ ...persona, name: e.target.value })}
          className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[#6366F1] transition-colors"
        />
      </div>

      {/* Voice Style */}
      <div className="mb-4">
        <label className="block text-sm mb-2">Voice Style</label>
        <div className="grid grid-cols-2 gap-2">
          {voiceStyles.map((style) => (
            <button
              key={style}
              onClick={() => onChange({ ...persona, voiceStyle: style })}
              className={`py-2 px-3 rounded-lg border text-sm transition-colors ${
                persona.voiceStyle === style
                  ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                  : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
              }`}
            >
              {style}
            </button>
          ))}
        </div>
      </div>

      {/* Gender */}
      <div className="mb-4">
        <label className="block text-sm mb-2">Gender</label>
        <div className="flex gap-2">
          {(['male', 'female'] as const).map((gender) => (
            <button
              key={gender}
              onClick={() => onChange({ ...persona, gender })}
              className={`flex-1 py-2 rounded-lg border text-sm transition-colors capitalize ${
                persona.gender === gender
                  ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                  : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
              }`}
            >
              {gender}
            </button>
          ))}
        </div>
      </div>

      {/* Preview Button */}
      <button className="w-full flex items-center justify-center gap-2 py-2.5 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors">
        <Play className="w-4 h-4" />
        Preview Voice
      </button>
    </div>
  );

  return (
    <CreateLayout
      currentStep={3}
      agents={agents}
      onPrevious={() => navigate('/create/personas')}
      onNext={() => navigate('/create/audio')}
      previousLabel="Back"
      nextLabel="Next"
    >
      <GlassCard className="p-8">
        <h2 className="text-2xl font-semibold mb-6">Configure Personas</h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          <PersonaCard persona={host} onChange={setHost} label="HOST" />
          <PersonaCard persona={guest} onChange={setGuest} label="GUEST" />
        </div>
      </GlassCard>
    </CreateLayout>
  );
}
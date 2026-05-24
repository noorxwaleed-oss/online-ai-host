import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Save, Monitor, Moon, Sun } from 'lucide-react';
import { SettingsLayout } from '../../components/settings-layout';
import { GlassCard } from '../../components/glass-card';

type Theme = 'dark' | 'light' | 'system';
type Density = 'compact' | 'comfortable' | 'spacious';

interface Prefs {
  theme: Theme;
  accent: string;
  density: Density;
  reduceMotion: boolean;
}

const DEFAULTS: Prefs = {
  theme: 'dark',
  accent: '#6366F1',
  density: 'comfortable',
  reduceMotion: false,
};

const STORAGE_KEY = 'podcraft.appearance';

const ACCENTS: { value: string; name: string }[] = [
  { value: '#6366F1', name: 'Indigo' },
  { value: '#8B5CF6', name: 'Violet' },
  { value: '#EC4899', name: 'Pink' },
  { value: '#10B981', name: 'Emerald' },
  { value: '#F59E0B', name: 'Amber' },
  { value: '#EF4444', name: 'Red' },
];

function loadPrefs(): Prefs {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULTS;
    return { ...DEFAULTS, ...(JSON.parse(raw) as Partial<Prefs>) };
  } catch {
    return DEFAULTS;
  }
}

export function AppearancePage() {
  const [prefs, setPrefs] = useState<Prefs>(loadPrefs);
  const [saving, setSaving] = useState(false);

  // Apply accent color as CSS variable live for instant preview
  useEffect(() => {
    document.documentElement.style.setProperty('--accent-color', prefs.accent);
  }, [prefs.accent]);

  const handleSave = async () => {
    setSaving(true);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
      await new Promise((r) => setTimeout(r, 300));
      toast.success('Appearance updated.');
    } finally {
      setSaving(false);
    }
  };

  const themeOptions: { value: Theme; label: string; Icon: typeof Sun }[] = [
    { value: 'light', label: 'Light', Icon: Sun },
    { value: 'dark', label: 'Dark', Icon: Moon },
    { value: 'system', label: 'System', Icon: Monitor },
  ];

  const densityOptions: { value: Density; label: string; description: string }[] = [
    { value: 'compact', label: 'Compact', description: 'Fit more on screen' },
    { value: 'comfortable', label: 'Comfortable', description: 'Recommended default' },
    { value: 'spacious', label: 'Spacious', description: 'Extra breathing room' },
  ];

  return (
    <SettingsLayout title="Appearance" description="Customize the look and feel of your workspace">
      {/* Theme */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-4">Theme</h3>
        <div className="grid grid-cols-3 gap-3">
          {themeOptions.map(({ value, label, Icon }) => {
            const selected = prefs.theme === value;
            return (
              <button
                key={value}
                onClick={() => setPrefs((p) => ({ ...p, theme: value }))}
                className={`flex flex-col items-center gap-2 py-4 rounded-lg border transition-colors ${
                  selected
                    ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                    : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-sm">{label}</span>
              </button>
            );
          })}
        </div>
        <p className="text-xs text-gray-500 mt-3">
          Light mode requires a theme refactor — currently the dark theme is applied regardless.
        </p>
      </GlassCard>

      {/* Accent */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-4">Accent Color</h3>
        <div className="flex flex-wrap gap-3">
          {ACCENTS.map((c) => {
            const selected = prefs.accent === c.value;
            return (
              <button
                key={c.value}
                onClick={() => setPrefs((p) => ({ ...p, accent: c.value }))}
                aria-label={c.name}
                title={c.name}
                className={`relative w-12 h-12 rounded-full transition-transform ${
                  selected ? 'ring-2 ring-white ring-offset-2 ring-offset-[#0a0a0f] scale-110' : ''
                }`}
                style={{ background: c.value }}
              />
            );
          })}
        </div>
      </GlassCard>

      {/* Density */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-4">Density</h3>
        <div className="grid md:grid-cols-3 gap-3">
          {densityOptions.map(({ value, label, description }) => {
            const selected = prefs.density === value;
            return (
              <button
                key={value}
                onClick={() => setPrefs((p) => ({ ...p, density: value }))}
                className={`text-left p-4 rounded-lg border transition-colors ${
                  selected
                    ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                    : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
                }`}
              >
                <p className="font-medium mb-1">{label}</p>
                <p className="text-xs text-gray-400">{description}</p>
              </button>
            );
          })}
        </div>
      </GlassCard>

      {/* Motion */}
      <GlassCard className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <p className="font-medium">Reduce motion</p>
            <p className="text-sm text-gray-400">
              Minimize animations and transitions across the app.
            </p>
          </div>
          <button
            onClick={() => setPrefs((p) => ({ ...p, reduceMotion: !p.reduceMotion }))}
            className={`relative shrink-0 w-12 h-6 rounded-full transition-colors ${
              prefs.reduceMotion ? 'bg-[#6366F1]' : 'bg-white/20'
            }`}
            aria-pressed={prefs.reduceMotion}
            aria-label="Reduce motion"
          >
            <div
              className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                prefs.reduceMotion ? 'translate-x-7' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </GlassCard>

      <div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {saving ? 'Saving...' : 'Save Appearance'}
        </button>
      </div>
    </SettingsLayout>
  );
}

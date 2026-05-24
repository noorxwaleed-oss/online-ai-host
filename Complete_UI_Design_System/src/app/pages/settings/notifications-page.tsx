import { useState } from 'react';
import { toast } from 'sonner';
import { Save } from 'lucide-react';
import { SettingsLayout } from '../../components/settings-layout';
import { GlassCard } from '../../components/glass-card';

type PrefKey =
  | 'emailEpisodeReady'
  | 'emailWeeklySummary'
  | 'emailMarketing'
  | 'pushEpisodeReady'
  | 'pushMentions'
  | 'inAppActivity';

type Prefs = Record<PrefKey, boolean>;

const DEFAULTS: Prefs = {
  emailEpisodeReady: true,
  emailWeeklySummary: true,
  emailMarketing: false,
  pushEpisodeReady: true,
  pushMentions: true,
  inAppActivity: true,
};

const STORAGE_KEY = 'podcraft.notifications';

function loadPrefs(): Prefs {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULTS;
    return { ...DEFAULTS, ...(JSON.parse(raw) as Partial<Prefs>) };
  } catch {
    return DEFAULTS;
  }
}

function Toggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (next: boolean) => void;
}) {
  return (
    <div className="flex items-start justify-between gap-4 py-3">
      <div className="flex-1">
        <p className="font-medium">{label}</p>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
      <button
        onClick={() => onChange(!checked)}
        aria-pressed={checked}
        aria-label={label}
        className={`relative shrink-0 w-12 h-6 rounded-full transition-colors ${
          checked ? 'bg-[#6366F1]' : 'bg-white/20'
        }`}
      >
        <div
          className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
            checked ? 'translate-x-7' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
}

export function NotificationsPage() {
  const [prefs, setPrefs] = useState<Prefs>(loadPrefs);
  const [saving, setSaving] = useState(false);

  const update = (key: PrefKey) => (next: boolean) => setPrefs((p) => ({ ...p, [key]: next }));

  const handleSave = async () => {
    setSaving(true);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
      // TODO: also persist to Supabase profiles table when backend column exists.
      await new Promise((r) => setTimeout(r, 300));
      toast.success('Notification preferences saved.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <SettingsLayout
      title="Notifications"
      description="Control how and when you receive notifications"
    >
      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-2">Email</h3>
        <div className="divide-y divide-white/10">
          <Toggle
            label="Episode ready"
            description="When a podcast finishes generating, send me an email."
            checked={prefs.emailEpisodeReady}
            onChange={update('emailEpisodeReady')}
          />
          <Toggle
            label="Weekly summary"
            description="Get a digest of your activity every Monday."
            checked={prefs.emailWeeklySummary}
            onChange={update('emailWeeklySummary')}
          />
          <Toggle
            label="Product updates & tips"
            description="New features, tutorials, and occasional offers."
            checked={prefs.emailMarketing}
            onChange={update('emailMarketing')}
          />
        </div>
      </GlassCard>

      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-2">Push</h3>
        <div className="divide-y divide-white/10">
          <Toggle
            label="Episode ready"
            description="Push notification when audio generation completes."
            checked={prefs.pushEpisodeReady}
            onChange={update('pushEpisodeReady')}
          />
          <Toggle
            label="Mentions & replies"
            description="When someone mentions you in a comment or shared episode."
            checked={prefs.pushMentions}
            onChange={update('pushMentions')}
          />
        </div>
      </GlassCard>

      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-2">In-app</h3>
        <div className="divide-y divide-white/10">
          <Toggle
            label="Activity feed"
            description="Show a notification badge for new activity inside the app."
            checked={prefs.inAppActivity}
            onChange={update('inAppActivity')}
          />
        </div>
      </GlassCard>

      <div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </SettingsLayout>
  );
}

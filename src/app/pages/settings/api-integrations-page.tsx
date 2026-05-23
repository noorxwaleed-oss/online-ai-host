import { useState } from 'react';
import { toast } from 'sonner';
import { Copy, Plus, Trash2, Eye, EyeOff, Plug } from 'lucide-react';
import { SettingsLayout } from '../../components/settings-layout';
import { GlassCard } from '../../components/glass-card';

interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  fullKey: string;
  createdAt: string;
  lastUsed: string;
}

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: string;
  connected: boolean;
}

function generateKey(): { prefix: string; full: string } {
  const random =
    typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID().replace(/-/g, '')
      : Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
  const full = `pk_live_${random}`;
  return { prefix: full.slice(0, 12), full };
}

export function ApiIntegrationsPage() {
  const [keys, setKeys] = useState<ApiKey[]>([
    {
      id: '1',
      name: 'Production',
      prefix: 'pk_live_a1b2',
      fullKey: 'pk_live_a1b2c3d4e5f6g7h8i9j0',
      createdAt: '2025-01-15',
      lastUsed: '2 hours ago',
    },
  ]);
  const [newKeyName, setNewKeyName] = useState('');
  const [revealedId, setRevealedId] = useState<string | null>(null);

  const [integrations, setIntegrations] = useState<Integration[]>([
    {
      id: 'elevenlabs',
      name: 'ElevenLabs',
      description: 'AI voice generation for your podcast hosts and guests.',
      icon: '🎙️',
      connected: true,
    },
    {
      id: 'cloudinary',
      name: 'Cloudinary',
      description: 'Asset storage and RSS feed hosting for published episodes.',
      icon: '☁️',
      connected: true,
    },
    {
      id: 'huggingface',
      name: 'Hugging Face',
      description: 'Inference endpoints for script generation models.',
      icon: '🤗',
      connected: false,
    },
    {
      id: 'zapier',
      name: 'Zapier',
      description: 'Trigger workflows when a podcast is generated.',
      icon: '⚡',
      connected: false,
    },
  ]);

  const handleCreateKey = () => {
    if (!newKeyName.trim()) {
      toast.warning('Give the key a name first.');
      return;
    }
    const { prefix, full } = generateKey();
    const newKey: ApiKey = {
      id: crypto.randomUUID(),
      name: newKeyName.trim(),
      prefix,
      fullKey: full,
      createdAt: new Date().toISOString().slice(0, 10),
      lastUsed: 'Never',
    };
    setKeys((k) => [newKey, ...k]);
    setNewKeyName('');
    setRevealedId(newKey.id);
    toast.success('API key created. Copy it now — it won\'t be shown again.');
  };

  const handleRevoke = (id: string) => {
    setKeys((k) => k.filter((key) => key.id !== id));
    toast.success('API key revoked.');
  };

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success('Copied to clipboard.');
    } catch {
      toast.error('Could not copy.');
    }
  };

  const handleToggleIntegration = (id: string) => {
    setIntegrations((list) =>
      list.map((i) => (i.id === id ? { ...i, connected: !i.connected } : i)),
    );
    const integration = integrations.find((i) => i.id === id);
    if (integration) {
      toast.info(
        integration.connected
          ? `${integration.name} disconnected.`
          : `${integration.name} connection placeholder — wire to OAuth flow.`,
      );
    }
  };

  return (
    <SettingsLayout
      title="API & Integrations"
      description="Connect third-party services and manage API keys"
    >
      {/* API Keys */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">API Keys</h3>
        </div>

        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            placeholder="Key name (e.g. Staging, Mobile app)"
            className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[#6366F1] transition-colors"
          />
          <button
            onClick={handleCreateKey}
            className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            <Plus className="w-4 h-4" />
            Create Key
          </button>
        </div>

        <div className="space-y-2">
          {keys.length === 0 && (
            <p className="text-sm text-gray-500 text-center py-6">
              No API keys yet. Create one to get started.
            </p>
          )}
          {keys.map((key) => {
            const revealed = revealedId === key.id;
            return (
              <div
                key={key.id}
                className="flex items-center gap-3 p-3 bg-white/5 border border-white/10 rounded-lg"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-medium truncate">{key.name}</p>
                    <span className="text-xs text-gray-500">Created {key.createdAt}</span>
                  </div>
                  <p className="text-sm font-mono text-gray-300 truncate">
                    {revealed ? key.fullKey : `${key.prefix}${'•'.repeat(20)}`}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">Last used: {key.lastUsed}</p>
                </div>
                <button
                  onClick={() => setRevealedId(revealed ? null : key.id)}
                  className="p-2 hover:bg-white/10 rounded transition-colors"
                  title={revealed ? 'Hide' : 'Reveal'}
                  aria-label={revealed ? 'Hide key' : 'Reveal key'}
                >
                  {revealed ? (
                    <EyeOff className="w-4 h-4 text-gray-400" />
                  ) : (
                    <Eye className="w-4 h-4 text-gray-400" />
                  )}
                </button>
                <button
                  onClick={() => handleCopy(key.fullKey)}
                  className="p-2 hover:bg-white/10 rounded transition-colors"
                  title="Copy"
                  aria-label="Copy key"
                >
                  <Copy className="w-4 h-4 text-gray-400" />
                </button>
                <button
                  onClick={() => handleRevoke(key.id)}
                  className="p-2 hover:bg-[#EF4444]/20 rounded transition-colors"
                  title="Revoke"
                  aria-label="Revoke key"
                >
                  <Trash2 className="w-4 h-4 text-[#EF4444]" />
                </button>
              </div>
            );
          })}
        </div>
      </GlassCard>

      {/* Integrations */}
      <GlassCard className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Plug className="w-5 h-5 text-[#6366F1]" />
          <h3 className="text-lg font-semibold">Connected Services</h3>
        </div>
        <div className="space-y-3">
          {integrations.map((integration) => (
            <div
              key={integration.id}
              className="flex items-center gap-4 p-4 bg-white/5 border border-white/10 rounded-lg"
            >
              <div className="text-3xl">{integration.icon}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-0.5">
                  <p className="font-medium">{integration.name}</p>
                  {integration.connected && (
                    <span className="text-xs px-2 py-0.5 bg-[#10B981]/20 text-[#10B981] rounded-full">
                      Connected
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-400">{integration.description}</p>
              </div>
              <button
                onClick={() => handleToggleIntegration(integration.id)}
                className={`px-4 py-2 text-sm rounded-lg transition-colors ${
                  integration.connected
                    ? 'bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10'
                    : 'bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white hover:opacity-90'
                }`}
              >
                {integration.connected ? 'Disconnect' : 'Connect'}
              </button>
            </div>
          ))}
        </div>
      </GlassCard>
    </SettingsLayout>
  );
}

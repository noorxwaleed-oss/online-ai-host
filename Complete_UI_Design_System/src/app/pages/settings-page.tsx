import { useNavigate } from 'react-router';
import { Header } from '../components/header';
import { Footer } from '../components/footer';
import { GlassCard } from '../components/glass-card';
import { BackgroundEffects } from '../components/background-effects';
import { User, Bell, Shield, Palette, Zap, ArrowRight, type LucideIcon } from 'lucide-react';

interface SettingsCard {
  title: string;
  description: string;
  cta: string;
  path: string;
  icon: LucideIcon;
  gradient: string;
}

const CARDS: SettingsCard[] = [
  {
    title: 'Account',
    description: 'Update your personal information and email preferences',
    cta: 'Manage Account',
    path: '/settings/account',
    icon: User,
    gradient: 'from-[#6366F1] to-[#8B5CF6]',
  },
  {
    title: 'Notifications',
    description: 'Control how and when you receive notifications',
    cta: 'Configure',
    path: '/settings/notifications',
    icon: Bell,
    gradient: 'from-[#8B5CF6] to-[#EC4899]',
  },
  {
    title: 'Privacy & Security',
    description: 'Manage your privacy settings and security preferences',
    cta: 'View Settings',
    path: '/settings/privacy',
    icon: Shield,
    gradient: 'from-[#10B981] to-[#06B6D4]',
  },
  {
    title: 'Appearance',
    description: 'Customize the look and feel of your workspace',
    cta: 'Customize',
    path: '/settings/appearance',
    icon: Palette,
    gradient: 'from-[#F59E0B] to-[#EF4444]',
  },
  {
    title: 'API & Integrations',
    description: 'Connect third-party services and manage API keys',
    cta: 'Manage',
    path: '/settings/integrations',
    icon: Zap,
    gradient: 'from-[#EC4899] to-[#8B5CF6]',
  },
];

export function SettingsPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      <BackgroundEffects />
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-6 py-12 w-full">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Settings</h1>
          <p className="text-gray-400">Manage your account settings and preferences</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {CARDS.map((card) => {
            const Icon = card.icon;
            return (
              <button
                key={card.path}
                onClick={() => navigate(card.path)}
                className="text-left group"
              >
                <GlassCard className="p-6 h-full transition-all group-hover:border-[#6366F1]/40 group-hover:translate-y-[-2px]">
                  <div className="flex items-center gap-3 mb-4">
                    <div
                      className={`w-10 h-10 bg-gradient-to-br ${card.gradient} rounded-lg flex items-center justify-center`}
                    >
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold">{card.title}</h3>
                  </div>
                  <p className="text-sm text-gray-400 mb-4">{card.description}</p>
                  <span className="inline-flex items-center gap-1 text-sm text-[#6366F1] group-hover:text-[#8B5CF6] transition-colors">
                    {card.cta}
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                  </span>
                </GlassCard>
              </button>
            );
          })}
        </div>
      </main>

      <Footer />
    </div>
  );
}

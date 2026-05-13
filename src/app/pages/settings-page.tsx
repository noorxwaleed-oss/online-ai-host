import { Header } from '../components/header';
import { Footer } from '../components/footer';
import { GlassCard } from '../components/glass-card';
import { BackgroundEffects } from '../components/background-effects';
import { User, Bell, Shield, Palette, Zap } from 'lucide-react';

export function SettingsPage() {
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
          {/* Account Settings */}
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold">Account</h3>
            </div>
            <p className="text-sm text-gray-400 mb-4">
              Update your personal information and email preferences
            </p>
            <button className="text-sm text-[#6366F1] hover:text-[#8B5CF6] transition-colors">
              Manage Account →
            </button>
          </GlassCard>

          {/* Notifications */}
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-[#8B5CF6] to-[#EC4899] rounded-lg flex items-center justify-center">
                <Bell className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold">Notifications</h3>
            </div>
            <p className="text-sm text-gray-400 mb-4">
              Control how and when you receive notifications
            </p>
            <button className="text-sm text-[#6366F1] hover:text-[#8B5CF6] transition-colors">
              Configure →
            </button>
          </GlassCard>

          {/* Privacy & Security */}
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-[#10B981] to-[#06B6D4] rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold">Privacy & Security</h3>
            </div>
            <p className="text-sm text-gray-400 mb-4">
              Manage your privacy settings and security preferences
            </p>
            <button className="text-sm text-[#6366F1] hover:text-[#8B5CF6] transition-colors">
              View Settings →
            </button>
          </GlassCard>

          {/* Appearance */}
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-[#F59E0B] to-[#EF4444] rounded-lg flex items-center justify-center">
                <Palette className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold">Appearance</h3>
            </div>
            <p className="text-sm text-gray-400 mb-4">
              Customize the look and feel of your workspace
            </p>
            <button className="text-sm text-[#6366F1] hover:text-[#8B5CF6] transition-colors">
              Customize →
            </button>
          </GlassCard>

          {/* API & Integrations */}
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-[#EC4899] to-[#8B5CF6] rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold">API & Integrations</h3>
            </div>
            <p className="text-sm text-gray-400 mb-4">
              Connect third-party services and manage API keys
            </p>
            <button className="text-sm text-[#6366F1] hover:text-[#8B5CF6] transition-colors">
              Manage →
            </button>
          </GlassCard>
        </div>
      </main>

      <Footer />
    </div>
  );
}
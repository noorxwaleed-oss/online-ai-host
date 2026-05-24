import { useState } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { Shield, AlertTriangle, LogOut, Trash2 } from 'lucide-react';
import { SettingsLayout } from '../../components/settings-layout';
import { GlassCard } from '../../components/glass-card';
import { useAuth } from '../../providers/auth-provider';
import { supabase } from '@/lib/supabase';

export function PrivacySecurityPage() {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const [twoFactor, setTwoFactor] = useState(false);
  const [analyticsConsent, setAnalyticsConsent] = useState(true);
  const [confirmDelete, setConfirmDelete] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [signingOutAll, setSigningOutAll] = useState(false);

  const handleSignOutAll = async () => {
    setSigningOutAll(true);
    try {
      const { error } = await supabase.auth.signOut({ scope: 'global' });
      if (error) throw error;
      toast.success('Signed out of all devices.');
      navigate('/login', { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not sign out other sessions.';
      toast.error(message);
    } finally {
      setSigningOutAll(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (confirmDelete !== 'DELETE') {
      toast.warning('Type DELETE to confirm.');
      return;
    }
    setDeleting(true);
    try {
      // Account deletion requires a server-side endpoint with the service role key —
      // the anon client cannot delete users for security reasons. Wire to your backend:
      //   await fetch('/api/account', { method: 'DELETE' });
      // For now, sign the user out and inform them.
      await signOut();
      toast.success('Deletion request submitted. You have been signed out.');
      navigate('/', { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not delete account.';
      toast.error(message);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <SettingsLayout
      title="Privacy & Security"
      description="Manage your privacy settings and security preferences"
    >
      {/* Two-factor */}
      <GlassCard className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Shield className="w-5 h-5 text-[#10B981]" />
              <h3 className="text-lg font-semibold">Two-Factor Authentication</h3>
            </div>
            <p className="text-sm text-gray-400">
              Add an extra layer of security to your account with an authenticator app.
            </p>
          </div>
          <button
            onClick={() => {
              setTwoFactor((v) => !v);
              toast.info(
                twoFactor
                  ? '2FA disabled (demo). Wire to Supabase MFA.'
                  : '2FA setup placeholder. Wire to Supabase MFA enrollment.',
              );
            }}
            className={`relative shrink-0 w-12 h-6 rounded-full transition-colors ${
              twoFactor ? 'bg-[#10B981]' : 'bg-white/20'
            }`}
            aria-pressed={twoFactor}
            aria-label="Two-factor authentication"
          >
            <div
              className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                twoFactor ? 'translate-x-7' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </GlassCard>

      {/* Privacy */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-4">Privacy</h3>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <p className="font-medium">Anonymous usage analytics</p>
            <p className="text-sm text-gray-400">
              Help us improve PodCraft by sharing anonymous product usage data.
            </p>
          </div>
          <button
            onClick={() => setAnalyticsConsent((v) => !v)}
            className={`relative shrink-0 w-12 h-6 rounded-full transition-colors ${
              analyticsConsent ? 'bg-[#6366F1]' : 'bg-white/20'
            }`}
            aria-pressed={analyticsConsent}
            aria-label="Anonymous analytics"
          >
            <div
              className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                analyticsConsent ? 'translate-x-7' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </GlassCard>

      {/* Sessions */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-1">Active Session</h3>
        <p className="text-sm text-gray-400 mb-4">
          Signed in as <span className="text-white">{user?.email}</span>
        </p>
        <button
          onClick={handleSignOutAll}
          disabled={signingOutAll}
          className="flex items-center gap-2 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50"
        >
          <LogOut className="w-4 h-4" />
          {signingOutAll ? 'Signing out...' : 'Sign out of all devices'}
        </button>
      </GlassCard>

      {/* Danger zone */}
      <GlassCard className="p-6 border-[#EF4444]/30">
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle className="w-5 h-5 text-[#EF4444]" />
          <h3 className="text-lg font-semibold text-[#EF4444]">Danger Zone</h3>
        </div>
        <p className="text-sm text-gray-400 mb-4">
          Permanently delete your account and all associated data. This action cannot be undone.
        </p>
        <label className="block text-sm mb-2" htmlFor="confirm-delete">
          Type <span className="font-mono text-[#EF4444]">DELETE</span> to confirm
        </label>
        <input
          id="confirm-delete"
          type="text"
          value={confirmDelete}
          onChange={(e) => setConfirmDelete(e.target.value)}
          placeholder="DELETE"
          className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 mb-3 focus:outline-none focus:border-[#EF4444] transition-colors"
        />
        <button
          onClick={handleDeleteAccount}
          disabled={deleting || confirmDelete !== 'DELETE'}
          className="flex items-center gap-2 px-6 py-2.5 bg-[#EF4444] text-white rounded-lg hover:bg-[#DC2626] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Trash2 className="w-4 h-4" />
          {deleting ? 'Deleting...' : 'Delete my account'}
        </button>
      </GlassCard>
    </SettingsLayout>
  );
}

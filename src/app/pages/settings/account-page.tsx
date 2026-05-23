import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { User, Mail, Lock, Save } from 'lucide-react';
import { SettingsLayout } from '../../components/settings-layout';
import { GlassCard } from '../../components/glass-card';
import { useAuth } from '../../providers/auth-provider';
import { supabase } from '@/lib/supabase';

export function AccountPage() {
  const { user } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);

  useEffect(() => {
    if (user) {
      setFullName((user.user_metadata?.full_name as string | undefined) ?? '');
      setEmail(user.email ?? '');
    }
  }, [user]);

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      const updates: { data?: { full_name: string }; email?: string } = {};
      if (fullName) updates.data = { full_name: fullName };
      if (email && email !== user?.email) updates.email = email;

      const { error } = await supabase.auth.updateUser(updates);
      if (error) throw error;

      if (updates.email) {
        toast.success('Check your inbox to confirm the new email address.');
      } else {
        toast.success('Profile updated.');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not update profile.';
      toast.error(message);
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword.length < 8) {
      toast.warning('Password must be at least 8 characters.');
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match.');
      return;
    }
    setChangingPassword(true);
    try {
      const { error } = await supabase.auth.updateUser({ password: newPassword });
      if (error) throw error;
      toast.success('Password updated.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not update password.';
      toast.error(message);
    } finally {
      setChangingPassword(false);
    }
  };

  return (
    <SettingsLayout title="Account" description="Update your personal information and email">
      {/* Profile */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-4">Profile</h3>
        <form onSubmit={handleProfileSave} className="space-y-4">
          <div>
            <label className="block text-sm mb-2" htmlFor="account-name">
              Full Name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                id="account-name"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm mb-2" htmlFor="account-email">
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                id="account-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Changing your email will require confirmation from the new address.
            </p>
          </div>

          <button
            type="submit"
            disabled={savingProfile}
            className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {savingProfile ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </GlassCard>

      {/* Password */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-4">Change Password</h3>
        <form onSubmit={handlePasswordChange} className="space-y-4">
          <div>
            <label className="block text-sm mb-2" htmlFor="current-password">
              Current Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                id="current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                autoComplete="current-password"
                className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm mb-2" htmlFor="new-password">
                New Password
              </label>
              <input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                autoComplete="new-password"
                minLength={8}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm mb-2" htmlFor="confirm-new-password">
                Confirm Password
              </label>
              <input
                id="confirm-new-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                autoComplete="new-password"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={changingPassword}
            className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            <Lock className="w-4 h-4" />
            {changingPassword ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      </GlassCard>
    </SettingsLayout>
  );
}

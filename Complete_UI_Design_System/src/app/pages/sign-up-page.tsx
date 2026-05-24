import { useState } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { GlassCard } from '../components/glass-card';
import { BackgroundEffects } from '../components/background-effects';
import { Sparkles, Mail, Lock, User, Github } from 'lucide-react';
import { useAuth } from '../providers/auth-provider';

export function SignUpPage() {
  const navigate = useNavigate();
  const { signUp, signInWithProvider } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match.');
      return;
    }
    if (!formData.agreeToTerms) {
      toast.warning('Please accept the Terms & Conditions.');
      return;
    }
    if (formData.password.length < 8) {
      toast.warning('Password must be at least 8 characters.');
      return;
    }

    setSubmitting(true);
    try {
      await signUp(formData.email, formData.password, formData.name);
      toast.success('Account created! Please check your email to confirm.');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not create account.';
      toast.error(
        message.includes('already registered') ? 'This email is already registered.' : message,
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleOAuth = async (provider: 'google' | 'github') => {
    try {
      await signInWithProvider(provider);
    } catch (err) {
      const message = err instanceof Error ? err.message : `${provider} sign-up failed.`;
      toast.error(message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-12">
      <BackgroundEffects />
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-lg flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <span className="text-2xl font-semibold">PodCraft AI</span>
        </div>

        <GlassCard className="p-8">
          <h1 className="text-2xl font-semibold mb-2 text-center">Create Account</h1>
          <p className="text-gray-400 text-center mb-6">Start creating amazing podcasts today</p>

          <form onSubmit={handleSignUp} className="space-y-4">
            <div>
              <label className="block text-sm mb-2" htmlFor="signup-name">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="signup-name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="John Doe"
                  className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
                  required
                  autoComplete="name"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm mb-2" htmlFor="signup-email">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="signup-email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="your@email.com"
                  className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
                  required
                  autoComplete="email"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm mb-2" htmlFor="signup-password">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="signup-password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="••••••••"
                  className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
                  required
                  minLength={8}
                  autoComplete="new-password"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm mb-2" htmlFor="signup-confirm-password">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="signup-confirm-password"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  placeholder="••••••••"
                  className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
                  required
                  autoComplete="new-password"
                />
              </div>
            </div>

            <label className="flex items-start gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.agreeToTerms}
                onChange={(e) => setFormData({ ...formData, agreeToTerms: e.target.checked })}
                className="w-4 h-4 mt-1 rounded border-white/10 bg-white/5 text-[#6366F1] focus:ring-[#6366F1]"
                required
              />
              <span className="text-sm text-gray-400">
                I agree to the{' '}
                <a href="#" className="text-[#6366F1] hover:underline">
                  Terms & Conditions
                </a>{' '}
                and{' '}
                <a href="#" className="text-[#6366F1] hover:underline">
                  Privacy Policy
                </a>
              </span>
            </label>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-sm text-gray-400">or sign up with</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => handleOAuth('google')}
              className="flex items-center justify-center gap-2 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              <span className="text-sm">Google</span>
            </button>
            <button
              type="button"
              onClick={() => handleOAuth('github')}
              className="flex items-center justify-center gap-2 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors"
            >
              <Github className="w-5 h-5" />
              <span className="text-sm">GitHub</span>
            </button>
          </div>

          <p className="text-center text-sm text-gray-400 mt-6">
            Already have an account?{' '}
            <button onClick={() => navigate('/login')} className="text-[#6366F1] hover:underline">
              Sign in
            </button>
          </p>
        </GlassCard>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router';
import { toast } from 'sonner';
import { GlassCard } from '../components/glass-card';
import { BackgroundEffects } from '../components/background-effects';
import { Sparkles, Mail, Lock, Github } from 'lucide-react';
import { useAuth } from '../providers/auth-provider';

interface LocationState {
  from?: { pathname: string };
}

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { signIn, signInWithProvider } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const redirectTo = (location.state as LocationState | null)?.from?.pathname ?? '/dashboard';

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.warning('Please enter both email and password.');
      return;
    }
    setSubmitting(true);
    try {
      await signIn(email, password);
      toast.success('Welcome back!');
      navigate(redirectTo, { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Sign-in failed.';
      toast.error(message.includes('Invalid') ? 'Incorrect email or password.' : message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleOAuth = async (provider: 'google' | 'github') => {
    try {
      await signInWithProvider(provider);
    } catch (err) {
      const message = err instanceof Error ? err.message : `${provider} sign-in failed.`;
      toast.error(message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-12">
      <BackgroundEffects />
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-lg flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <span className="text-2xl font-semibold">PodCraft AI</span>
        </div>

        <GlassCard className="p-8">
          <h1 className="text-2xl font-semibold mb-2 text-center">Welcome Back</h1>
          <p className="text-gray-400 text-center mb-6">Sign in to continue to your account</p>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm mb-2" htmlFor="login-email">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="login-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
                  required
                  autoComplete="email"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm mb-2" htmlFor="login-password">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="login-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
                  required
                  autoComplete="current-password"
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-white/10 bg-white/5 text-[#6366F1] focus:ring-[#6366F1]"
                />
                <span className="text-gray-400">Remember me</span>
              </label>
              <button
                type="button"
                onClick={() => navigate('/forgot-password')}
                className="text-[#6366F1] hover:underline"
              >
                Forgot password?
              </button>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-sm text-gray-400">or continue with</span>
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
            Don&apos;t have an account?{' '}
            <button
              onClick={() => navigate('/signup')}
              className="text-[#6366F1] hover:underline"
            >
              Sign up
            </button>
          </p>
        </GlassCard>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router';
import { toast } from 'sonner';
import { Sparkles, Settings, LogOut } from 'lucide-react';
import { useAuth } from '../providers/auth-provider';

export function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, signOut } = useAuth();
  const [loggingOut, setLoggingOut] = useState(false);

  const isAuthenticated = Boolean(user);

  const navItems = [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Create New', path: '/create/input' },
    { label: 'Personas', path: '/personas' },
    { label: 'My Library', path: '/library' },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  const handleLogout = async () => {
    if (loggingOut) return;
    setLoggingOut(true);
    try {
      await signOut();
      toast.success('Logged out successfully');
      navigate('/', { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Logout failed';
      toast.error(message);
    } finally {
      setLoggingOut(false);
    }
  };

  const displayName =
    (user?.user_metadata?.full_name as string | undefined) ??
    user?.email?.split('@')[0] ??
    'User';

  return (
    <header className="border-b border-white/10 bg-[#0A0A0F]/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
          <div className="w-8 h-8 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-semibold">PodCraft AI</span>
        </div>

        {/* Navigation */}
        <nav className="flex items-center gap-8">
          {navItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path);
            const Icon = item.icon;

            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`relative py-1 transition-colors flex items-center gap-2 ${
                  isActive ? 'text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                {Icon && <Icon className="w-4 h-4" />}
                {item.label}
                {isActive && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#8B5CF6]" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Right side: auth controls */}
        {isAuthenticated ? (
          <div className="flex items-center gap-3">
            <span
              className="text-sm text-gray-300 hidden md:inline-block max-w-[160px] truncate"
              title={user?.email ?? ''}
            >
              👋 {displayName}
            </span>
            <button
              onClick={handleLogout}
              disabled={loggingOut}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 hover:border-[#EF4444]/40 hover:text-[#EF4444] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Log out"
            >
              <LogOut className="w-4 h-4" />
              {loggingOut ? 'Logging out...' : 'Logout'}
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-2 text-sm text-white hover:text-[#6366F1] transition-colors"
            >
              Get Started
            </button>
            <button
              onClick={() => navigate('/signup')}
              className="px-6 py-2 text-sm bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity"
            >
              Sign Up
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

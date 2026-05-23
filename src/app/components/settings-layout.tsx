import { type ReactNode } from 'react';
import { useNavigate } from 'react-router';
import { ArrowLeft } from 'lucide-react';
import { Header } from './header';
import { Footer } from './footer';
import { BackgroundEffects } from './background-effects';

interface SettingsLayoutProps {
  title: string;
  description?: string;
  children: ReactNode;
}

export function SettingsLayout({ title, description, children }: SettingsLayoutProps) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      <BackgroundEffects />
      <Header />

      <main className="flex-1 max-w-4xl mx-auto px-6 py-12 w-full">
        <button
          onClick={() => navigate('/settings')}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Settings
        </button>

        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">{title}</h1>
          {description && <p className="text-gray-400">{description}</p>}
        </div>

        <div className="space-y-6">{children}</div>
      </main>

      <Footer />
    </div>
  );
}

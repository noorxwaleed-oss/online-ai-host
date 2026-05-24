import { useNavigate } from 'react-router';
import { Header } from '../components/header';
import { GlassCard } from '../components/glass-card';
import { BackgroundEffects } from '../components/background-effects';
import { Search, Sparkles, FileText, Mic, Music, Play } from 'lucide-react';

export function DashboardPage() {
  const navigate = useNavigate();

  const agents = [
    {
      icon: Sparkles,
      title: 'Content Agent',
      description: 'Analyzes input from URLs, PDFs, and text',
      gradient: 'from-[#6366F1] to-[#8B5CF6]',
    },
    {
      icon: FileText,
      title: 'Script Agent',
      description: 'Writes engaging dialogue and conversation',
      gradient: 'from-[#8B5CF6] to-[#EC4899]',
    },
    {
      icon: Mic,
      title: 'Audio Agent',
      description: 'Generates realistic AI voices',
      gradient: 'from-[#10B981] to-[#06B6D4]',
    },
    {
      icon: Music,
      title: 'Video Agent',
      description: 'Renders visual content and cover art',
      gradient: 'from-[#F59E0B] to-[#EF4444]',
    },
  ];

  const recentCreations = [
    {
      id: 1,
      title: 'The Future of AI in Healthcare',
      duration: '15:24',
      date: 'March 14, 2026',
      cover: 'medical-ai',
    },
    {
      id: 2,
      title: 'Climate Change Solutions',
      duration: '12:45',
      date: 'March 13, 2026',
      cover: 'climate',
    },
    {
      id: 3,
      title: 'Cryptocurrency Explained',
      duration: '18:30',
      date: 'March 12, 2026',
      cover: 'crypto',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <BackgroundEffects />
      <Header />
      
      <main className="flex-1 max-w-7xl mx-auto px-6 py-8 w-full">
        {/* Search Bar */}
        <div className="mb-8">
          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search your episodes..."
              className="w-full bg-white/5 border border-white/10 rounded-xl pl-12 pr-4 py-4 focus:outline-none focus:border-[#6366F1] transition-colors"
            />
          </div>
        </div>

        {/* How It Works */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-6">How It Works</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {agents.map((agent, index) => {
              const Icon = agent.icon;
              return (
                <GlassCard key={index} className="p-6 hover:border-white/20 transition-colors">
                  <div className={`w-12 h-12 bg-gradient-to-br ${agent.gradient} rounded-lg flex items-center justify-center mb-4`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{agent.title}</h3>
                  <p className="text-sm text-gray-400">{agent.description}</p>
                </GlassCard>
              );
            })}
          </div>
        </section>

        {/* Recent Creations */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold">Your Recent Creations</h2>
            <button
              onClick={() => navigate('/create/input')}
              className="text-sm text-[#6366F1] hover:underline flex items-center gap-1"
            >
              View All
            </button>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recentCreations.map((podcast) => (
              <GlassCard key={podcast.id} className="overflow-hidden hover:border-white/20 transition-colors group cursor-pointer">
                {/* Cover Art */}
                <div className="aspect-video bg-gradient-to-br from-[#6366F1]/20 to-[#8B5CF6]/20 flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] opacity-0 group-hover:opacity-20 transition-opacity" />
                  <div className="w-16 h-16 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Play className="w-8 h-8 text-white ml-1" />
                  </div>
                </div>
                
                {/* Info */}
                <div className="p-5">
                  <h3 className="font-semibold mb-2 line-clamp-2">{podcast.title}</h3>
                  <div className="flex items-center justify-between text-sm text-gray-400">
                    <span>{podcast.duration}</span>
                    <span>{podcast.date}</span>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </section>
      </main>

      {/* Floating Create Button */}
      <button
        onClick={() => navigate('/create/input')}
        className="fixed right-8 bottom-8 w-16 h-16 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] rounded-full flex items-center justify-center shadow-lg shadow-[#6366F1]/50 hover:shadow-xl hover:shadow-[#6366F1]/60 hover:scale-110 transition-all group"
      >
        <Play className="w-8 h-8 text-white group-hover:rotate-90 transition-transform" />
      </button>
    </div>
  );
}
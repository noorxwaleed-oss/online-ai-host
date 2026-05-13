import { Header } from '../components/header';
import { Footer } from '../components/footer';
import { GlassCard } from '../components/glass-card';
import { BackgroundEffects } from '../components/background-effects';
import { Play, Clock, FileAudio, Search, Filter } from 'lucide-react';

export function MyLibraryPage() {
  const podcasts = [
    {
      id: 1,
      title: 'Introduction to AI Agents',
      duration: '24:35',
      createdAt: '2 days ago',
      status: 'Published',
      thumbnail: '🎙️',
    },
    {
      id: 2,
      title: 'The Future of Voice Technology',
      duration: '18:42',
      createdAt: '5 days ago',
      status: 'Published',
      thumbnail: '🎧',
    },
    {
      id: 3,
      title: 'Machine Learning Basics',
      duration: '32:15',
      createdAt: '1 week ago',
      status: 'Draft',
      thumbnail: '🤖',
    },
    {
      id: 4,
      title: 'Content Creation with AI',
      duration: '27:08',
      createdAt: '2 weeks ago',
      status: 'Published',
      thumbnail: '✨',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <BackgroundEffects />
      <Header />
      
      <main className="flex-1 max-w-7xl mx-auto px-6 py-12 w-full">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">My Library</h1>
          <p className="text-gray-400">All your created podcasts in one place</p>
        </div>

        {/* Search and Filter Bar */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search your podcasts..."
              className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-[#6366F1]"
            />
          </div>
          <button className="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-colors">
            <Filter className="w-5 h-5" />
            Filter
          </button>
        </div>

        {/* Podcasts Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {podcasts.map((podcast) => (
            <GlassCard key={podcast.id} className="p-6 hover:bg-white/5 transition-all cursor-pointer">
              <div className="flex items-start justify-between mb-4">
                <div className="text-4xl mb-2">{podcast.thumbnail}</div>
                <span className={`px-3 py-1 rounded-full text-xs ${
                  podcast.status === 'Published' 
                    ? 'bg-[#10B981]/20 text-[#10B981]' 
                    : 'bg-[#F59E0B]/20 text-[#F59E0B]'
                }`}>
                  {podcast.status}
                </span>
              </div>

              <h3 className="text-lg font-semibold mb-2">{podcast.title}</h3>
              
              <div className="flex items-center gap-4 text-sm text-gray-400 mb-4">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {podcast.duration}
                </div>
                <div className="flex items-center gap-1">
                  <FileAudio className="w-4 h-4" />
                  {podcast.createdAt}
                </div>
              </div>

              <button className="w-full py-2 px-4 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity flex items-center justify-center gap-2">
                <Play className="w-4 h-4" />
                Play
              </button>
            </GlassCard>
          ))}
        </div>

        {/* Empty State */}
        {podcasts.length === 0 && (
          <GlassCard className="p-12 text-center">
            <div className="text-6xl mb-4">🎙️</div>
            <h3 className="text-2xl font-semibold mb-2">No podcasts yet</h3>
            <p className="text-gray-400 mb-6">Start creating your first podcast to see it here</p>
            <button className="px-8 py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity">
              Create New Podcast
            </button>
          </GlassCard>
        )}
      </main>

      <Footer />
    </div>
  );
}
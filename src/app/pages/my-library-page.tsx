import { useEffect, useMemo, useRef, useState } from 'react';
import { Header } from '../components/header';
import { Footer } from '../components/footer';
import { GlassCard } from '../components/glass-card';
import { BackgroundEffects } from '../components/background-effects';
import { Play, Clock, FileAudio, Search, Filter, X, Check } from 'lucide-react';

type Status = 'All' | 'Published' | 'Draft';
type SortKey = 'recent' | 'oldest' | 'title' | 'duration';

interface Podcast {
  id: number;
  title: string;
  duration: string;
  durationSeconds: number;
  createdAt: string;
  createdAtTs: number; // for sorting
  status: 'Published' | 'Draft';
  thumbnail: string;
}

const SORT_OPTIONS: { value: SortKey; label: string }[] = [
  { value: 'recent', label: 'Most recent' },
  { value: 'oldest', label: 'Oldest first' },
  { value: 'title', label: 'Title (A–Z)' },
  { value: 'duration', label: 'Longest first' },
];

const STATUS_OPTIONS: Status[] = ['All', 'Published', 'Draft'];

export function MyLibraryPage() {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<Status>('All');
  const [sort, setSort] = useState<SortKey>('recent');
  const [filterOpen, setFilterOpen] = useState(false);
  const filterRef = useRef<HTMLDivElement>(null);

  const podcasts: Podcast[] = [
    {
      id: 1,
      title: 'Introduction to AI Agents',
      duration: '24:35',
      durationSeconds: 24 * 60 + 35,
      createdAt: '2 days ago',
      createdAtTs: Date.now() - 2 * 24 * 60 * 60 * 1000,
      status: 'Published',
      thumbnail: '🎙️',
    },
    {
      id: 2,
      title: 'The Future of Voice Technology',
      duration: '18:42',
      durationSeconds: 18 * 60 + 42,
      createdAt: '5 days ago',
      createdAtTs: Date.now() - 5 * 24 * 60 * 60 * 1000,
      status: 'Published',
      thumbnail: '🎧',
    },
    {
      id: 3,
      title: 'Machine Learning Basics',
      duration: '32:15',
      durationSeconds: 32 * 60 + 15,
      createdAt: '1 week ago',
      createdAtTs: Date.now() - 7 * 24 * 60 * 60 * 1000,
      status: 'Draft',
      thumbnail: '🤖',
    },
    {
      id: 4,
      title: 'Content Creation with AI',
      duration: '27:08',
      durationSeconds: 27 * 60 + 8,
      createdAt: '2 weeks ago',
      createdAtTs: Date.now() - 14 * 24 * 60 * 60 * 1000,
      status: 'Published',
      thumbnail: '✨',
    },
  ];

  // Close the popover on outside click / escape
  useEffect(() => {
    if (!filterOpen) return;
    const onClick = (e: MouseEvent) => {
      if (filterRef.current && !filterRef.current.contains(e.target as Node)) {
        setFilterOpen(false);
      }
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setFilterOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onClick);
      document.removeEventListener('keydown', onKey);
    };
  }, [filterOpen]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = podcasts.filter((p) => {
      if (status !== 'All' && p.status !== status) return false;
      if (q && !p.title.toLowerCase().includes(q)) return false;
      return true;
    });

    switch (sort) {
      case 'oldest':
        return [...list].sort((a, b) => a.createdAtTs - b.createdAtTs);
      case 'title':
        return [...list].sort((a, b) => a.title.localeCompare(b.title));
      case 'duration':
        return [...list].sort((a, b) => b.durationSeconds - a.durationSeconds);
      case 'recent':
      default:
        return [...list].sort((a, b) => b.createdAtTs - a.createdAtTs);
    }
    // podcasts is stable per render — safe to omit
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, status, sort]);

  const activeFilterCount = (status !== 'All' ? 1 : 0) + (sort !== 'recent' ? 1 : 0);
  const hasActiveFilters = activeFilterCount > 0 || query.length > 0;

  const handleReset = () => {
    setStatus('All');
    setSort('recent');
    setQuery('');
    setFilterOpen(false);
  };

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
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search your podcasts..."
              className="w-full pl-10 pr-10 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-[#6366F1]"
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                aria-label="Clear search"
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Filter dropdown */}
          <div className="relative" ref={filterRef}>
            <button
              onClick={() => setFilterOpen((v) => !v)}
              aria-expanded={filterOpen}
              aria-haspopup="true"
              className={`flex items-center gap-2 px-6 py-3 border rounded-lg text-white transition-colors ${
                filterOpen || activeFilterCount > 0
                  ? 'bg-[#6366F1]/20 border-[#6366F1]/50'
                  : 'bg-white/5 border-white/10 hover:bg-white/10'
              }`}
            >
              <Filter className="w-5 h-5" />
              Filter
              {activeFilterCount > 0 && (
                <span className="ml-1 inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 bg-[#6366F1] text-white text-xs font-medium rounded-full">
                  {activeFilterCount}
                </span>
              )}
            </button>

            {filterOpen && (
              <div className="absolute right-0 mt-2 w-72 z-20 bg-[#0f0f17] border border-white/10 rounded-lg shadow-xl p-4 backdrop-blur-md">
                <div className="mb-4">
                  <p className="text-xs uppercase tracking-wide text-gray-400 mb-2">Status</p>
                  <div className="grid grid-cols-3 gap-2">
                    {STATUS_OPTIONS.map((s) => {
                      const selected = status === s;
                      return (
                        <button
                          key={s}
                          onClick={() => setStatus(s)}
                          className={`py-2 rounded-lg text-sm border transition-colors ${
                            selected
                              ? 'border-[#6366F1] bg-[#6366F1]/20 text-white'
                              : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
                          }`}
                        >
                          {s}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-xs uppercase tracking-wide text-gray-400 mb-2">Sort by</p>
                  <div className="space-y-1">
                    {SORT_OPTIONS.map((opt) => {
                      const selected = sort === opt.value;
                      return (
                        <button
                          key={opt.value}
                          onClick={() => setSort(opt.value)}
                          className={`flex items-center justify-between w-full px-3 py-2 rounded-lg text-sm transition-colors ${
                            selected
                              ? 'bg-[#6366F1]/20 text-white'
                              : 'text-gray-300 hover:bg-white/5'
                          }`}
                        >
                          <span>{opt.label}</span>
                          {selected && <Check className="w-4 h-4 text-[#6366F1]" />}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="flex items-center justify-between gap-2 pt-3 border-t border-white/10">
                  <button
                    onClick={handleReset}
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    Reset
                  </button>
                  <button
                    onClick={() => setFilterOpen(false)}
                    className="px-4 py-1.5 text-sm bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity"
                  >
                    Done
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Result summary */}
        <div className="flex items-center justify-between mb-6 text-sm text-gray-400">
          <span>
            Showing <span className="text-white">{filtered.length}</span> of {podcasts.length}{' '}
            podcast{podcasts.length === 1 ? '' : 's'}
          </span>
          {hasActiveFilters && (
            <button
              onClick={handleReset}
              className="text-[#6366F1] hover:text-[#8B5CF6] transition-colors"
            >
              Clear filters
            </button>
          )}
        </div>

        {/* Podcasts Grid */}
        {filtered.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((podcast) => (
              <GlassCard
                key={podcast.id}
                className="p-6 hover:bg-white/5 transition-all cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="text-4xl mb-2">{podcast.thumbnail}</div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs ${
                      podcast.status === 'Published'
                        ? 'bg-[#10B981]/20 text-[#10B981]'
                        : 'bg-[#F59E0B]/20 text-[#F59E0B]'
                    }`}
                  >
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
        ) : (
          <GlassCard className="p-12 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-2xl font-semibold mb-2">No podcasts match your filters</h3>
            <p className="text-gray-400 mb-6">Try changing the status or clearing your search.</p>
            <button
              onClick={handleReset}
              className="px-8 py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity"
            >
              Clear filters
            </button>
          </GlassCard>
        )}
      </main>

      <Footer />
    </div>
  );
}

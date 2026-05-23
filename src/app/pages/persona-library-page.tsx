import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Header } from '../components/header';
import { GlassCard } from '../components/glass-card';
import { BackgroundEffects } from '../components/background-effects';
import { Search, Plus, Edit, Trash2, User } from 'lucide-react';

interface Persona {
  id: number;
  name: string;
  type: 'host' | 'guest';
  voiceStyle: string;
  status: 'draft' | 'generated' | 'published';
}

export function PersonaLibraryPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<'all' | 'draft' | 'generated' | 'published'>('all');
  const [sortBy, setSortBy] = useState('newest');

  const personas: Persona[] = [
    { id: 1, name: 'Alex Rivera', type: 'host', voiceStyle: 'Professional', status: 'published' },
    { id: 2, name: 'Sarah Chen', type: 'guest', voiceStyle: 'Energetic', status: 'published' },
    { id: 3, name: 'Dr. James Watson', type: 'guest', voiceStyle: 'Authoritative', status: 'generated' },
    { id: 4, name: 'Emma Thompson', type: 'host', voiceStyle: 'Warm', status: 'generated' },
  ];

  const filters = [
    { id: 'all', label: 'all', count: 4 },
    { id: 'draft', label: 'draft', count: 0 },
    { id: 'generated', label: 'generated', count: 2 },
    { id: 'published', label: 'published', count: 2 },
  ];

  const filteredPersonas = personas.filter((persona) => {
    const matchesSearch = persona.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = activeFilter === 'all' || persona.status === activeFilter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="min-h-screen flex flex-col">
      <BackgroundEffects />
      <Header />
      
      <main className="flex-1 max-w-7xl mx-auto px-6 py-8 w-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-semibold mb-2">Persona Library</h1>
            <p className="text-gray-400">Manage your voice personas and settings</p>
          </div>
          <button
            onClick={() => navigate('/create/personas')}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            <Plus className="w-5 h-5" />
            New Persona
          </button>
        </div>

        {/* Search and Filters */}
        <div className="mb-6">
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search personas..."
                className="w-full bg-white/5 border border-white/10 rounded-lg pl-12 pr-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
              />
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-white/5 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-[#6366F1] transition-colors"
            >
              <option value="newest">Sort by: Newest</option>
              <option value="oldest">Sort by: Oldest</option>
              <option value="name">Sort by: Name</option>
            </select>
          </div>

          {/* Filter Chips */}
          <div className="flex items-center gap-2">
            {filters.map((filter) => (
              <button
                key={filter.id}
                onClick={() => setActiveFilter(filter.id as any)}
                className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                  activeFilter === filter.id
                    ? 'bg-[#6366F1] text-white'
                    : 'bg-white/5 border border-white/10 text-gray-400 hover:text-white'
                }`}
              >
                {filter.label} ({filter.count})
              </button>
            ))}
          </div>
        </div>

        {/* Personas Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPersonas.map((persona) => (
            <GlassCard key={persona.id} className="p-6 hover:border-white/20 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-full flex items-center justify-center">
                    <User className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{persona.name}</h3>
                    <p className="text-sm text-gray-400 capitalize">{persona.type}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-1">
                  <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                    <Edit className="w-4 h-4 text-gray-400 hover:text-white" />
                  </button>
                  <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                    <Trash2 className="w-4 h-4 text-gray-400 hover:text-red-400" />
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Voice Style</span>
                  <span className="text-white">{persona.voiceStyle}</span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Status</span>
                  <span
                    className={`px-2 py-1 rounded text-xs capitalize ${
                      persona.status === 'published'
                        ? 'bg-[#10B981]/20 text-[#10B981]'
                        : persona.status === 'generated'
                        ? 'bg-[#6366F1]/20 text-[#6366F1]'
                        : 'bg-gray-500/20 text-gray-400'
                    }`}
                  >
                    {persona.status}
                  </span>
                </div>
              </div>

              <button className="w-full mt-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-sm">
                Use in Episode
              </button>
            </GlassCard>
          ))}
        </div>

        {/* Empty State */}
        {filteredPersonas.length === 0 && (
          <div className="text-center py-12">
            <User className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No personas found</h3>
            <p className="text-gray-400 mb-6">
              {searchQuery
                ? 'Try adjusting your search or filters'
                : 'Create your first persona to get started'}
            </p>
            <button
              onClick={() => navigate('/create/personas')}
              className="px-6 py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity"
            >
              Create Persona
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
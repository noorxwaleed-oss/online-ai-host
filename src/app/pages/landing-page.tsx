import { useNavigate } from "react-router";
import { Header } from "../components/header";
import { Footer } from "../components/footer";
import { GlassCard } from "../components/glass-card";
import { BackgroundEffects } from "../components/background-effects";
import { Sparkles, Mic, FileAudio, Video } from "lucide-react";

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      <BackgroundEffects />
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-6 py-20 text-center">
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-white via-[#6366F1] to-[#8B5CF6] bg-clip-text text-transparent">
            Create Professional Podcasts
            <br />
            in Minutes, Not Hours
          </h1>

          <p className="text-xl text-gray-400 mb-10 max-w-3xl mx-auto">
            Transform your ideas into engaging podcast episodes
            with AI-powered script writing, voice generation,
            and automated production. No recording equipment
            needed.
          </p>

          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => navigate("/login")}
              className="px-8 py-4 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity text-lg"
            >
              Get Started Free
            </button>
          </div>
        </section>

        {/* Features Section */}
        <section className="max-w-7xl mx-auto px-6 py-20">
          <h2 className="text-3xl font-bold text-center mb-12">
            Powered by Advanced AI Agents
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard className="p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-lg flex items-center justify-center mb-4">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">
                Content Agent
              </h3>
              <p className="text-gray-400 text-sm">
                Analyzes your input from URLs, PDFs, or text to
                extract key insights and topics
              </p>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-[#8B5CF6] to-[#EC4899] rounded-lg flex items-center justify-center mb-4">
                <Mic className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">
                Script Agent
              </h3>
              <p className="text-gray-400 text-sm">
                Writes engaging dialogue between host and guest
                with natural conversation flow
              </p>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-[#10B981] to-[#06B6D4] rounded-lg flex items-center justify-center mb-4">
                <FileAudio className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">
                Audio Agent
              </h3>
              <p className="text-gray-400 text-sm">
                Generates realistic voices with customizable
                personas and speaking styles
              </p>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-[#F59E0B] to-[#EF4444] rounded-lg flex items-center justify-center mb-4">
                <Video className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">
                Video Agent
              </h3>
              <p className="text-gray-400 text-sm">
                Renders engaging video content with custom cover
                art for social media
              </p>
            </GlassCard>
          </div>
        </section>

        {/* CTA Section */}
        <section className="max-w-7xl mx-auto px-6 py-20">
          <GlassCard className="p-12 text-center">
            <h2 className="text-4xl font-bold mb-4">
              Ready to Create Your First Podcast?
            </h2>
            <p className="text-xl text-gray-400 mb-8">
              Join thousands of creators who are already using
              AI to produce amazing content
            </p>
            <button
              onClick={() => navigate("/signup")}
              className="px-8 py-4 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity text-lg"
            >
              Start Creating Now
            </button>
          </GlassCard>
        </section>
      </main>

      <Footer />
    </div>
  );
}
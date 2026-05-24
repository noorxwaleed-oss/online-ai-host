import { ReactNode } from 'react';
import { useNavigate } from 'react-router';
import { Header } from './header';
import { GlassCard } from './glass-card';
import { BackgroundEffects } from './background-effects';
import { ArrowLeft, ArrowRight, CheckCircle2, Circle, LucideIcon } from 'lucide-react';

interface Agent {
  name: string;
  status: 'completed' | 'active' | 'waiting';
  message: string;
  icon?: LucideIcon;
}

interface CreateLayoutProps {
  children: ReactNode;
  currentStep: number;
  agents: Agent[];
  onPrevious?: () => void;
  onNext?: () => void;
  previousLabel?: string;
  nextLabel?: string;
}

const steps = [
  { number: 1, label: 'Input' },
  { number: 2, label: 'Personas' },
  { number: 3, label: 'Script' },
  { number: 4, label: 'Audio' },
  { number: 5, label: 'Cover Art' },
  { number: 6, label: 'Publish' },
];

export function CreateLayout({
  children,
  currentStep,
  agents,
  onPrevious,
  onNext,
  previousLabel = 'Dashboard',
  nextLabel = 'Next',
}: CreateLayoutProps) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      <BackgroundEffects />
      <Header />
      
      <main className="flex-1 max-w-7xl mx-auto px-6 py-8 w-full">
        {/* Step Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center">
                <div className="flex flex-col items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all ${
                      step.number === currentStep
                        ? 'border-[#6366F1] bg-[#6366F1] text-white'
                        : step.number < currentStep
                        ? 'border-[#10B981] bg-[#10B981] text-white'
                        : 'border-white/20 bg-white/5 text-gray-400'
                    }`}
                  >
                    {step.number < currentStep ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : (
                      <span className="text-sm">{step.number}</span>
                    )}
                  </div>
                  <span className={`text-xs mt-1 ${step.number === currentStep ? 'text-white' : 'text-gray-400'}`}>
                    {step.label}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`w-12 h-0.5 mb-6 mx-1 ${
                      step.number < currentStep ? 'bg-[#10B981]' : 'bg-white/10'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid lg:grid-cols-[1fr_300px] gap-6">
          {/* Main Content */}
          <div>{children}</div>

          {/* Agent Sidebar */}
          <div>
            <GlassCard className="p-6 sticky top-24">
              <h3 className="text-lg font-semibold mb-4">CrewAI Agents</h3>
              <div className="space-y-3">
                {agents.map((agent, index) => {
                  const Icon = agent.icon || Circle;
                  return (
                    <div
                      key={index}
                      className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
                        agent.status === 'active' ? 'bg-[#6366F1]/10 border border-[#6366F1]/20' : 'bg-white/5'
                      }`}
                    >
                      <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
                        agent.status === 'completed'
                          ? 'bg-[#10B981]/20'
                          : agent.status === 'active'
                          ? 'bg-[#6366F1]'
                          : 'bg-white/10'
                      }`}>
                        <Icon
                          className={`w-5 h-5 ${
                            agent.status === 'completed'
                              ? 'text-[#10B981]'
                              : agent.status === 'active'
                              ? 'text-white'
                              : 'text-[#6B7280]'
                          }`}
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium mb-1">{agent.name}</p>
                        <p className={`text-xs ${
                          agent.status === 'completed'
                            ? 'text-[#10B981]'
                            : agent.status === 'active'
                            ? 'text-[#6366F1]'
                            : 'text-gray-400'
                        }`}>
                          {agent.message}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </GlassCard>
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8">
          {/* Navigation Buttons */}
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={onPrevious || (() => navigate('/dashboard'))}
              className="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              {previousLabel}
            </button>
            
            {onNext && (
              <button
                onClick={onNext}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity"
              >
                {nextLabel}
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Step Progress Dots */}
          <div className="flex flex-col items-center gap-3">
            <p className="text-center text-sm text-gray-400">Step {currentStep} of 6</p>
            <div className="flex items-center justify-center gap-2">
              {steps.map((step) => (
                <div
                  key={step.number}
                  className={`h-2 rounded-full transition-all ${
                    step.number === currentStep
                      ? 'w-8 bg-[#8B5CF6]'
                      : step.number < currentStep
                      ? 'w-2 bg-[#10B981]'
                      : 'w-2 bg-white/20'
                  }`}
                  title={step.label}
                />
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
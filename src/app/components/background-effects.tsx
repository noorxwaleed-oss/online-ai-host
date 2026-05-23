export function BackgroundEffects() {
  return (
    <>
      {/* Animated gradient orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        {/* Primary Purple gradient orb - top left */}
        <div 
          className="absolute -top-1/4 left-1/4 w-[500px] h-[500px] bg-[#8B5CF6] rounded-full mix-blend-normal filter blur-3xl opacity-20 animate-pulse"
          style={{ animationDuration: '8s' }}
        />
        
        {/* Fuchsia gradient orb - top right */}
        <div 
          className="absolute -top-1/3 right-1/4 w-[450px] h-[450px] bg-[#EC4899] rounded-full mix-blend-normal filter blur-3xl opacity-15 animate-pulse"
          style={{ animationDuration: '10s', animationDelay: '1s' }}
        />
        
        {/* Purple gradient orb - left middle */}
        <div 
          className="absolute top-1/2 -left-1/4 w-[550px] h-[550px] bg-[#8B5CF6] rounded-full mix-blend-normal filter blur-3xl opacity-18 animate-pulse"
          style={{ animationDuration: '12s', animationDelay: '2s' }}
        />
        
        {/* Indigo gradient orb - center */}
        <div 
          className="absolute top-1/4 left-1/2 w-[400px] h-[400px] bg-[#6366F1] rounded-full mix-blend-normal filter blur-3xl opacity-12 animate-pulse"
          style={{ animationDuration: '14s', animationDelay: '3s' }}
        />
        
        {/* Fuchsia gradient orb - right middle */}
        <div 
          className="absolute top-1/3 -right-1/4 w-[480px] h-[480px] bg-[#EC4899] rounded-full mix-blend-normal filter blur-3xl opacity-16 animate-pulse"
          style={{ animationDuration: '11s', animationDelay: '4s' }}
        />
        
        {/* Purple gradient orb - bottom left */}
        <div 
          className="absolute -bottom-1/4 left-1/3 w-[520px] h-[520px] bg-[#8B5CF6] rounded-full mix-blend-normal filter blur-3xl opacity-17 animate-pulse"
          style={{ animationDuration: '13s', animationDelay: '5s' }}
        />
        
        {/* Fuchsia gradient orb - bottom right */}
        <div 
          className="absolute -bottom-1/4 right-1/4 w-[460px] h-[460px] bg-[#EC4899] rounded-full mix-blend-normal filter blur-3xl opacity-14 animate-pulse"
          style={{ animationDuration: '9s', animationDelay: '6s' }}
        />
        
        {/* Small accent purple orb - top center */}
        <div 
          className="absolute top-0 left-1/2 w-[350px] h-[350px] bg-[#A78BFA] rounded-full mix-blend-normal filter blur-3xl opacity-10 animate-pulse"
          style={{ animationDuration: '15s', animationDelay: '2.5s' }}
        />
        
        {/* Small accent fuchsia orb - bottom center */}
        <div 
          className="absolute bottom-0 left-1/3 w-[380px] h-[380px] bg-[#F472B6] rounded-full mix-blend-normal filter blur-3xl opacity-12 animate-pulse"
          style={{ animationDuration: '10s', animationDelay: '4.5s' }}
        />
      </div>

      {/* Subtle grid overlay */}
      <div 
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(139, 92, 246, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(139, 92, 246, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />
    </>
  );
}
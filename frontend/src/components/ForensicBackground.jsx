import { useEffect, useRef } from 'react';

export default function ForensicBackground() {
  const bgRef = useRef(null);

  useEffect(() => {
    // Only add mouse tracker if not reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    const handleMouseMove = (e) => {
      if (bgRef.current) {
        // Absolute position for the cursor orb
        bgRef.current.style.setProperty('--mouse-x', `${e.clientX}px`);
        bgRef.current.style.setProperty('--mouse-y', `${e.clientY}px`);
        
        // Normalized position (-1 to 1) for parallax shifting
        const xNorm = (e.clientX / window.innerWidth) * 2 - 1;
        const yNorm = (e.clientY / window.innerHeight) * 2 - 1;
        bgRef.current.style.setProperty('--mouse-x-norm', xNorm);
        bgRef.current.style.setProperty('--mouse-y-norm', yNorm);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div ref={bgRef} className="forensic-bg fixed inset-0 z-0 pointer-events-none overflow-hidden bg-[#09090b]">
      {/* Deep space base tint */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-zinc-900/60 via-[#09090b] to-[#09090b]"></div>

      {/* Faint galaxy haze */}
      <div className="nebula-haze nebula-1"></div>
      <div className="nebula-haze nebula-2"></div>

      {/* Slow parallax star drift & Static stars with mouse interaction */}
      <div className="star-layer star-layer-static parallax-1"></div>
      <div className="star-layer star-layer-1 parallax-2"></div>
      <div className="star-layer star-layer-2 parallax-3"></div>
      <div className="star-layer star-layer-3 parallax-4"></div>

      {/* Forensic scan grid & radar sweep */}
      <div className="grid-bg opacity-50"></div>
      <div className="scanline-layer"></div>

      {/* Cursor spotlight */}
      <div className="cursor-orb hidden md:block"></div>
    </div>
  );
}
